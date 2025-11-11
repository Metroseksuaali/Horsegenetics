"""
Phenotype calculation module - Determines coat colors from genotypes

This module handles all phenotype (visible color) determination from genotypes.
Includes dilution effects, gene interactions, and color nomenclature.
"""

from genetics.core import GenePool


class PhenotypeCalculator:
    """
    Calculates phenotypes (coat colors) from genotypes.

    This class handles complex gene interactions and produces accurate
    color nomenclature following equine genetics standards.
    """

    def __init__(self):
        """Initialize with gene pool for base color determination."""
        self.gene_pool = GenePool()

    def determine_phenotype(self, genotype):
        """
        Determine the phenotype (coat color name) from complete genotype.

        Args:
            genotype: Dictionary containing all genes

        Returns:
            str: Phenotype name (e.g., "Palomino", "Silver Bay Dun")
        """
        extension = genotype['extension']
        agouti = genotype['agouti']
        dilution = genotype['dilution']
        dun = genotype['dun']
        silver = genotype['silver']
        champagne = genotype['champagne']
        flaxen = genotype['flaxen']
        sooty = genotype['sooty']

        # Determine base color (chestnut, bay, or black)
        base_color = self.gene_pool.determine_base_color(extension, agouti)

        # Count dilution alleles
        cr_count = self.gene_pool.count_alleles(dilution, 'Cr')
        prl_count = self.gene_pool.count_alleles(dilution, 'Prl')

        # Check for gene presence
        has_champagne = 'Ch' in champagne
        has_silver = 'Z' in silver
        has_dun = 'D' in dun
        has_nd1 = 'nd1' in dun and 'D' not in dun
        has_flaxen = (extension == ('e', 'e') and flaxen == ('f', 'f'))
        has_sooty = 'STY' in sooty

        # Apply dilutions in order
        phenotype = self._apply_dilution(base_color, cr_count, prl_count)

        if has_champagne:
            phenotype = self._apply_champagne(phenotype, base_color)

        if has_silver and base_color != 'chestnut':
            phenotype = self._apply_silver(phenotype, base_color)

        # Add dun notation
        if has_dun:
            phenotype = f"{phenotype} Dun"
        elif has_nd1:
            phenotype = f"{phenotype} (nd1)"

        # Add flaxen (only visible on chestnut base)
        if has_flaxen:
            phenotype = f"{phenotype} with Flaxen"

        # Add sooty (darkens coat with black hairs on red pigment)
        # Sooty is NOT visible on fully black horses (no red pigment to darken)
        if has_sooty:
            # Check if sooty is applicable to this phenotype
            if self._is_sooty_visible(phenotype, base_color):
                phenotype = f"Sooty {phenotype}"

        return phenotype

    def _is_sooty_visible(self, phenotype, base_color):
        """
        Determine if Sooty gene is visible on given phenotype.

        Sooty adds darker (black) hairs to red/pheomelanin pigment.
        It is NOT visible on fully black horses.

        Args:
            phenotype: Current phenotype string
            base_color: Original base color

        Returns:
            bool: True if sooty is visible
        """
        # Sooty does not affect fully black horses
        fully_black_colors = [
            'Black',
            'Smoky Black',
            'Smoky Cream',  # Double cream on black - nearly white
            'Classic Champagne'  # Black + champagne
        ]

        # Check if phenotype is fully black (excluding Dun/nd1 notation)
        phenotype_base = phenotype.split(' Dun')[0].split(' (nd1)')[0]

        for black_color in fully_black_colors:
            if phenotype_base == black_color:
                return False

        # Sooty is visible on colors with red pigment
        return True

    def _apply_dilution(self, base_color, cr_count, prl_count):
        """
        Apply dilution based on SLC45A2 genotype (Cream/Pearl gene).

        Genotypes and effects:
        - N/N: No dilution
        - N/Cr: Single cream (Palomino, Buckskin, Smoky Black)
        - Cr/Cr: Double cream (Cremello, Perlino, Smoky Cream)
        - N/Prl: Pearl carrier (no visible effect)
        - Prl/Prl: Double pearl (Apricot, Pearl Bay, Pearl Black)
        - Cr/Prl: Compound heterozygote (pseudo-double dilute)

        Note: Cream is incomplete dominant, Pearl is recessive.

        Args:
            base_color: Base coat color ('chestnut', 'bay', 'black')
            cr_count: Number of Cream alleles (0, 1, or 2)
            prl_count: Number of Pearl alleles (0, 1, or 2)

        Returns:
            str: Diluted color name
        """
        # Cr/Cr - Double cream dilution
        if cr_count == 2:
            if base_color == 'chestnut':
                return 'Cremello'
            elif base_color == 'bay':
                return 'Perlino'
            elif base_color == 'black':
                return 'Smoky Cream'

        # Prl/Prl - Double pearl dilution
        elif prl_count == 2:
            if base_color == 'chestnut':
                return 'Apricot'
            elif base_color == 'bay':
                return 'Pearl Bay'
            elif base_color == 'black':
                return 'Smoky Pearl'  # Fixed from "Pearl Black"

        # Cr/Prl - Compound heterozygote (pseudo-double dilute)
        elif cr_count == 1 and prl_count == 1:
            if base_color == 'chestnut':
                return 'Pseudo-Cremello'
            elif base_color == 'bay':
                return 'Pseudo-Perlino'
            elif base_color == 'black':
                return 'Pseudo-Smoky Cream'

        # N/Cr - Single cream dilution
        elif cr_count == 1:
            if base_color == 'chestnut':
                return 'Palomino'
            elif base_color == 'bay':
                return 'Buckskin'
            elif base_color == 'black':
                return 'Smoky Black'

        # N/Prl or N/N - No visible dilution
        else:
            return base_color.capitalize()

    def _apply_champagne(self, phenotype, base_color):
        """
        Apply champagne dilution to phenotype.

        Champagne (SLC36A1 gene) dilutes both eumelanin (black) and
        pheomelanin (red) pigment.

        Color names:
        - Gold Champagne = chestnut base
        - Amber Champagne = bay base
        - Classic Champagne = black base

        Args:
            phenotype: Current phenotype string
            base_color: Original base color

        Returns:
            str: Champagne-modified phenotype
        """
        champagne_map = {
            'Cremello': 'Gold Cream Champagne',  # Fixed from "Ivory Champagne"
            'Perlino': 'Perlino Champagne',  # Fixed from "Amber Cream Champagne"
            'Smoky Cream': 'Smoky Cream Champagne',  # Fixed
            'Palomino': 'Gold Cream Champagne',
            'Buckskin': 'Amber Cream Champagne',
            'Smoky Black': 'Classic Cream Champagne',
            'Pseudo-Cremello': 'Ivory Pearl Champagne',
            'Pseudo-Perlino': 'Amber Pearl Champagne',
            'Pseudo-Smoky Cream': 'Classic Pearl Champagne',
            'Apricot': 'Gold Pearl Champagne',
            'Pearl Bay': 'Amber Pearl Champagne',
            'Smoky Pearl': 'Classic Pearl Champagne',
            'Chestnut': 'Gold Champagne',
            'Bay': 'Amber Champagne',
            'Black': 'Classic Champagne',
        }

        # Check if phenotype contains any mapped colors
        for base, champ_version in champagne_map.items():
            if base in phenotype:
                return phenotype.replace(base, champ_version)

        # Fallback - add Champagne prefix
        return f"Champagne {phenotype}"

    def _apply_silver(self, phenotype, base_color):
        """
        Apply silver dilution to phenotype.

        Silver (PMEL17 gene) only affects eumelanin (black pigment).
        It lightens black pigment, especially in mane and tail.

        Does NOT affect:
        - Chestnut (no black pigment)

        NOTE: Silver DOES affect double cream dilutes (Perlino, Smoky Cream)
        even though the effect is subtle. It must be noted for genetic accuracy
        and breeding purposes.

        Args:
            phenotype: Current phenotype string
            base_color: Original base color

        Returns:
            str: Silver-modified phenotype (if applicable)
        """
        # Silver does not affect chestnut (no black pigment)
        if base_color == 'chestnut':
            return phenotype

        silver_map = {
            # Double cream dilutes - Silver still applies
            'Perlino': 'Silver Perlino',
            'Smoky Cream': 'Silver Smoky Cream',
            # Note: Cremello is chestnut-based, filtered above
            'Pseudo-Cremello': 'Silver Pseudo-Cremello',
            'Pseudo-Perlino': 'Silver Pseudo-Perlino',
            'Pseudo-Smoky Cream': 'Silver Pseudo-Smoky Cream',
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
        # E.g., "Smoky Black" must be checked before "Black" to get correct word order
        sorted_map = sorted(silver_map.items(), key=lambda x: len(x[0]), reverse=True)
        for base, silver_version in sorted_map:
            if base in phenotype:
                return phenotype.replace(base, silver_version)

        # Fallback for black/bay containing phenotypes
        if any(keyword in phenotype.lower() for keyword in ['bay', 'black', 'classic', 'amber']):
            return f"Silver {phenotype}"

        return phenotype

    def format_genotype(self, genotype):
        """
        Format genotype dictionary for display.

        Args:
            genotype: Complete genotype dictionary

        Returns:
            str: Formatted genotype string
        """
        ext = '/'.join(genotype['extension'])
        ag = '/'.join(genotype['agouti'])
        dil = '/'.join(genotype['dilution'])
        dn = '/'.join(genotype['dun'])
        slv = '/'.join(genotype['silver'])
        ch = '/'.join(genotype['champagne'])
        fl = '/'.join(genotype['flaxen'])
        sty = '/'.join(genotype['sooty'])

        return f"E: {ext}  A: {ag}  Dil: {dil}  D: {dn}  Z: {slv}  Ch: {ch}  F: {fl}  STY: {sty}"

    def format_genotype_detailed(self, genotype):
        """
        Format genotype with detailed gene names for display.

        Args:
            genotype: Complete genotype dictionary

        Returns:
            str: Detailed multi-line genotype string
        """
        lines = []
        lines.append(f"Extension (E):    {'/'.join(genotype['extension'])}")
        lines.append(f"Agouti (A):       {'/'.join(genotype['agouti'])}")
        lines.append(f"Dilution (Cr/Prl):{'/'.join(genotype['dilution'])}")
        lines.append(f"Dun (D):          {'/'.join(genotype['dun'])}")
        lines.append(f"Silver (Z):       {'/'.join(genotype['silver'])}")
        lines.append(f"Champagne (Ch):   {'/'.join(genotype['champagne'])}")
        lines.append(f"Flaxen (F):       {'/'.join(genotype['flaxen'])}")
        lines.append(f"Sooty (STY):      {'/'.join(genotype['sooty'])}")
        return '\n'.join(lines)
