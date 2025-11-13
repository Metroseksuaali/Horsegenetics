"""
Gene Registry module - Registry pattern for gene management

This module implements the Registry pattern, allowing dynamic gene management
and making it easy to extend the system with new genes without modifying core code.

Useful for game projects that might want to add custom genes or traits.
"""

import random
from typing import Dict, List, Tuple, Optional, Callable, Set
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

    def generate_random_genotype(
        self,
        excluded_genes: Optional[Set[str]] = None,
        custom_probabilities: Optional[Dict[str, float]] = None
    ) -> Dict[str, Tuple[str, str]]:
        """
        Generate a random complete genotype for all registered genes.

        Args:
            excluded_genes: Set of gene names to exclude (force to wild-type/recessive)
                           Example: {'gray', 'dominant_white'} will prevent gray and white horses
            custom_probabilities: Dict mapping gene names to custom probability of recessive allele
                                 Example: {'gray': 0.5} will make 75% of horses gray
                                 Value should be between 0.0 and 1.0

        Returns:
            dict: Complete genotype with all genes
                  Format: {'gene_name': ('allele1', 'allele2'), ...}
        """
        excluded_genes = excluded_genes or set()
        custom_probabilities = custom_probabilities or {}

        genotype = {}
        for gene_name in self._gene_order:
            gene = self._genes[gene_name]
            excluded = gene_name in excluded_genes
            custom_prob = custom_probabilities.get(gene_name)
            genotype[gene_name] = self._random_allele_pair(gene, excluded, custom_prob)
        return genotype

    def _random_allele_pair(
        self,
        gene: GeneDefinition,
        excluded: bool = False,
        custom_probability: Optional[float] = None
    ) -> Tuple[str, str]:
        """
        Generate a random pair of alleles for a gene.

        Avoids lethal combinations:
        - Frame Overo O/O (LWOS)
        - Dominant White lethal homozygous (W1/W1, W5/W5, W10/W10, W13/W13, W22/W22)

        Uses weighted probabilities for rare genes:
        - Dominant White: ~2-5% (rare in real horses)
        - Frame Overo: ~10% (uncommon)

        Args:
            gene: GeneDefinition to generate alleles for
            excluded: If True, force gene to wild-type/recessive (gene excluded from generation)
            custom_probability: Custom probability of recessive allele (0.0-1.0)
                               Overrides default probabilities if provided

        Returns:
            tuple: Sorted pair of alleles (guaranteed viable)
        """
        # Handle excluded genes - force to wild-type/recessive
        if excluded:
            # Find the recessive/wild-type allele (usually 'n', 'g', 'lp', etc.)
            wildtype = self._get_wildtype_allele(gene)
            return (wildtype, wildtype)
        max_attempts = 100
        for _ in range(max_attempts):
            # Handle custom probability if provided
            if custom_probability is not None:
                allele1, allele2 = self._generate_with_custom_probability(
                    gene, custom_probability
                )
            # Special handling for genes with realistic frequency-based weighted probabilities
            # Based on research: Sabino/Gray common (25-35%), Tobiano moderate (15-25%),
            # Roan/Leopard uncommon (5-10%), Frame rare (3-7%), Splash/Champagne very rare (2-5%),
            # Dominant White extremely rare (1-3%)

            elif gene.name == 'dominant_white':
                # Dominant White: extremely rare (~1-3% population)
                # "Quite rare, only handful of families" - research
                if random.random() < 0.99:  # 99% chance of 'n' per allele → ~2% DW
                    allele1 = 'n'
                else:
                    w_alleles = [a for a in gene.alleles if a != 'n']
                    allele1 = random.choice(w_alleles)

                if random.random() < 0.99:
                    allele2 = 'n'
                else:
                    w_alleles = [a for a in gene.alleles if a != 'n']
                    allele2 = random.choice(w_alleles)

            elif gene.name == 'frame':
                # Frame Overo: rare (~3-7% population pure Frame, additional Tovero combinations)
                # "Rare in most breeds except Paint" - research
                # Note: Tovero (Tobiano + Frame) will add to total Frame count
                if random.random() < 0.98:  # 98% chance of 'n' → ~4% pure Frame
                    allele1 = 'n'
                else:
                    allele1 = 'O'

                if random.random() < 0.98:
                    allele2 = 'n'
                else:
                    allele2 = 'O'

            elif gene.name == 'tobiano':
                # Tobiano: moderately common (~15-25% population)
                # Common in Paint, moderate elsewhere
                if random.random() < 0.88:  # 88% chance of 'n' → ~23% Tobiano
                    allele1 = 'n'
                else:
                    allele1 = 'To'

                if random.random() < 0.88:
                    allele2 = 'n'
                else:
                    allele2 = 'To'

            elif gene.name == 'sabino':
                # Sabino: common (~25-35% population)
                # "Extremely widespread, found in virtually all breeds" - research
                if random.random() < 0.80:  # 80% chance of 'n' → ~36% Sabino
                    allele1 = 'n'
                else:
                    allele1 = 'Sb1'

                if random.random() < 0.80:
                    allele2 = 'n'
                else:
                    allele2 = 'Sb1'

            elif gene.name == 'splash':
                # Splash White: very rare (~2-5% population)
                # "Least common overo pattern, very rare" - research
                if random.random() < 0.975:  # 97.5% chance of 'n' → ~5% Splash
                    allele1 = 'n'
                else:
                    splash_alleles = [a for a in gene.alleles if a != 'n']
                    allele1 = random.choice(splash_alleles)

                if random.random() < 0.975:
                    allele2 = 'n'
                else:
                    splash_alleles = [a for a in gene.alleles if a != 'n']
                    allele2 = random.choice(splash_alleles)

            elif gene.name == 'roan':
                # Roan: uncommon (~5-10% population)
                # "Rare in Icelandic horse population" - research
                if random.random() < 0.962:  # 96.2% chance of 'n' → ~7.5% Roan
                    allele1 = 'n'
                else:
                    allele1 = 'Rn'

                if random.random() < 0.962:
                    allele2 = 'n'
                else:
                    allele2 = 'Rn'

            elif gene.name == 'leopard':
                # Leopard/Appaloosa: uncommon (~5-10% general population)
                # "Lower frequency in most breeds" - research
                if random.random() < 0.962:  # 96.2% chance of 'lp' → ~7.5% Leopard
                    allele1 = 'lp'
                else:
                    allele1 = 'Lp'

                if random.random() < 0.962:
                    allele2 = 'lp'
                else:
                    allele2 = 'Lp'

            elif gene.name == 'gray':
                # Gray: common (~25-35% population)
                # Very common dominant gene across breeds
                if random.random() < 0.84:  # 84% chance of 'g' → ~30% Gray
                    allele1 = 'g'
                else:
                    allele1 = 'G'

                if random.random() < 0.84:
                    allele2 = 'g'
                else:
                    allele2 = 'G'

            elif gene.name == 'champagne':
                # Champagne: very rare (~2-4% population)
                # "Fairly rare gene, less common dilution" - research
                if random.random() < 0.985:  # 98.5% chance of 'n' → ~3% Champagne
                    allele1 = 'n'
                else:
                    allele1 = 'Ch'

                if random.random() < 0.985:
                    allele2 = 'n'
                else:
                    allele2 = 'Ch'

            else:
                # Normal random selection for common genes
                allele1 = random.choice(gene.alleles)
                allele2 = random.choice(gene.alleles)

            pair = gene.sort_alleles([allele1, allele2])

            # Check for lethal combinations
            # Frame Overo: O/O is lethal
            if gene.name == 'frame' and pair == ('O', 'O'):
                continue

            # Dominant White: Most homozygous combinations are lethal (except W20/W20)
            if gene.name == 'dominant_white':
                lethal_w_alleles = ['W1', 'W5', 'W10', 'W13', 'W22']
                if pair[0] == pair[1] and pair[0] in lethal_w_alleles:
                    continue

            # Valid combination found
            return pair

        # Fallback: force heterozygous or homozygous wildtype
        if gene.name == 'frame':
            return ('n', 'n')  # Safe: no Frame Overo
        elif gene.name == 'dominant_white':
            return ('n', 'n')  # Safe: no Dominant White
        else:
            return gene.sort_alleles([gene.alleles[0], gene.alleles[0]])

    def _get_wildtype_allele(self, gene: GeneDefinition) -> str:
        """
        Get the wild-type/recessive allele for a gene.

        Args:
            gene: GeneDefinition to get wildtype for

        Returns:
            str: Wild-type allele (usually 'n', 'g', 'lp', 'e', 'a', etc.)
        """
        # Map gene names to their wild-type alleles
        wildtype_map = {
            'extension': 'e',
            'agouti': 'a',
            'dilution': 'N',
            'dun': 'nd2',
            'dominant_white': 'n',
            'frame': 'n',
            'tobiano': 'n',
            'sabino': 'n',
            'splash': 'n',
            'roan': 'n',
            'leopard': 'lp',
            'gray': 'g',
            'champagne': 'n',
            'flaxen': 'f',
            'sooty': 'sty'
        }
        return wildtype_map.get(gene.name, gene.alleles[0])

    def _generate_with_custom_probability(
        self, gene: GeneDefinition, probability: float
    ) -> Tuple[str, str]:
        """
        Generate alleles using custom probability for recessive allele.

        Args:
            gene: GeneDefinition to generate alleles for
            probability: Probability of getting recessive allele per draw (0.0-1.0)

        Returns:
            tuple: Pair of alleles
        """
        wildtype = self._get_wildtype_allele(gene)
        other_alleles = [a for a in gene.alleles if a != wildtype]

        # Generate first allele
        if random.random() < probability:
            allele1 = wildtype
        else:
            allele1 = random.choice(other_alleles) if other_alleles else wildtype

        # Generate second allele
        if random.random() < probability:
            allele2 = wildtype
        else:
            allele2 = random.choice(other_alleles) if other_alleles else wildtype

        return allele1, allele2

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
            error_text += "  E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty G:G/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"

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
