"""
Horse API module - High-level fluent interface for horse genetics

This module provides a clean, intuitive API for working with horse genetics.
Perfect for game projects and other applications that need simple horse generation.

Example usage:
    # Generate random horse
    horse = Horse.random()
    print(horse.phenotype)
    print(horse.genotype_string)

    # Breed two horses
    mare = Horse.random()
    stallion = Horse.random()
    foal = Horse.breed(mare, stallion)

    # Create horse from genotype string
    horse = Horse.from_string("E:E/e A:A/a Dil:N/Cr D:D/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g")
"""

from typing import Dict, Tuple, Optional
from genetics.gene_registry import GeneRegistry, get_default_registry
from genetics.gene_interaction import PhenotypeCalculator


class Horse:
    """
    Represents a horse with complete genetic information.

    Provides a clean, fluent API for horse genetics operations.
    """

    def __init__(
        self,
        genotype: Dict[str, Tuple[str, str]],
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None
    ):
        """
        Create a horse from a genotype.

        Args:
            genotype: Complete genotype dictionary
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)
        """
        self.registry = registry or get_default_registry()
        self.calculator = calculator or PhenotypeCalculator(self.registry)

        # Validate genotype
        self.registry.validate_genotype(genotype)
        self._genotype = genotype

        # Calculate phenotype
        self._phenotype = self.calculator.determine_phenotype(genotype)

    @property
    def genotype(self) -> Dict[str, Tuple[str, str]]:
        """Get complete genotype dictionary."""
        return self._genotype.copy()

    @property
    def phenotype(self) -> str:
        """Get phenotype (coat color) string."""
        return self._phenotype

    @property
    def genotype_string(self) -> str:
        """Get formatted genotype string (compact format)."""
        return self.registry.format_genotype(self._genotype, compact=True)

    @property
    def genotype_detailed(self) -> str:
        """Get formatted genotype string (detailed multi-line format)."""
        return self.registry.format_genotype(self._genotype, compact=False)

    def get_gene(self, gene_name: str) -> Tuple[str, str]:
        """
        Get genotype for a specific gene.

        Args:
            gene_name: Gene name (e.g., 'extension')

        Returns:
            tuple: Allele pair (e.g., ('E', 'e'))
        """
        return self._genotype[gene_name]

    def has_allele(self, gene_name: str, allele: str) -> bool:
        """
        Check if horse has at least one copy of an allele.

        Args:
            gene_name: Gene name
            allele: Allele to check for

        Returns:
            bool: True if allele present
        """
        return self.registry.has_allele(self._genotype[gene_name], allele)

    def is_homozygous(self, gene_name: str) -> bool:
        """
        Check if horse is homozygous for a gene.

        Args:
            gene_name: Gene name

        Returns:
            bool: True if homozygous (both alleles same)
        """
        return self.registry.is_homozygous(self._genotype[gene_name])

    def to_dict(self) -> dict:
        """
        Convert horse to dictionary format.

        Returns:
            dict: Horse data with genotype and phenotype
        """
        return {
            'genotype': self._genotype,
            'phenotype': self._phenotype,
            'genotype_string': self.genotype_string
        }

    def __str__(self) -> str:
        """String representation of horse."""
        return f"{self._phenotype}\n{self.genotype_string}"

    def __repr__(self) -> str:
        """Developer representation of horse."""
        return f"Horse(phenotype='{self._phenotype}')"

    # ========================================================================
    # FACTORY METHODS - Fluent API for creating horses
    # ========================================================================

    @classmethod
    def random(
        cls,
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None
    ) -> 'Horse':
        """
        Generate a random horse.

        Args:
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)

        Returns:
            Horse: New random horse

        Example:
            horse = Horse.random()
            print(horse.phenotype)
        """
        reg = registry or get_default_registry()
        genotype = reg.generate_random_genotype()
        return cls(genotype, reg, calculator)

    @classmethod
    def from_string(
        cls,
        genotype_str: str,
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None
    ) -> 'Horse':
        """
        Create horse from genotype string.

        Args:
            genotype_str: Genotype string (e.g., "E:E/e A:A/a Dil:N/N ...")
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)

        Returns:
            Horse: New horse with specified genotype

        Example:
            horse = Horse.from_string("E:e/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:f/f STY:sty/sty G:g/g")
        """
        reg = registry or get_default_registry()
        genotype = reg.parse_genotype_string(genotype_str)
        return cls(genotype, reg, calculator)

    @classmethod
    def from_dict(
        cls,
        data: dict,
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None
    ) -> 'Horse':
        """
        Create horse from dictionary.

        Args:
            data: Dictionary with 'genotype' key
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)

        Returns:
            Horse: New horse

        Example:
            data = {'genotype': {'extension': ('E', 'e'), ...}}
            horse = Horse.from_dict(data)
        """
        genotype = data['genotype']
        return cls(genotype, registry, calculator)

    @classmethod
    def breed(
        cls,
        parent1: 'Horse',
        parent2: 'Horse',
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None
    ) -> 'Horse':
        """
        Breed two horses to produce offspring.

        Follows Mendelian inheritance - each parent contributes one
        random allele from each gene.

        Args:
            parent1: First parent
            parent2: Second parent
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)

        Returns:
            Horse: Offspring horse

        Example:
            mare = Horse.random()
            stallion = Horse.random()
            foal = Horse.breed(mare, stallion)
        """
        reg = registry or get_default_registry()
        offspring_genotype = reg.breed(parent1._genotype, parent2._genotype)
        return cls(offspring_genotype, reg, calculator)


# ============================================================================
# CONVENIENCE FUNCTIONS - Alternative API style
# ============================================================================

def generate_random_horse() -> Horse:
    """
    Generate a random horse.

    Convenience function for functional-style API.

    Returns:
        Horse: New random horse

    Example:
        horse = generate_random_horse()
    """
    return Horse.random()


def breed_horses(parent1: Horse, parent2: Horse) -> Horse:
    """
    Breed two horses to produce offspring.

    Convenience function for functional-style API.

    Args:
        parent1: First parent
        parent2: Second parent

    Returns:
        Horse: Offspring horse

    Example:
        foal = breed_horses(mare, stallion)
    """
    return Horse.breed(parent1, parent2)


def parse_horse(genotype_str: str) -> Horse:
    """
    Create horse from genotype string.

    Convenience function for functional-style API.

    Args:
        genotype_str: Genotype string

    Returns:
        Horse: New horse

    Example:
        horse = parse_horse("E:E/e A:A/a Dil:N/Cr ...")
    """
    return Horse.from_string(genotype_str)
