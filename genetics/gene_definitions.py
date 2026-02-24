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
    alleles=['A', 'At', 'a'],
    dominance_order={'A': 10, 'At': 5, 'a': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Controls distribution of black pigment (only visible with E/_). Multiple alleles: A (bay), At (seal brown/black-and-tan), a (recessive black).',
    effects='A/_ = bay (black restricted to points), At/At or At/a = seal brown (near-black body with tan muzzle/flanks/armpits), a/a = uniform black. Not expressed on e/e.'
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

ROAN = GeneDefinition(
    name='roan',
    symbol='Rn',
    full_name='Roan',
    locus='KIT',
    alleles=['Rn', 'n'],
    dominance_order={'Rn': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Intermingled white and colored hairs throughout coat. Historically thought lethal when homozygous, but recent research shows Rn/Rn horses are viable.',
    effects='Rn/Rn or Rn/n = roan pattern (white hairs evenly intermixed), n/n = solid. Note: Homozygous roans may be less common due to historical beliefs.'
)

TOBIANO = GeneDefinition(
    name='tobiano',
    symbol='To',
    full_name='Tobiano',
    locus='KIT',
    alleles=['To', 'n'],
    dominance_order={'To': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='White spotting pattern with rounded edges, white crosses back',
    effects='To/To or To/n = tobiano pattern (white patches with clean edges). Crosses back between withers and tail.'
)

FRAME_OVERO = GeneDefinition(
    name='frame',
    symbol='O',
    full_name='Frame Overo',
    locus='EDNRB',
    alleles=['O', 'n'],
    dominance_order={'O': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='White spotting pattern, rarely crosses back. LETHAL when homozygous (LWOS).',
    effects='O/n = frame overo pattern (white usually horizontal), O/O = LETHAL (Lethal White Overo Syndrome), n/n = solid'
)

SABINO = GeneDefinition(
    name='sabino',
    symbol='Sb',
    full_name='Sabino',
    locus='KIT',
    alleles=['Sb1', 'n'],
    dominance_order={'Sb1': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.INCOMPLETE_DOMINANT,
    description='White spotting with irregular edges, high white on legs, white face',
    effects='Sb1/Sb1 = maximum sabino (often mostly white), Sb1/n = sabino pattern, n/n = solid'
)

DOMINANT_WHITE = GeneDefinition(
    name='dominant_white',
    symbol='W',
    full_name='Dominant White',
    locus='KIT',
    alleles=['W1', 'W5', 'W10', 'W13', 'W20', 'W22', 'n'],
    dominance_order={'W1': 10, 'W5': 9, 'W10': 8, 'W13': 7, 'W20': 6, 'W22': 5, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='White or mostly white coat. Multiple alleles (W1-W39 exist). Most are LETHAL when homozygous.',
    effects='W_/n = white/mostly white, W20/W20 = viable white, W1/W1, W5/W5, W10/W10, W13/W13, W22/W22 = LETHAL (embryonic death)'
)

SPLASH_WHITE = GeneDefinition(
    name='splash',
    symbol='Spl',
    full_name='Splash White',
    locus='MITF',
    alleles=['Sw1', 'Sw2', 'Sw3', 'n'],
    dominance_order={'Sw1': 10, 'Sw2': 9, 'Sw3': 8, 'n': 1},
    inheritance_pattern=InheritancePattern.INCOMPLETE_DOMINANT,
    description='White spotting from bottom up, blue eyes common',
    effects='Splash alleles cause white from legs/belly upward, often with blue eyes'
)

LEOPARD_COMPLEX = GeneDefinition(
    name='leopard',
    symbol='Lp',
    full_name='Leopard Complex',
    locus='TRPM1',
    alleles=['Lp', 'lp'],
    dominance_order={'Lp': 10, 'lp': 1},
    inheritance_pattern=InheritancePattern.INCOMPLETE_DOMINANT,
    description='Appaloosa spotting pattern, creates various patterns',
    effects='Lp/Lp = fewspot/snowcap (mostly white with color on head/legs), Lp/lp = leopard/blanket patterns, lp/lp = solid'
)

# Requires PATN genes for full leopard patterns
PATN1 = GeneDefinition(
    name='patn1',
    symbol='PATN1',
    full_name='Pattern 1',
    locus='PATN1',
    alleles=['PATN1', 'n'],
    dominance_order={'PATN1': 10, 'n': 1},
    inheritance_pattern=InheritancePattern.DOMINANT,
    description='Modifies leopard complex to create leopard pattern (spots all over)',
    effects='PATN1 + Lp = leopard pattern (white with dark spots). No effect without Lp.'
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
    GRAY,
    ROAN,
    TOBIANO,
    FRAME_OVERO,
    SABINO,
    DOMINANT_WHITE,
    SPLASH_WHITE,
    LEOPARD_COMPLEX,
    PATN1
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


# ============================================================================
# LETHAL COMBINATIONS - Single source of truth
# ============================================================================

LETHAL_COMBINATIONS: Dict[str, Dict[str, Any]] = {
    'frame': {
        'genotypes': [('O', 'O')],
        'description': 'Lethal White Overo Syndrome (LWOS)',
    },
    'dominant_white': {
        'genotypes': [
            ('W1', 'W1'), ('W5', 'W5'), ('W10', 'W10'),
            ('W13', 'W13'), ('W22', 'W22'),
        ],
        'description': 'Homozygous Dominant White - embryonic lethal',
    },
}
