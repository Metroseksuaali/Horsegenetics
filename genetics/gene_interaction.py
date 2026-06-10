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
        self.base_color: str = ""  # 'chestnut', 'bay', 'seal_brown' or 'black'
        self.phenotype: str = ""  # Current phenotype name (built incrementally)

        # Structured trait state, filled in by pipeline modifiers so later
        # modifiers can reason about traits without parsing phenotype strings
        self.cream_count: int = 0
        self.pearl_count: int = 0
        self.kit_has_tobiano: bool = False
        self.kit_has_sabino: bool = False
        self.kit_sabino_homozygous: bool = False

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


# Color names per (base color, dilution state): (plain name, champagne name).
# Single source of truth for the cream/pearl/champagne naming - replaces the
# old chain of string-replacement maps that was fragile to partial matches.
#
# Dilution states:
# - none:        N/N or N/Prl (single pearl has no visible effect)
# - cream1:      N/Cr (single cream)
# - cream2:      Cr/Cr (double cream)
# - pearl2:      Prl/Prl (double pearl)
# - cream_pearl: Cr/Prl (compound heterozygote, pseudo-double dilute)
BASE_DILUTION_NAMES: Dict[Tuple[str, str], Tuple[str, str]] = {
    ('chestnut', 'none'): ('Chestnut', 'Gold Champagne'),
    ('bay', 'none'): ('Bay', 'Amber Champagne'),
    ('seal_brown', 'none'): ('Seal Brown', 'Amber Champagne'),
    ('black', 'none'): ('Black', 'Classic Champagne'),

    ('chestnut', 'cream1'): ('Palomino', 'Gold Cream Champagne'),
    ('bay', 'cream1'): ('Buckskin', 'Amber Cream Champagne'),
    ('seal_brown', 'cream1'): ('Seal Buckskin', 'Amber Cream Champagne'),
    ('black', 'cream1'): ('Smoky Black', 'Classic Cream Champagne'),

    ('chestnut', 'cream2'): ('Cremello', 'Gold Cream Champagne'),
    ('bay', 'cream2'): ('Perlino', 'Perlino Champagne'),
    ('seal_brown', 'cream2'): ('Seal Perlino', 'Perlino Champagne'),
    ('black', 'cream2'): ('Smoky Cream', 'Smoky Cream Champagne'),

    ('chestnut', 'pearl2'): ('Apricot', 'Gold Pearl Champagne'),
    ('bay', 'pearl2'): ('Pearl Bay', 'Amber Pearl Champagne'),
    ('seal_brown', 'pearl2'): ('Seal Pearl', 'Amber Pearl Champagne'),
    ('black', 'pearl2'): ('Smoky Pearl', 'Classic Pearl Champagne'),

    ('chestnut', 'cream_pearl'): ('Palomino Pearl', 'Ivory Pearl Champagne'),
    ('bay', 'cream_pearl'): ('Buckskin Pearl', 'Amber Pearl Champagne'),
    ('seal_brown', 'cream_pearl'): ('Seal Buckskin Pearl', 'Amber Pearl Champagne'),
    ('black', 'cream_pearl'): ('Smoky Black Pearl', 'Classic Pearl Champagne'),
}


def _dilution_state(cream_count: int, pearl_count: int) -> str:
    """Map cream/pearl allele counts to a dilution state key."""
    if cream_count == 2:
        return 'cream2'
    if pearl_count == 2:
        return 'pearl2'
    if cream_count == 1 and pearl_count == 1:
        return 'cream_pearl'
    if cream_count == 1:
        return 'cream1'
    # N/N or N/Prl - single pearl is carrier-only, no visible effect
    return 'none'


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

    Stores cream/pearl counts on ctx and sets ctx.phenotype from
    BASE_DILUTION_NAMES.
    """
    ctx.cream_count = ctx.count_alleles('dilution', 'Cr')
    ctx.pearl_count = ctx.count_alleles('dilution', 'Prl')

    state = _dilution_state(ctx.cream_count, ctx.pearl_count)
    plain_name, _ = BASE_DILUTION_NAMES[(ctx.base_color, state)]
    ctx.phenotype = plain_name


def apply_champagne(ctx: PhenotypeContext) -> None:
    """
    Apply champagne dilution to phenotype.

    Champagne (SLC36A1 gene) dilutes both eumelanin (black) and
    pheomelanin (red) pigment.

    Color names:
    - Gold Champagne = chestnut base
    - Amber Champagne = bay base
    - Classic Champagne = black base

    Sets ctx.phenotype to the champagne name from BASE_DILUTION_NAMES.
    """
    if not ctx.has_allele('champagne', 'Ch'):
        return

    state = _dilution_state(ctx.cream_count, ctx.pearl_count)
    _, champagne_name = BASE_DILUTION_NAMES[(ctx.base_color, state)]
    ctx.phenotype = champagne_name


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

    # All other bases carry black pigment; runs before dun/patterns so the
    # phenotype is still a plain dilution/champagne name at this point
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


def apply_kit_gene(ctx: PhenotypeContext) -> None:
    """
    Apply KIT gene effects (Roan, Tobiano, Sabino, Dominant White).

    The KIT gene has multiple alleles on a single locus. A horse has exactly
    2 KIT alleles. Alleles: n, sb1, rn, to, W1, W5, W10, W13, W20, W22.

    Dominance: W alleles > to > rn > sb1 > n

    This means a horse CAN be tobiano + roan (KIT: to/rn) but CANNOT be
    tobiano + roan + sabino (would need 3 alleles — impossible).

    Modifies ctx.phenotype
    """
    kit_genotype = ctx.get_genotype('kit')
    allele1, allele2 = kit_genotype

    # Collect W alleles
    w_alleles_present = [a for a in kit_genotype if a.startswith('W')]

    # --- Dominant White handling (highest priority) ---
    if w_alleles_present:
        from genetics.gene_definitions import LETHAL_COMBINATIONS
        kit_lethals = LETHAL_COMBINATIONS['kit']['genotypes']

        # Check for lethal homozygous W combinations
        if kit_genotype in kit_lethals:
            ctx.phenotype = f"NONVIABLE - Homozygous Dominant White ({allele1}/{allele2}) is lethal"
            return

        # W20/W20 is viable but causes maximum white
        if kit_genotype == ('W20', 'W20'):
            ctx.phenotype = f"Dominant White (Homozygous {allele1})"
            return

        # Heterozygous or compound W — show dominant W allele
        # Pick the highest-priority W allele present
        w_allele = w_alleles_present[0]  # Already sorted by dominance
        ctx.phenotype = f"Dominant White ({w_allele})"
        return

    # --- Roan (applies before white pattern labels) ---
    has_roan = 'rn' in kit_genotype
    if has_roan:
        ctx.phenotype = f"{ctx.phenotype} Roan"

    # Store KIT pattern info for apply_white_patterns to use
    ctx.kit_has_tobiano = 'to' in kit_genotype
    ctx.kit_has_sabino = 'sb1' in kit_genotype
    ctx.kit_sabino_homozygous = (allele1 == 'sb1' and allele2 == 'sb1')


def apply_white_patterns(ctx: PhenotypeContext) -> None:
    """
    Apply white spotting patterns from KIT (Tobiano, Sabino) + Frame (EDNRB) + Splash (MITF).

    Handles special cases:
    - Tovero: Combination of Tobiano (KIT) + any Overo pattern (Frame/Splash)
    - Frame Overo O/O is LETHAL (Lethal White Overo Syndrome)
    - Sabino from KIT gene

    Uses industry-standard terminology.

    Modifies ctx.phenotype
    """
    # Check for lethal Frame Overo homozygous (uses shared constant)
    from genetics.gene_definitions import LETHAL_COMBINATIONS
    frame_genotype = ctx.get_genotype('frame')
    if frame_genotype in LETHAL_COMBINATIONS['frame']['genotypes']:
        ctx.phenotype = "NONVIABLE - Homozygous Frame Overo (O/O) - Lethal White Overo Syndrome (LWOS)"
        return

    # Get KIT pattern info (set by apply_kit_gene)
    has_tobiano = ctx.kit_has_tobiano
    has_sabino = ctx.kit_has_sabino
    sabino_homozygous = ctx.kit_sabino_homozygous

    # Frame and Splash are on separate genes (EDNRB and MITF)
    has_frame = ctx.has_allele('frame', 'O')
    has_splash = ctx.has_allele('splash', 'Sw1') or ctx.has_allele('splash', 'Sw2') or ctx.has_allele('splash', 'Sw3')

    # Count overo-type patterns (Frame, Sabino, Splash)
    overo_patterns = []
    if has_frame:
        overo_patterns.append('Frame')
    if has_sabino:
        if sabino_homozygous:
            overo_patterns.append('Maximum Sabino')
        else:
            overo_patterns.append('Sabino')
    if has_splash:
        overo_patterns.append('Splash White')

    # Tovero: Tobiano + any Overo pattern (Frame or Splash — NOT sabino from same KIT)
    # Note: Sabino from KIT is on the same allele pair as tobiano, so a horse
    # with to/sb1 shows both patterns. We treat Frame/Splash combos as Tovero
    # since they come from different genes.
    non_kit_overo = []
    if has_frame:
        non_kit_overo.append('Frame')
    if has_splash:
        non_kit_overo.append('Splash White')

    if has_tobiano and len(non_kit_overo) > 0:
        ctx.phenotype = f"{ctx.phenotype} Tovero"
        return

    # Just Tobiano (possibly with Sabino from KIT — show both)
    if has_tobiano:
        if has_sabino:
            # to/sb1 — both patterns expressed
            if sabino_homozygous:
                ctx.phenotype = f"{ctx.phenotype} Tobiano Maximum Sabino"
            else:
                ctx.phenotype = f"{ctx.phenotype} Tobiano Sabino"
        else:
            ctx.phenotype = f"{ctx.phenotype} Tobiano"
        return

    # Overo patterns (without Tobiano)
    if len(overo_patterns) > 0:
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
            apply_kit_gene,  # KIT: Roan, Dominant White, sets up Tobiano/Sabino flags
            apply_white_patterns,  # Tobiano, Sabino (KIT) + Frame (EDNRB), Splash (MITF), Tovero
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
