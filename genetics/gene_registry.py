"""
Gene Registry module - Registry pattern for gene management

This module implements the Registry pattern, allowing dynamic gene management
and making it easy to extend the system with new genes without modifying core code.

Useful for game projects that might want to add custom genes or traits.
"""

import random
from typing import Dict, List, Tuple, Optional, Callable
from genetics.gene_definitions import (
    GeneDefinition,
    ALL_GENES,
    GENES_BY_NAME,
    get_gene,
    get_all_gene_names
)


class GeneRegistry:
    """
    Central registry for all genetic traits.

    Uses Registry pattern to allow dynamic gene registration and management.
    Provides methods for genotype generation, validation, and manipulation.
    """

    def __init__(self, genes: Optional[List[GeneDefinition]] = None):
        """
        Initialize registry with gene definitions.

        Args:
            genes: List of GeneDefinition objects. If None, uses ALL_GENES.
        """
        if genes is None:
            genes = ALL_GENES

        self._genes: Dict[str, GeneDefinition] = {
            gene.name: gene for gene in genes
        }
        self._gene_order: List[str] = [gene.name for gene in genes]

    def register_gene(self, gene: GeneDefinition) -> None:
        """
        Register a new gene to the registry.

        Useful for extending the system with custom genes.

        Args:
            gene: GeneDefinition to register
        """
        if gene.name in self._genes:
            raise ValueError(f"Gene '{gene.name}' already registered")

        self._genes[gene.name] = gene
        self._gene_order.append(gene.name)

    def get_gene(self, name: str) -> GeneDefinition:
        """
        Get gene definition by name.

        Args:
            name: Gene name (e.g., 'extension')

        Returns:
            GeneDefinition object

        Raises:
            KeyError: If gene not found
        """
        if name not in self._genes:
            raise KeyError(f"Gene '{name}' not found in registry")
        return self._genes[name]

    def get_all_gene_names(self) -> List[str]:
        """Get ordered list of all registered gene names."""
        return self._gene_order.copy()

    def generate_random_genotype(self) -> Dict[str, Tuple[str, str]]:
        """
        Generate a random complete genotype for all registered genes.

        Returns:
            dict: Complete genotype with all genes
                  Format: {'gene_name': ('allele1', 'allele2'), ...}
        """
        genotype = {}
        for gene_name in self._gene_order:
            gene = self._genes[gene_name]
            genotype[gene_name] = self._random_allele_pair(gene)
        return genotype

    def _random_allele_pair(self, gene: GeneDefinition) -> Tuple[str, str]:
        """
        Generate a random pair of alleles for a gene.

        Args:
            gene: GeneDefinition to generate alleles for

        Returns:
            tuple: Sorted pair of alleles
        """
        allele1 = random.choice(gene.alleles)
        allele2 = random.choice(gene.alleles)
        return gene.sort_alleles([allele1, allele2])

    def count_alleles(self, genotype: Tuple[str, str], allele: str) -> int:
        """
        Count copies of a specific allele in a genotype.

        Args:
            genotype: Tuple of alleles (e.g., ('E', 'e'))
            allele: Allele to count (e.g., 'E')

        Returns:
            int: Number of copies (0, 1, or 2)
        """
        return genotype.count(allele)

    def has_allele(self, genotype: Tuple[str, str], allele: str) -> bool:
        """
        Check if genotype contains at least one copy of an allele.

        Args:
            genotype: Tuple of alleles
            allele: Allele to check for

        Returns:
            bool: True if allele present
        """
        return allele in genotype

    def is_homozygous(self, genotype: Tuple[str, str]) -> bool:
        """
        Check if genotype is homozygous (both alleles the same).

        Args:
            genotype: Tuple of alleles

        Returns:
            bool: True if homozygous
        """
        return genotype[0] == genotype[1]

    def validate_genotype(self, genotype: Dict[str, Tuple[str, str]]) -> bool:
        """
        Validate that a genotype dictionary is properly formed.

        Args:
            genotype: Genotype dictionary to validate

        Returns:
            bool: True if valid

        Raises:
            ValueError: If genotype is invalid
        """
        # Check all required genes present
        for gene_name in self._gene_order:
            if gene_name not in genotype:
                raise ValueError(f"Missing gene: {gene_name}")

        # Check each gene's alleles are valid
        for gene_name, alleles in genotype.items():
            if gene_name not in self._genes:
                raise ValueError(f"Unknown gene: {gene_name}")

            gene = self._genes[gene_name]

            if not isinstance(alleles, tuple) or len(alleles) != 2:
                raise ValueError(
                    f"Invalid {gene_name} genotype: must be tuple of 2 alleles"
                )

            for allele in alleles:
                if allele not in gene.alleles:
                    raise ValueError(
                        f"Invalid allele '{allele}' for gene {gene_name}. "
                        f"Valid alleles: {gene.alleles}"
                    )

        return True

    def breed(
        self,
        parent1_genotype: Dict[str, Tuple[str, str]],
        parent2_genotype: Dict[str, Tuple[str, str]]
    ) -> Dict[str, Tuple[str, str]]:
        """
        Breed two genotypes following Mendelian inheritance.

        Each parent contributes one random allele from each gene.

        Args:
            parent1_genotype: Complete genotype dict for parent 1
            parent2_genotype: Complete genotype dict for parent 2

        Returns:
            dict: Offspring genotype

        Raises:
            ValueError: If genotypes are invalid
        """
        # Validate parents
        self.validate_genotype(parent1_genotype)
        self.validate_genotype(parent2_genotype)

        offspring_genotype = {}

        # For each gene, offspring gets one allele from each parent
        for gene_name in self._gene_order:
            gene = self._genes[gene_name]

            # Random allele from parent 1
            allele_from_parent1 = random.choice(parent1_genotype[gene_name])
            # Random allele from parent 2
            allele_from_parent2 = random.choice(parent2_genotype[gene_name])

            # Sort alleles by dominance
            offspring_genotype[gene_name] = gene.sort_alleles(
                [allele_from_parent1, allele_from_parent2]
            )

        return offspring_genotype

    def format_genotype(
        self,
        genotype: Dict[str, Tuple[str, str]],
        compact: bool = True
    ) -> str:
        """
        Format genotype for display.

        Args:
            genotype: Complete genotype dictionary
            compact: If True, use compact format. If False, use detailed format.

        Returns:
            str: Formatted genotype string
        """
        if compact:
            return self._format_genotype_compact(genotype)
        else:
            return self._format_genotype_detailed(genotype)

    def _format_genotype_compact(
        self,
        genotype: Dict[str, Tuple[str, str]]
    ) -> str:
        """Format genotype in compact format (one line)."""
        parts = []
        for gene_name in self._gene_order:
            gene = self._genes[gene_name]
            alleles = '/'.join(genotype[gene_name])
            parts.append(f"{gene.symbol}:{alleles}")
        return " ".join(parts)

    def _format_genotype_detailed(
        self,
        genotype: Dict[str, Tuple[str, str]]
    ) -> str:
        """Format genotype in detailed format (multi-line)."""
        lines = []
        for gene_name in self._gene_order:
            gene = self._genes[gene_name]
            alleles = '/'.join(genotype[gene_name])
            # Align symbols nicely
            symbol_padded = f"{gene.full_name} ({gene.symbol}):".ljust(25)
            lines.append(f"{symbol_padded}{alleles}")
        return '\n'.join(lines)

    def parse_genotype_string(self, genotype_str: str) -> Dict[str, Tuple[str, str]]:
        """
        Parse user input genotype string with helpful error messages.

        Expected format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty G:G/g

        Args:
            genotype_str: String representation of genotype

        Returns:
            dict: Parsed genotype dictionary

        Raises:
            ValueError: If genotype string is invalid (with helpful suggestions)
        """
        # Use validation module for better error messages
        from genetics.validation import validate_genotype_string, validate_allele_values

        # First validate format
        validation_result = validate_genotype_string(genotype_str)

        if validation_result['errors']:
            error_messages = validation_result['errors']
            info_messages = validation_result['info']

            error_text = "Invalid genotype format:\n"
            for i, err in enumerate(error_messages, 1):
                error_text += f"  {i}. {err}\n"

            if info_messages:
                error_text += "\nHelp:\n"
                for info in info_messages:
                    error_text += f"  • {info}\n"

            error_text += "\nExpected format:\n"
            error_text += "  E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty G:G/g"

            raise ValueError(error_text)

        # Then validate allele values
        allele_validation = validate_allele_values(genotype_str)
        if allele_validation['errors']:
            error_text = "Invalid allele values:\n"
            for i, err in enumerate(allele_validation['errors'], 1):
                error_text += f"  {i}. {err}\n"
            raise ValueError(error_text)

        # If validation passed, parse the genotype
        genotype = {}

        try:
            parts = genotype_str.strip().split()

            for part in parts:
                if ':' not in part:
                    continue

                symbol, alleles_str = part.split(':', 1)
                alleles = alleles_str.split('/')

                # Find gene by symbol
                gene = None
                for g in self._genes.values():
                    if g.symbol == symbol:
                        gene = g
                        break

                if gene is not None:
                    genotype[gene.name] = gene.sort_alleles(alleles)

            return genotype

        except Exception as e:
            raise ValueError(
                f"Unexpected error parsing genotype: {e}\n"
                f"Please check format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty G:G/g"
            )


# Global default registry instance
_default_registry = GeneRegistry()


def get_default_registry() -> GeneRegistry:
    """Get the default global gene registry."""
    return _default_registry
