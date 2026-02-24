"""
Core genetics module - Gene pools and allele definitions

DEPRECATED: This module only defines 9 of 17 genes.
Use genetics.gene_definitions and genetics.gene_registry for full 17-gene support.

This module is kept for backwards compatibility only.
"""

import random


class GenePool:
    """
    Manages all genetic alleles and provides core genetic operations.

    This class is designed to be extensible for thousands of genetic traits.
    """

    def __init__(self):
        """Initialize all gene pools with their alleles."""

        # Extension gene (MC1R) - determines red vs black pigment
        self.extension_alleles = ['E', 'e']

        # Agouti gene (ASIP) - determines bay vs black distribution
        self.agouti_alleles = ['A', 'a']

        # Dilution gene (SLC45A2) - Cream and Pearl are alleles of SAME gene
        # N = wild-type, Cr = cream, Prl = pearl
        self.dilution_alleles = ['N', 'Cr', 'Prl']

        # Dun gene (TBX3) - creates dun dilution with primitive markings
        # D = dun, nd1 = non-dun1, nd2 = non-dun2
        self.dun_alleles = ['D', 'nd1', 'nd2']

        # Silver gene (PMEL17) - dilutes black pigment
        # Z = silver (dominant), n = non-silver
        self.silver_alleles = ['Z', 'n']

        # Champagne gene (SLC36A1) - dilutes both red and black pigment
        # Ch = champagne (dominant), n = non-champagne
        self.champagne_alleles = ['Ch', 'n']

        # Flaxen gene - lightens mane/tail on chestnuts only
        # Genetic basis unknown (suspected polygenic); simplified as single recessive
        # F = non-flaxen, f = flaxen (only visible on e/e)
        self.flaxen_alleles = ['F', 'f']

        # Sooty gene - adds darker hairs (simplified - actually polygenic)
        # STY = sooty, sty = non-sooty
        self.sooty_alleles = ['STY', 'sty']

        # Gray gene (STX17) - progressive graying with age
        # G = gray (dominant), g = non-gray
        # Note: Horses are born colored and progressively gray with age
        self.gray_alleles = ['G', 'g']

        # Dominance hierarchy for sorting alleles consistently
        self.dominance_order = {
            'E': 10, 'e': 1,
            'A': 10, 'a': 1,
            'N': 10, 'Cr': 5, 'Prl': 3,
            'D': 10, 'nd1': 5, 'nd2': 1,
            'Z': 10, 'n': 1,  # Note: 'n' used by both Silver and Champagne
            'Ch': 10,  # 'n' for champagne has same dominance as for silver (1)
            'F': 10, 'f': 1,
            'STY': 10, 'sty': 1,
            'G': 10, 'g': 1
        }

    def generate_random_genotype(self):
        """
        Generate a random complete genotype for all genes.

        Returns:
            dict: Complete genotype with all genes
        """
        return {
            'extension': self._random_pair(self.extension_alleles),
            'agouti': self._random_pair(self.agouti_alleles),
            'dilution': self._random_pair(self.dilution_alleles),
            'dun': self._random_pair(self.dun_alleles),
            'silver': self._random_pair(self.silver_alleles),
            'champagne': self._random_pair(self.champagne_alleles),
            'flaxen': self._random_pair(self.flaxen_alleles),
            'sooty': self._random_pair(self.sooty_alleles),
            'gray': self._random_pair(self.gray_alleles)
        }

    def _random_pair(self, alleles):
        """
        Generate a random pair of alleles.

        Args:
            alleles: List of possible alleles

        Returns:
            tuple: Sorted pair of alleles
        """
        allele1 = random.choice(alleles)
        allele2 = random.choice(alleles)
        return self._sort_alleles([allele1, allele2])

    def _sort_alleles(self, allele_list):
        """
        Sort alleles by dominance for consistent display.

        Args:
            allele_list: List of alleles to sort

        Returns:
            tuple: Sorted alleles (dominant first)
        """
        sorted_alleles = sorted(
            allele_list,
            key=lambda x: self.dominance_order.get(x, 0),
            reverse=True
        )
        return tuple(sorted_alleles)

    def count_alleles(self, genotype, allele):
        """
        Count copies of a specific allele in a genotype.

        Args:
            genotype: Tuple of alleles
            allele: Allele to count

        Returns:
            int: Number of copies (0, 1, or 2)
        """
        return genotype.count(allele)

    def determine_base_color(self, extension, agouti):
        """
        Determine base coat color from Extension and Agouti genes.

        Extension gene is epistatic to Agouti (E/e masks A/a expression).

        Args:
            extension: Extension genotype tuple
            agouti: Agouti genotype tuple

        Returns:
            str: Base color ('chestnut', 'bay', or 'black')
        """
        # Homozygous recessive extension = chestnut (red)
        if extension == ('e', 'e'):
            return 'chestnut'

        # At least one E allele = black pigment
        # Agouti determines distribution
        if 'A' in agouti:
            return 'bay'  # A restricts black to points
        else:
            return 'black'  # a/a = all black
