"""
Gene definitions module - Centralized gene data structures

This module contains all gene definitions in a centralized, data-driven format.
Makes it easy to add new genes or modify existing ones without touching core logic.

Scientific basis: Each gene definition includes molecular basis, inheritance pattern,
and phenotypic effects based on peer-reviewed equine genetics research.
"""

from typing import List, Dict, Any, Callable, Tuple
from enum import Enum
from functools import lru_cache


class InheritancePattern(Enum):
    """Inheritance patterns for genes."""
    DOMINANT = "dominant"
    RECESSIVE = "recessive"
    CODOMINANT = "codominant"
    INCOMPLETE_DOMINANT = "incomplete_dominant"
    EPISTATIC = "epistatic"


class GeneDefinition:
    """
    Complete definition of a genetic trait.

    Attributes:
        name: Internal gene name (e.g., 'extension')
        symbol: Short symbol for display (e.g., 'E')
        full_name: Full scientific name
        locus: Genetic locus/gene name (e.g., 'MC1R')
        alleles: List of possible alleles
        dominance_order: Allele dominance hierarchy (higher = more dominant)
        inheritance_pattern: How the gene is inherited
        description: Scientific description
        effects: What the gene does phenotypically
    """

    def __init__(
        self,
        name: str,
        symbol: str,
        full_name: str,
        locus: str,
        alleles: List[str],
        dominance_order: Dict[str, int],
        inheritance_pattern: InheritancePattern,
        description: str,
        effects: str
    ):
        self.name = name
        self.symbol = symbol
        self.full_name = full_name
        self.locus = locus
        self.alleles = alleles
        self.dominance_order = dominance_order
        self.inheritance_pattern = inheritance_pattern
        self.description = description
        self.effects = effects

    def sort_alleles(self, allele_list: List[str]) -> Tuple[str, str]:
        """Sort alleles by dominance for consistent display."""
        sorted_alleles = sorted(
            allele_list,
            key=lambda x: self.dominance_order.get(x, 0),
            reverse=True
        )
        return tuple(sorted_alleles)


# ============================================================================
# GENE DEFINITIONS - All equine coat color genes
# ============================================================================

EXTENSION = GeneDefinition(
    name='extension',
    symbol='E',
    full_name='Extension',
    locus='MC1R',
    alleles=['E', 'e'],
    dominance_order={'E': 10, 'e': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Controls whether black (eumelanin) or red (pheomelanin) pigment is produced',
    effects='E = black pigment, e/e = red pigment (chestnut). Epistatic to Agouti.'
)

AGOUTI = GeneDefinition(
    name='agouti',
    symbol='A',
    full_name='Agouti',
    locus='ASIP',
    alleles=['A', 'a'],
    dominance_order={'A': 10, 'a': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Controls distribution of black pigment (only visible with E/_)',
    effects='A = restricts black to points (bay), a/a = uniform black. Not expressed on e/e.'
)

DILUTION = GeneDefinition(
    name='dilution',
    symbol='Dil',
    full_name='Dilution (Cream/Pearl)',
    locus='SLC45A2',
    alleles=['N', 'Cr', 'Prl'],
    dominance_order={'N': 10, 'Cr': 5, 'Prl': 3},
    inheritance_pattern=InheritancePattern.INCOMPLETE_DOMINANT,
    description='Cream and Pearl dilutions (same locus, different alleles)',
    effects='Cr = incomplete dominant cream dilution, Prl = recessive pearl dilution'
)

DUN = GeneDefinition(
    name='dun',
    symbol='D',
    full_name='Dun',
    locus='TBX3',
    alleles=['D', 'nd1', 'nd2'],
    dominance_order={'D': 10, 'nd1': 5, 'nd2': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Dilutes coat and adds primitive markings (dorsal stripe, leg bars)',
    effects='D = dun with primitive markings, nd1 = non-dun1 allele, nd2 = non-dun2 allele'
)

SILVER = GeneDefinition(
    name='silver',
    symbol='Z',
    full_name='Silver',
    locus='PMEL17',
    alleles=['Z', 'n'],
    dominance_order={'Z': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Dilutes black (eumelanin) pigment only, especially mane and tail',
    effects='Z = silver dilution on black pigment. Does not affect red (chestnut).'
)

CHAMPAGNE = GeneDefinition(
    name='champagne',
    symbol='Ch',
    full_name='Champagne',
    locus='SLC36A1',
    alleles=['Ch', 'n'],
    dominance_order={'Ch': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Dilutes both red and black pigment, causes amber eyes',
    effects='Ch = champagne dilution affecting both pigment types'
)

FLAXEN = GeneDefinition(
    name='flaxen',
    symbol='F',
    full_name='Flaxen',
    locus='Unknown (polygenic)',
    alleles=['F', 'f'],
    dominance_order={'F': 10, 'f': 1},
    inheritance_pattern=InheritancePattern.RECESSIVE,
    description='Lightens mane and tail on chestnut horses only (simplified model)',
    effects='f/f = flaxen mane/tail on e/e horses. Not visible on black-based colors.'
)

SOOTY = GeneDefinition(
    name='sooty',
    symbol='STY',
    full_name='Sooty',
    locus='Unknown (polygenic)',
    alleles=['STY', 'sty'],
    dominance_order={'STY': 10, 'sty': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Adds darker (black) hairs to red pigment areas (simplified model)',
    effects='STY = darker hairs on coat. Only visible on colors with red pigment.'
)

GRAY = GeneDefinition(
    name='gray',
    symbol='G',
    full_name='Gray',
    locus='STX17',
    alleles=['G', 'g'],
    dominance_order={'G': 10, 'g': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Progressive graying with age (4.6kb duplication in STX17)',
    effects='G = horse born with base color, progressively grays/whitens with age'
)


# ============================================================================
# GENE REGISTRY - Ordered list of all genes
# ============================================================================

ALL_GENES: List[GeneDefinition] = [
    EXTENSION,
    AGOUTI,
    DILUTION,
    DUN,
    SILVER,
    CHAMPAGNE,
    FLAXEN,
    SOOTY,
    GRAY
]

# Quick lookup by name
GENES_BY_NAME: Dict[str, GeneDefinition] = {
    gene.name: gene for gene in ALL_GENES
}

# Quick lookup by symbol
GENES_BY_SYMBOL: Dict[str, GeneDefinition] = {
    gene.symbol: gene for gene in ALL_GENES
}


def get_gene(identifier: str) -> GeneDefinition:
    """
    Get gene definition by name or symbol.

    Args:
        identifier: Gene name (e.g., 'extension') or symbol (e.g., 'E')

    Returns:
        GeneDefinition object

    Raises:
        KeyError: If gene not found
    """
    if identifier in GENES_BY_NAME:
        return GENES_BY_NAME[identifier]
    elif identifier in GENES_BY_SYMBOL:
        return GENES_BY_SYMBOL[identifier]
    else:
        raise KeyError(f"Unknown gene: {identifier}")


def get_all_gene_names() -> List[str]:
    """Get list of all gene internal names."""
    return [gene.name for gene in ALL_GENES]


def get_all_gene_symbols() -> List[str]:
    """Get list of all gene symbols."""
    return [gene.symbol for gene in ALL_GENES]
