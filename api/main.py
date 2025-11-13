#!/usr/bin/env python3
"""
Horse Genetics REST API - FastAPI implementation

Provides HTTP endpoints for web/mobile game integration.

To run:
    pip install fastapi uvicorn
    python3 api/main.py

Or with uvicorn directly:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

API Documentation:
    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    print("Error: FastAPI not installed. Install with: pip install fastapi uvicorn")
    sys.exit(1)

from genetics.horse import Horse
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator
from genetics.breeding_stats import (
    calculate_offspring_probabilities,
    calculate_single_gene_probability,
    get_guaranteed_traits
)

# Initialize FastAPI app
app = FastAPI(
    title="Horse Genetics Simulator API",
    description="Scientifically accurate horse coat color genetics simulator for game integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web game integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your game's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize genetics components
registry = get_default_registry()
calculator = PhenotypeCalculator(registry)


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class HorseResponse(BaseModel):
    """Horse data response model."""
    phenotype: str = Field(..., description="Coat color phenotype name")
    genotype_string: str = Field(..., description="Compact genotype string")
    genotype: Dict[str, List[str]] = Field(..., description="Full genotype dictionary")

    class Config:
        schema_extra = {
            "example": {
                "phenotype": "Buckskin",
                "genotype_string": "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g",
                "genotype": {
                    "extension": ["E", "e"],
                    "agouti": ["A", "a"],
                    "dilution": ["N", "Cr"],
                    "dun": ["nd2", "nd2"],
                    "silver": ["n", "n"],
                    "champagne": ["n", "n"],
                    "flaxen": ["F", "f"],
                    "sooty": ["sty", "sty"],
                    "gray": ["g", "g"]
                }
            }
        }


class BreedRequest(BaseModel):
    """Request model for breeding two horses."""
    parent1: str = Field(..., description="Parent 1 genotype string")
    parent2: str = Field(..., description="Parent 2 genotype string")

    class Config:
        schema_extra = {
            "example": {
                "parent1": "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g",
                "parent2": "E:e/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"
            }
        }


class BreedResponse(BaseModel):
    """Response model for breeding."""
    offspring: HorseResponse = Field(..., description="Offspring horse data")


class ProbabilityRequest(BaseModel):
    """Request model for probability calculation."""
    parent1: str = Field(..., description="Parent 1 genotype string")
    parent2: str = Field(..., description="Parent 2 genotype string")
    sample_size: Optional[int] = Field(None, description="Sample size for Monte Carlo (optional)")

    class Config:
        schema_extra = {
            "example": {
                "parent1": "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g",
                "parent2": "E:e/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g",
                "sample_size": None
            }
        }


class ProbabilityResponse(BaseModel):
    """Response model for probability calculation."""
    probabilities: Dict[str, float] = Field(..., description="Phenotype probabilities")
    method: str = Field(..., description="Calculation method used (exact or monte_carlo)")

    class Config:
        schema_extra = {
            "example": {
                "probabilities": {
                    "Buckskin": 0.25,
                    "Bay": 0.25,
                    "Palomino": 0.125,
                    "Chestnut": 0.125
                },
                "method": "exact"
            }
        }


class GenotypeRequest(BaseModel):
    """Request model for phenotype lookup."""
    genotype_string: str = Field(..., description="Genotype string to analyze")

    class Config:
        schema_extra = {
            "example": {
                "genotype_string": "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"
            }
        }


class BatchGenerateRequest(BaseModel):
    """Request model for batch horse generation."""
    count: int = Field(..., ge=1, le=1000, description="Number of horses to generate (1-1000)")

    class Config:
        schema_extra = {
            "example": {
                "count": 10
            }
        }


class BatchGenerateResponse(BaseModel):
    """Response model for batch generation."""
    horses: List[HorseResponse] = Field(..., description="Generated horses")
    count: int = Field(..., description="Number of horses generated")


# ============================================================================
# Helper Functions
# ============================================================================

def horse_to_response(horse: Horse) -> HorseResponse:
    """Convert Horse object to API response model."""
    return HorseResponse(
        phenotype=horse.phenotype,
        genotype_string=horse.genotype_string,
        genotype={
            gene_name: list(alleles)
            for gene_name, alleles in horse.genotype.items()
        }
    )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """API root endpoint with welcome message."""
    return {
        "message": "Horse Genetics Simulator API",
        "version": "2.0.0",
        "documentation": "/docs",
        "endpoints": {
            "POST /api/random": "Generate random horse",
            "POST /api/breed": "Breed two horses",
            "POST /api/probabilities": "Calculate breeding probabilities",
            "POST /api/phenotype": "Get phenotype from genotype",
            "POST /api/batch": "Generate multiple random horses",
            "GET /api/genes": "List all genes",
            "GET /api/health": "Health check"
        }
    }


@app.get("/api/health", tags=["General"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "genes_loaded": len(registry.get_all_gene_names())
    }


@app.get("/api/genes", tags=["Information"])
async def list_genes():
    """List all available genes and their alleles."""
    genes_info = []

    for gene_name in registry.get_all_gene_names():
        gene_def = registry.get_gene(gene_name)
        genes_info.append({
            "name": gene_def.name,
            "symbol": gene_def.symbol,
            "full_name": gene_def.full_name,
            "locus": gene_def.locus,
            "alleles": gene_def.alleles,
            "inheritance": gene_def.inheritance_pattern.value,
            "description": gene_def.description
        })

    return {"genes": genes_info, "count": len(genes_info)}


@app.post("/api/random", response_model=HorseResponse, tags=["Horse Generation"])
async def generate_random_horse():
    """
    Generate a random horse with random genetics.

    Returns a horse with randomly selected alleles for all genes.
    Perfect for spawning new horses in your game!
    """
    try:
        horse = Horse.random(registry, calculator)
        return horse_to_response(horse)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating horse: {str(e)}")


@app.post("/api/batch", response_model=BatchGenerateResponse, tags=["Horse Generation"])
async def generate_batch_horses(request: BatchGenerateRequest):
    """
    Generate multiple random horses at once.

    Useful for creating initial populations or large stables.
    Limited to 1000 horses per request.
    """
    try:
        horses = [Horse.random(registry, calculator) for _ in range(request.count)]
        return BatchGenerateResponse(
            horses=[horse_to_response(h) for h in horses],
            count=len(horses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating horses: {str(e)}")


@app.post("/api/breed", response_model=BreedResponse, tags=["Breeding"])
async def breed_horses(request: BreedRequest):
    """
    Breed two horses and return the offspring.

    Follows Mendelian inheritance - each parent contributes one random
    allele from each gene to the offspring.
    """
    try:
        # Parse parent genotypes
        parent1_genotype = registry.parse_genotype_string(request.parent1)
        parent2_genotype = registry.parse_genotype_string(request.parent2)

        # Create Horse objects
        parent1 = Horse(parent1_genotype, registry, calculator)
        parent2 = Horse(parent2_genotype, registry, calculator)

        # Breed
        offspring = Horse.breed(parent1, parent2, registry, calculator)

        return BreedResponse(offspring=horse_to_response(offspring))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid genotype: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error breeding horses: {str(e)}")


@app.post("/api/probabilities", response_model=ProbabilityResponse, tags=["Breeding"])
async def calculate_probabilities(request: ProbabilityRequest):
    """
    Calculate probability distribution of offspring phenotypes.

    This shows you the chances of getting each possible coat color
    from a specific breeding pair before you actually breed them!

    Use sample_size for Monte Carlo approximation (faster for large calculations).
    Leave sample_size as null for exact calculation.
    """
    try:
        probabilities = calculate_offspring_probabilities(
            request.parent1,
            request.parent2,
            sample_size=request.sample_size
        )

        method = "monte_carlo" if request.sample_size else "exact"

        return ProbabilityResponse(
            probabilities=probabilities,
            method=method
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid genotype: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating probabilities: {str(e)}")


@app.post("/api/phenotype", response_model=HorseResponse, tags=["Information"])
async def get_phenotype(request: GenotypeRequest):
    """
    Get phenotype (coat color) from a genotype string.

    Useful for looking up what a specific genotype produces without
    actually breeding horses.
    """
    try:
        horse = Horse.from_string(request.genotype_string, registry, calculator)
        return horse_to_response(horse)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid genotype: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error determining phenotype: {str(e)}")


@app.post("/api/validate", tags=["Information"])
async def validate_genotype(request: GenotypeRequest):
    """
    Validate a genotype string without creating a horse.

    Returns validation status and any error messages.
    """
    from genetics.validation import quick_validate

    is_valid, message = quick_validate(request.genotype_string)

    return {
        "valid": is_valid,
        "message": message,
        "genotype": request.genotype_string
    }


@app.post("/api/guaranteed-traits", tags=["Breeding"])
async def get_guaranteed(request: BreedRequest):
    """
    Find traits guaranteed to appear in all offspring.

    For example, if both parents are e/e (chestnut), all offspring
    will definitely be e/e.
    """
    try:
        parent1_genotype = registry.parse_genotype_string(request.parent1)
        parent2_genotype = registry.parse_genotype_string(request.parent2)

        guaranteed = get_guaranteed_traits(parent1_genotype, parent2_genotype, registry)

        return {
            "guaranteed_traits": guaranteed,
            "count": len(guaranteed)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid genotype: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating guaranteed traits: {str(e)}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        import uvicorn
        print("=" * 60)
        print("Horse Genetics Simulator API")
        print("=" * 60)
        print("\nStarting server...")
        print("API Documentation: http://localhost:8000/docs")
        print("Alternative docs: http://localhost:8000/redoc")
        print("\nPress Ctrl+C to stop")
        print("=" * 60)

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("\nError: uvicorn not installed")
        print("Install with: pip install uvicorn")
        print("\nOr run with: uvicorn api.main:app --reload")
        sys.exit(1)
