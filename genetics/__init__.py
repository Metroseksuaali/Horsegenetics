"""
Horse Genetics Module

This module provides comprehensive horse coat color genetics simulation
with support for thousands of genetic combinations across 17 genes.

Main components:
- horse: Main Horse class with fluent API
- gene_registry: Dynamic gene management (17 genes)
- gene_interaction: Phenotype calculation pipeline
- breeding_stats: Breeding probability calculations

Legacy components (9 genes only, kept for backwards compatibility):
- core: Gene pools and allele definitions
- phenotype: Legacy phenotype determination
- breeding: Legacy breeding simulation
"""

# New API (17 genes) - preferred
from genetics.horse import Horse
from genetics.gene_registry import GeneRegistry, get_default_registry
from genetics.gene_interaction import PhenotypeCalculator

# Legacy API (9 genes only) - kept for backwards compatibility
from genetics.core import GenePool
from genetics.breeding import BreedingSimulator
from genetics.phenotype import PhenotypeCalculator as LegacyPhenotypeCalculator

__all__ = [
    # New API
    'Horse',
    'GeneRegistry',
    'get_default_registry',
    'PhenotypeCalculator',
    # Legacy
    'GenePool',
    'BreedingSimulator',
    'LegacyPhenotypeCalculator',
]
__version__ = '2.0.0'
