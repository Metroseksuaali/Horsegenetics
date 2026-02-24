"""
Gene Interaction module - Phenotype determination from genotypes

This module handles all gene interactions and phenotype calculations.
Uses a modular system of "modifiers" that can be applied in sequence.

Architecture allows easy extension with new genes or interaction patterns.
"""

from typing import Dict, Tuple, Callable, List
from genetics.gene_registry import GeneRegistry


class PhenotypeContext:
    """
    Context object passed through phenotype determination pipeline.

    Contains all information needed to determine phenotype:
    - Complete genotype
    - Base color determination
    - Current phenotype string
    - Registry for gene lookups
    """

    def __init__(self, genotype: Dict[str, Tuple[str, str]], registry: GeneRegistry):
        """
        Initialize phenotype context.

        Args:
            genotype: Complete genotype dictionary
            registry: Gene registry for lookups
        """
        self.genotype = genotype
        self.registry = registry
        self.base_color: str = ""  # 'chestnut', 'bay', or 'black'
        self.phenotype: str = ""  # Current phenotype name (built incrementally)

    def has_allele(self, gene_name: str, allele: str) -> bool:
        """Check if genotype has at least one copy of an allele."""
        return self.registry.has_allele(self.genotype[gene_name], allele)

    def count_alleles(self, gene_name: str, allele: str) -> int:
        """Count copies of an allele in genotype."""
        return self.registry.count_alleles(self.genotype[gene_name], allele)

    def get_genotype(self, gene_name: str) -> Tuple[str, str]:
        """Get genotype for a specific gene."""
        return self.genotype[gene_name]


# ============================================================================
# PHENOTYPE MODIFIERS - Modular functions that determine phenotype
# ============================================================================

def determine_base_color(ctx: PhenotypeContext) -> None:
    """
    Determine base coat color from Extension and Agouti genes.

    Extension gene is epistatic to Agouti (e/e masks A/a expression).

    Modifies ctx.base_color and ctx.phenotype
    """
    extension = ctx.get_genotype('extension')
    agouti = ctx.get_genotype('agouti')

    # Homozygous recessive extension = chestnut (red)
    if extension == ('e', 'e'):
        ctx.base_color = 'chestnut'
        ctx.phenotype = 'Chestnut'
    # At least one E allele = black pigment; Agouti determines distribution
    elif ctx.has_allele('agouti', 'A'):
        # A is dominant over At and a → bay
        ctx.base_color = 'bay'
        ctx.phenotype = 'Bay'
    elif ctx.has_allele('agouti', 'At'):
        # At/At or At/a → seal brown (near-black with tan points)
        ctx.base_color = 'seal_brown'
        ctx.phenotype = 'Seal Brown'
    else:
        # a/a → uniform black
        ctx.base_color = 'black'
        ctx.phenotype = 'Black'


def apply_dilution(ctx: PhenotypeContext) -> None:
    """
    Apply dilution based on SLC45A2 genotype (Cream/Pearl gene).

    Genotypes and effects:
    - N/N: No dilution
    - N/Cr: Single cream (Palomino, Buckskin, Smoky Black)
    - Cr/Cr: Double cream (Cremello, Perlino, Smoky Cream)
    - N/Prl: Pearl carrier (no visible effect)
    - Prl/Prl: Double pearl (Apricot, Pearl Bay, Smoky Pearl)
    - Cr/Prl: Compound heterozygote (pseudo-double dilute)

    Note: Cream is incomplete dominant, Pearl is recessive.

    Modifies ctx.phenotype
    """
    cr_count = ctx.count_alleles('dilution', 'Cr')
    prl_count = ctx.count_alleles('dilution', 'Prl')
    base = ctx.base_color

    # Cr/Cr - Double cream dilution
    if cr_count == 2:
        dilution_map = {
            'chestnut': 'Cremello',
            'bay': 'Perlino',
            'black': 'Smoky Cream',
            'seal_brown': 'Seal Perlino',
        }
        ctx.phenotype = dilution_map[base]

    # Prl/Prl - Double pearl dilution
    elif prl_count == 2:
        dilution_map = {
            'chestnut': 'Apricot',
            'bay': 'Pearl Bay',
            'black': 'Smoky Pearl',
            'seal_brown': 'Seal Pearl',
        }
        ctx.phenotype = dilution_map[base]

    # Cr/Prl - Compound heterozygote (one cream + one pearl)
    elif cr_count == 1 and prl_count == 1:
        dilution_map = {
            'chestnut': 'Palomino Pearl',
            'bay': 'Buckskin Pearl',
            'black': 'Smoky Black Pearl',
            'seal_brown': 'Seal Buckskin Pearl',
        }
        ctx.phenotype = dilution_map[base]

    # N/Cr - Single cream dilution
    elif cr_count == 1:
        dilution_map = {
            'chestnut': 'Palomino',
            'bay': 'Buckskin',
            'black': 'Smoky Black',
            'seal_brown': 'Seal Buckskin',
        }
        ctx.phenotype = dilution_map[base]

    # N/Prl or N/N - No visible dilution (phenotype already set)


def apply_champagne(ctx: PhenotypeContext) -> None:
    """
    Apply champagne dilution to phenotype.

    Champagne (SLC36A1 gene) dilutes both eumelanin (black) and
    pheomelanin (red) pigment.

    Color names:
    - Gold Champagne = chestnut base
    - Amber Champagne = bay base
    - Classic Champagne = black base

    Modifies ctx.phenotype
    """
    if not ctx.has_allele('champagne', 'Ch'):
        return

    # Champagne mapping for different base colors and dilutions.
    # Longer/more specific keys must appear before their substrings
    # (e.g. 'Seal Buckskin Pearl' before 'Seal Buckskin' before 'Buckskin').
    champagne_map = {
        # Seal brown + compound dilutes (longest first)
        'Seal Buckskin Pearl': 'Amber Pearl Champagne',
        'Seal Perlino': 'Perlino Champagne',
        'Seal Buckskin': 'Amber Cream Champagne',
        'Seal Pearl': 'Amber Pearl Champagne',
        'Seal Brown': 'Amber Champagne',
        # Compound heterozygotes (one cream + one pearl)
        'Smoky Black Pearl': 'Classic Pearl Champagne',
        'Palomino Pearl': 'Ivory Pearl Champagne',
        'Buckskin Pearl': 'Amber Pearl Champagne',
        # Double cream dilutes
        'Cremello': 'Gold Cream Champagne',
        'Perlino': 'Perlino Champagne',
        'Smoky Cream': 'Smoky Cream Champagne',
        # Single cream
        'Palomino': 'Gold Cream Champagne',
        'Buckskin': 'Amber Cream Champagne',
        'Smoky Black': 'Classic Cream Champagne',
        # Double pearl
        'Apricot': 'Gold Pearl Champagne',
        'Pearl Bay': 'Amber Pearl Champagne',
        'Smoky Pearl': 'Classic Pearl Champagne',
        # Base colors
        'Chestnut': 'Gold Champagne',
        'Bay': 'Amber Champagne',
        'Black': 'Classic Champagne',
    }

    # Check if phenotype contains any mapped colors
    for base_color, champ_version in champagne_map.items():
        if base_color in ctx.phenotype:
            ctx.phenotype = ctx.phenotype.replace(base_color, champ_version)
            return

    # Fallback - add Champagne prefix
    ctx.phenotype = f"Champagne {ctx.phenotype}"


def apply_silver(ctx: PhenotypeContext) -> None:
    """
    Apply silver dilution to phenotype.

    Silver (PMEL17 gene) only affects eumelanin (black pigment).
    It lightens black pigment, especially in mane and tail.

    Does NOT affect:
    - Chestnut (no black pigment)

    NOTE: Silver DOES affect double cream dilutes (Perlino, Smoky Cream)
    even though the effect is subtle. Must be noted for genetic accuracy.

    Modifies ctx.phenotype
    """
    if not ctx.has_allele('silver', 'Z'):
        return

    # Silver does not affect chestnut (no black pigment)
    if ctx.base_color == 'chestnut':
        return

    # Silver mapping for black/bay-based colors.
    # Sorted by key length (longest first) before iteration to prevent partial matches.
    silver_map = {
        # Double cream dilutes - Silver still applies
        'Perlino': 'Silver Perlino',
        'Smoky Cream': 'Silver Smoky Cream',
        'Pseudo-Perlino': 'Silver Pseudo-Perlino',
        'Pseudo-Smoky Cream': 'Silver Pseudo-Smoky Cream',
        # Seal brown combinations
        'Seal Buckskin Pearl': 'Silver Seal Buckskin Pearl',
        'Seal Perlino': 'Silver Seal Perlino',
        'Seal Buckskin': 'Silver Seal Buckskin',
        'Seal Pearl': 'Silver Seal Pearl',
        'Seal Brown': 'Silver Seal Brown',
        # Compound heterozygotes (one cream + one pearl)
        'Smoky Black Pearl': 'Silver Smoky Black Pearl',
        'Buckskin Pearl': 'Silver Buckskin Pearl',
        'Palomino Pearl': 'Silver Palomino Pearl',
        # Standard colors
        'Black': 'Silver Black',
        'Bay': 'Silver Bay',
        'Smoky Black': 'Silver Smoky Black',
        'Buckskin': 'Silver Buckskin',
        'Pearl Bay': 'Silver Pearl Bay',
        'Smoky Pearl': 'Silver Smoky Pearl',
        # Champagne colors with black/bay base
        'Classic Champagne': 'Silver Classic Champagne',
        'Amber Champagne': 'Silver Amber Champagne',
        'Amber Cream Champagne': 'Silver Amber Cream Champagne',
        'Classic Cream Champagne': 'Silver Classic Cream Champagne',
    }

    # Apply silver mapping - sort by length (longest first) to avoid partial matches
    sorted_map = sorted(silver_map.items(), key=lambda x: len(x[0]), reverse=True)
    for base_color, silver_version in sorted_map:
        if base_color in ctx.phenotype:
            ctx.phenotype = ctx.phenotype.replace(base_color, silver_version)
            return

    # Fallback for black/bay/seal brown containing phenotypes
    if any(keyword in ctx.phenotype.lower() for keyword in ['bay', 'black', 'classic', 'amber', 'seal', 'brown']):
        ctx.phenotype = f"Silver {ctx.phenotype}"


def apply_dun(ctx: PhenotypeContext) -> None:
    """
    Apply dun notation to phenotype.

    Dun (TBX3 gene) creates dilution with primitive markings.

    Uses industry-standard names (e.g., Grullo, Red Dun, Dunalino)
    with genetic descriptions in parentheses.

    Modifies ctx.phenotype
    """
    if ctx.has_allele('dun', 'D'):
        # Apply dun and use industry-standard names where applicable
        genetic_description = f"{ctx.phenotype} Dun"

        # Map common dun colors to industry-standard names
        # Format: "Industry Name (Genetic Description)"
        dun_name_map = {
            # Basic dun colors
            'Black Dun': 'Grullo (Black Dun)',
            'Chestnut Dun': 'Red Dun (Chestnut Dun)',
            'Palomino Dun': 'Dunalino (Palomino Dun)',
            'Buckskin Dun': 'Dunskin (Buckskin Dun)',
            'Smoky Black Dun': 'Smoky Grullo (Smoky Black Dun)',

            # Silver variants
            'Silver Black Dun': 'Silver Grullo (Silver Black Dun)',
            'Silver Bay Dun': 'Silver Bay Dun',

            # Sooty variants
            'Sooty Black Dun': 'Sooty Grullo (Sooty Black Dun)',
            'Sooty Chestnut Dun': 'Sooty Red Dun (Sooty Chestnut Dun)',
            'Sooty Bay Dun': 'Sooty Bay Dun',
            'Sooty Palomino Dun': 'Sooty Dunalino (Sooty Palomino Dun)',
            'Sooty Buckskin Dun': 'Sooty Dunskin (Sooty Buckskin Dun)',

            # Flaxen variants
            'Chestnut Dun with Flaxen': 'Red Dun with Flaxen (Chestnut Dun with Flaxen)',
            'Palomino Dun with Flaxen': 'Dunalino with Flaxen (Palomino Dun with Flaxen)',
            'Sooty Chestnut Dun with Flaxen': 'Sooty Red Dun with Flaxen (Sooty Chestnut Dun with Flaxen)',

            # Champagne variants (already industry standard)
            'Classic Champagne Dun': 'Classic Champagne Dun',
            'Gold Champagne Dun': 'Gold Champagne Dun',
            'Amber Champagne Dun': 'Amber Champagne Dun',
        }

        # Check if we have an industry name mapping
        if genetic_description in dun_name_map:
            ctx.phenotype = dun_name_map[genetic_description]
        else:
            # For colors without special industry names, just add "Dun"
            ctx.phenotype = genetic_description

    elif ctx.has_allele('dun', 'nd1') and not ctx.has_allele('dun', 'D'):
        ctx.phenotype = f"{ctx.phenotype} (nd1)"


def apply_flaxen(ctx: PhenotypeContext) -> None:
    """
    Apply flaxen notation to phenotype.

    Flaxen lightens mane and tail on chestnut horses only.
    Only visible on e/e (chestnut base) with f/f genotype.

    Handles both simple names and industry names with genetic descriptions.

    Modifies ctx.phenotype
    """
    extension = ctx.get_genotype('extension')
    flaxen = ctx.get_genotype('flaxen')

    # Only visible on chestnut (e/e) with homozygous flaxen (f/f)
    if extension == ('e', 'e') and flaxen == ('f', 'f'):
        # If phenotype has format "Industry Name (Genetic Description)",
        # add "with Flaxen" to both parts
        if '(' in ctx.phenotype and ')' in ctx.phenotype:
            # Split into industry name and genetic description
            parts = ctx.phenotype.split('(', 1)
            industry_name = parts[0].strip()
            genetic_desc = parts[1].rstrip(')')

            ctx.phenotype = f"{industry_name} with Flaxen ({genetic_desc} with Flaxen)"
        else:
            # Simple format, just append
            ctx.phenotype = f"{ctx.phenotype} with Flaxen"


def apply_sooty(ctx: PhenotypeContext) -> None:
    """
    Apply sooty notation to phenotype.

    Sooty adds darker (black) hairs to red/pheomelanin pigment.
    It is NOT visible on:
    - Fully black horses (no red pigment to darken)
    - Double cream dilutes (nearly white, sooty effect invisible)

    Modifies ctx.phenotype
    """
    if not ctx.has_allele('sooty', 'STY'):
        return

    # Sooty NEVER affects pure black base colors
    # (no red pigment to add darker hairs to)
    if ctx.base_color == 'black':
        return

    # Sooty is not visible on double cream dilutes because the pigment is too diluted
    double_dilutes = ('Cremello', 'Perlino', 'Smoky Cream',
                      'Seal Perlino', 'Seal Pearl')
    if ctx.phenotype in double_dilutes:
        return

    # Sooty is visible on bay and chestnut bases (they have red pigment)
    ctx.phenotype = f"Sooty {ctx.phenotype}"


def apply_gray(ctx: PhenotypeContext) -> None:
    """
    Apply gray notation to phenotype.

    Gray (STX17 gene) causes progressive graying with age.
    Gray is epistatic over all other colors - horse will eventually become gray/white.
    Horse is born with its base color and progressively lightens.

    Modifies ctx.phenotype
    """
    if ctx.has_allele('gray', 'G'):
        ctx.phenotype = f"{ctx.phenotype} (Gray - will lighten with age)"


def apply_roan(ctx: PhenotypeContext) -> None:
    """
    Apply roan pattern to phenotype.

    Roan (KIT gene) adds white hairs evenly distributed through coat.
    Pattern does not change with age (unlike Gray).

    NOTE: Historically thought to be lethal when homozygous, but recent
    research (2020) on Icelandic horses shows Rn/Rn is viable.

    Modifies ctx.phenotype
    """
    if ctx.has_allele('roan', 'Rn'):
        ctx.phenotype = f"{ctx.phenotype} Roan"


def apply_dominant_white(ctx: PhenotypeContext) -> None:
    """
    Apply Dominant White pattern.

    Dominant White is caused by mutations in the KIT gene (W1-W39 alleles exist).
    Most W alleles are LETHAL when homozygous, except W20.

    Lethal combinations:
    - W1/W1, W5/W5, W10/W10, W13/W13, W22/W22 = embryonic lethal
    - W20/W20 = viable (rare exception)

    Modifies ctx.phenotype
    """
    # Check if horse has any W allele
    w_alleles = ['W1', 'W5', 'W10', 'W13', 'W20', 'W22']
    has_w = any(ctx.has_allele('dominant_white', allele) for allele in w_alleles)

    if not has_w:
        return

    # Get genotype to check for lethal homozygous combinations
    dw_genotype = ctx.get_genotype('dominant_white')

    # Check for lethal homozygous combinations (uses shared constant)
    from genetics.gene_definitions import LETHAL_COMBINATIONS
    dw_lethals = LETHAL_COMBINATIONS['dominant_white']['genotypes']
    if dw_genotype in dw_lethals:
        ctx.phenotype = f"NONVIABLE - Homozygous Dominant White ({dw_genotype[0]}/{dw_genotype[1]}) is lethal"
        return

    # W20/W20 is viable but causes maximum white
    if dw_genotype == ('W20', 'W20'):
        ctx.phenotype = f"Dominant White (Homozygous {dw_genotype[0]})"
        return

    # Heterozygous W alleles cause white/mostly white
    # Identify which W allele is present
    w_allele = None
    for allele in w_alleles:
        if ctx.has_allele('dominant_white', allele):
            w_allele = allele
            break

    if w_allele:
        ctx.phenotype = f"Dominant White ({w_allele})"


def apply_white_patterns(ctx: PhenotypeContext) -> None:
    """
    Apply white spotting patterns (Tobiano, Overo, Sabino, Splash).

    Handles special cases:
    - Tovero: Combination of Tobiano + any Overo pattern
    - Frame Overo O/O is LETHAL (Lethal White Overo Syndrome)

    Uses industry-standard terminology.

    Modifies ctx.phenotype
    """
    # Check for lethal Frame Overo homozygous (uses shared constant)
    from genetics.gene_definitions import LETHAL_COMBINATIONS
    frame_genotype = ctx.get_genotype('frame')
    if frame_genotype in LETHAL_COMBINATIONS['frame']['genotypes']:
        ctx.phenotype = "NONVIABLE - Homozygous Frame Overo (O/O) - Lethal White Overo Syndrome (LWOS)"
        return

    # Collect which patterns are present
    has_tobiano = ctx.has_allele('tobiano', 'To')
    has_frame = ctx.has_allele('frame', 'O')
    has_sabino = ctx.has_allele('sabino', 'Sb1')
    has_splash = ctx.has_allele('splash', 'Sw1') or ctx.has_allele('splash', 'Sw2') or ctx.has_allele('splash', 'Sw3')

    # Count overo-type patterns (Frame, Sabino, Splash)
    overo_patterns = []
    if has_frame:
        overo_patterns.append('Frame')
    if has_sabino:
        sabino_genotype = ctx.get_genotype('sabino')
        if sabino_genotype == ('Sb1', 'Sb1'):
            overo_patterns.append('Maximum Sabino')
        else:
            overo_patterns.append('Sabino')
    if has_splash:
        overo_patterns.append('Splash White')

    # Tovero: Tobiano + any Overo pattern
    if has_tobiano and len(overo_patterns) > 0:
        ctx.phenotype = f"{ctx.phenotype} Tovero"
        return

    # Just Tobiano
    if has_tobiano:
        ctx.phenotype = f"{ctx.phenotype} Tobiano"
        return

    # Overo patterns (without Tobiano)
    if len(overo_patterns) > 0:
        # If multiple overo patterns, list them
        if len(overo_patterns) == 1:
            ctx.phenotype = f"{ctx.phenotype} {overo_patterns[0]}"
        else:
            overo_str = ' + '.join(overo_patterns)
            ctx.phenotype = f"{ctx.phenotype} {overo_str}"


def apply_leopard_complex(ctx: PhenotypeContext) -> None:
    """
    Apply Leopard Complex (Appaloosa) patterns.

    Patterns depend on Lp and PATN1 genes:
    - Lp/Lp + PATN1 = Leopard (white with colored spots all over)
    - Lp/Lp without PATN1 = Fewspot/Snowcap (mostly white)
    - Lp/lp + PATN1 = Leopard pattern (fewer spots)
    - Lp/lp without PATN1 = Blanket/Snowflake

    Uses industry-standard Appaloosa terminology.

    Modifies ctx.phenotype
    """
    if not ctx.has_allele('leopard', 'Lp'):
        return

    lp_count = ctx.count_alleles('leopard', 'Lp')
    has_patn1 = ctx.has_allele('patn1', 'PATN1')

    # Homozygous Lp/Lp
    if lp_count == 2:
        if has_patn1:
            ctx.phenotype = f"{ctx.phenotype} Leopard"
        else:
            ctx.phenotype = f"{ctx.phenotype} Fewspot"

    # Heterozygous Lp/lp
    else:
        if has_patn1:
            ctx.phenotype = f"{ctx.phenotype} Leopard"
        else:
            ctx.phenotype = f"{ctx.phenotype} Blanket"


# ============================================================================
# PHENOTYPE CALCULATOR - Main class using modifier pipeline
# ============================================================================

class PhenotypeCalculator:
    """
    Calculates phenotypes (coat colors) from genotypes.

    Uses a modular pipeline of modifiers for extensibility.
    """

    def __init__(self, registry: GeneRegistry = None):
        """
        Initialize calculator with gene registry.

        Args:
            registry: Gene registry to use. If None, uses default.
        """
        from genetics.gene_registry import get_default_registry
        self.registry = registry or get_default_registry()

        # Define the phenotype determination pipeline
        # Modifiers are applied in order
        self.pipeline: List[Callable[[PhenotypeContext], None]] = [
            determine_base_color,  # Must be first
            apply_dilution,
            apply_champagne,
            apply_silver,
            apply_dun,
            apply_flaxen,
            apply_sooty,
            apply_roan,  # Apply before white patterns
            apply_dominant_white,  # Dominant White (usually overrides base color completely)
            apply_white_patterns,  # Tobiano, Overo, Sabino, Splash, Tovero
            apply_leopard_complex,  # Appaloosa patterns
            apply_gray,  # Usually last (epistatic)
        ]

    def determine_phenotype(self, genotype: Dict[str, Tuple[str, str]]) -> str:
        """
        Determine the phenotype (coat color name) from complete genotype.

        Args:
            genotype: Dictionary containing all genes

        Returns:
            str: Phenotype name (e.g., "Palomino", "Silver Bay Dun")
        """
        # Create context
        ctx = PhenotypeContext(genotype, self.registry)

        # Run through pipeline
        for modifier in self.pipeline:
            modifier(ctx)

        return ctx.phenotype

    def add_modifier(
        self,
        modifier: Callable[[PhenotypeContext], None],
        position: int = -1
    ) -> None:
        """
        Add a custom phenotype modifier to the pipeline.

        Useful for extending the system with new genes or interactions.

        Args:
            modifier: Function that takes PhenotypeContext and modifies it
            position: Where to insert (-1 = append to end)
        """
        if position == -1:
            self.pipeline.append(modifier)
        else:
            self.pipeline.insert(position, modifier)

    def remove_modifier(self, modifier: Callable[[PhenotypeContext], None]) -> None:
        """
        Remove a modifier from the pipeline.

        Args:
            modifier: Modifier function to remove
        """
        if modifier in self.pipeline:
            self.pipeline.remove(modifier)
