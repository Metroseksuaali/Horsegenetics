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


class LethalGenotypeError(ValueError):
    """Raised when a lethal genotype is created without explicit permission.

    Inherits from ValueError for backwards compatibility with existing
    exception handlers.
    """
    pass


class Horse:
    """
    Represents a horse with complete genetic information.

    Provides a clean, fluent API for horse genetics operations.
    """

    def __init__(
        self,
        genotype: Dict[str, Tuple[str, str]],
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None,
        allow_lethal: bool = False
    ):
        """
        Create a horse from a genotype.

        Args:
            genotype: Complete genotype dictionary
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)
            allow_lethal: If False (default), raises LethalGenotypeError
                for lethal genotypes. Set True to allow (e.g. for breeding).

        Raises:
            LethalGenotypeError: If genotype is lethal and allow_lethal is False
        """
        self.registry = registry or get_default_registry()
        self.calculator = calculator or PhenotypeCalculator(self.registry)

        # Validate genotype format and allele values
        self.registry.validate_genotype(genotype)
        self._genotype = genotype

        # Calculate phenotype
        self._phenotype = self.calculator.determine_phenotype(genotype)

        # Check for lethal combinations (after phenotype calc so is_lethal works)
        if not allow_lethal:
            from genetics.validation import check_lethal_genotype
            lethal_reason = check_lethal_genotype(genotype)
            if lethal_reason:
                raise LethalGenotypeError(
                    f"Lethal genotype: {lethal_reason}. "
                    f"Use allow_lethal=True to create this horse explicitly."
                )

    @property
    def is_lethal(self) -> bool:
        """Check if this horse has a lethal genotype (NONVIABLE phenotype)."""
        return 'NONVIABLE' in self._phenotype

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
        calculator: Optional[PhenotypeCalculator] = None,
        excluded_genes: Optional[set] = None,
        custom_probabilities: Optional[dict] = None
    ) -> 'Horse':
        """
        Generate a random horse.

        Args:
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)
            excluded_genes: Set of gene names to exclude (force to wild-type)
                           Example: {'gray', 'dominant_white'} prevents gray/white horses
            custom_probabilities: Dict mapping gene names to custom probability of recessive allele
                                 Example: {'gray': 0.5} makes 75% of horses gray

        Returns:
            Horse: New random horse

        Example:
            # Normal random horse
            horse = Horse.random()

            # No gray horses
            horse = Horse.random(excluded_genes={'gray'})

            # 90% gray horses
            horse = Horse.random(custom_probabilities={'gray': 0.1})
        """
        reg = registry or get_default_registry()
        genotype = reg.generate_random_genotype(excluded_genes, custom_probabilities)
        return cls(genotype, reg, calculator)

    @classmethod
    def from_string(
        cls,
        genotype_str: str,
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None,
        allow_lethal: bool = False
    ) -> 'Horse':
        """
        Create horse from genotype string.

        Args:
            genotype_str: Genotype string (e.g., "E:E/e A:A/a Dil:N/N ...")
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)
            allow_lethal: If False (default), raises LethalGenotypeError
                for lethal genotypes like Frame Overo O/O.

        Returns:
            Horse: New horse with specified genotype

        Raises:
            LethalGenotypeError: If genotype is lethal and allow_lethal is False

        Example:
            horse = Horse.from_string("E:e/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:f/f STY:sty/sty G:g/g")
        """
        reg = registry or get_default_registry()
        genotype = reg.parse_genotype_string(genotype_str)
        return cls(genotype, reg, calculator, allow_lethal=allow_lethal)

    @classmethod
    def from_dict(
        cls,
        data: dict,
        registry: Optional[GeneRegistry] = None,
        calculator: Optional[PhenotypeCalculator] = None,
        allow_lethal: bool = False
    ) -> 'Horse':
        """
        Create horse from dictionary.

        Args:
            data: Dictionary with 'genotype' key
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)
            allow_lethal: If False (default), raises LethalGenotypeError
                for lethal genotypes.

        Returns:
            Horse: New horse

        Raises:
            LethalGenotypeError: If genotype is lethal and allow_lethal is False

        Example:
            data = {'genotype': {'extension': ('E', 'e'), ...}}
            horse = Horse.from_dict(data)
        """
        genotype = data['genotype']
        return cls(genotype, registry, calculator, allow_lethal=allow_lethal)

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
        random allele from each gene. Lethal offspring are allowed
        since they are a realistic result of carrier crosses
        (e.g. O/n x O/n can produce 25% O/O = LWOS).

        Args:
            parent1: First parent
            parent2: Second parent
            registry: Gene registry (uses default if None)
            calculator: Phenotype calculator (creates new if None)

        Returns:
            Horse: Offspring horse (check .is_lethal for viability)

        Example:
            mare = Horse.random()
            stallion = Horse.random()
            foal = Horse.breed(mare, stallion)
        """
        reg = registry or get_default_registry()
        offspring_genotype = reg.breed(parent1._genotype, parent2._genotype)
        return cls(offspring_genotype, reg, calculator, allow_lethal=True)


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
