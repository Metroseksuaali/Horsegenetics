#!/usr/bin/env python3
"""
Horse Coat Color Genetics Generator
Generates random horse genotypes and determines phenotypes based on
Extension, Agouti, Dilution (Cream/Pearl), Dun, Silver, and Sooty genes.

Note: Cream and Pearl are alleles of the same gene (SLC45A2), not separate genes.
This has been corrected for biological accuracy.
"""

import random
import itertools


class HorseGeneticGenerator:
    """Generates random horse genetics and determines coat color phenotype."""

    def __init__(self):
        # Define possible alleles for each gene
        self.extension_alleles = ['E', 'e']
        self.agouti_alleles = ['A', 'a']
        # CORRECTED: Cream and Pearl are alleles of the SAME gene (SLC45A2)
        self.dilution_alleles = ['N', 'Cr', 'Prl']  # N = wild-type, Cr = cream, Prl = pearl
        self.dun_alleles = ['D', 'nd1', 'nd2']   # D = dun, nd1 = non-dun1, nd2 = non-dun2
        self.silver_alleles = ['Z', 'n']         # Z = silver, n = non-silver
        # Champagne gene (SLC36A1) - dilutes both red and black pigment
        self.champagne_alleles = ['Ch', 'n']     # Ch = champagne (dominant), n = non-champagne
        # Flaxen gene - lightens mane/tail on chestnuts only
        # Note: Genetic basis unknown (suspected polygenic); simplified as single recessive
        self.flaxen_alleles = ['F', 'f']         # F = non-flaxen, f = flaxen (only visible on e/e)
        # Note: Sooty is simplified - in reality it's polygenic (multiple genes)
        self.sooty_alleles = ['STY', 'sty']      # STY = sooty, sty = non-sooty

    def generate_genotype(self):
        """Generate random genotype for all eight genes."""
        extension = self._random_pair(self.extension_alleles)
        agouti = self._random_pair(self.agouti_alleles)
        dilution = self._random_pair(self.dilution_alleles)
        dun = self._random_pair(self.dun_alleles)
        silver = self._random_pair(self.silver_alleles)
        champagne = self._random_pair(self.champagne_alleles)
        flaxen = self._random_pair(self.flaxen_alleles)
        sooty = self._random_pair(self.sooty_alleles)

        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            'dun': dun,
            'silver': silver,
            'champagne': champagne,
            'flaxen': flaxen,
            'sooty': sooty
        }

    def _random_pair(self, alleles):
        """Generate a random pair of alleles."""
        allele1 = random.choice(alleles)
        allele2 = random.choice(alleles)
        return self._sort_alleles([allele1, allele2])

    def _sort_alleles(self, allele_list):
        """Sort alleles by dominance for consistent display."""
        dominance_order = {
            'E': 10, 'e': 1,
            'A': 10, 'a': 1,
            'N': 10, 'Cr': 5, 'Prl': 3,
            'D': 10, 'nd1': 5, 'nd2': 1,
            'Z': 10, 'n': 1,
            'Ch': 10, 'n': 1,  # Note: 'n' used for both silver and champagne wild-type
            'F': 10, 'f': 1,
            'STY': 10, 'sty': 1
        }

        sorted_alleles = sorted(allele_list, key=lambda x: dominance_order.get(x, 0), reverse=True)
        return tuple(sorted_alleles)

    def determine_base_color(self, extension, agouti):
        """Determine base coat color from Extension and Agouti genes."""
        if extension == ('e', 'e'):
            return 'chestnut'

        if 'A' in agouti:
            return 'bay'
        else:
            return 'black'

    def count_alleles(self, genotype, allele):
        """Count copies of a specific allele in a genotype."""
        return genotype.count(allele)

    def determine_phenotype(self, genotype):
        """Determine the phenotype (coat color name) from genotype."""
        extension = genotype['extension']
        agouti = genotype['agouti']
        dilution = genotype['dilution']
        dun = genotype['dun']
        silver = genotype['silver']
        champagne = genotype['champagne']
        flaxen = genotype['flaxen']
        sooty = genotype['sooty']

        base_color = self.determine_base_color(extension, agouti)

        cr_count = self.count_alleles(dilution, 'Cr')
        prl_count = self.count_alleles(dilution, 'Prl')

        has_champagne = 'Ch' in champagne
        has_silver = 'Z' in silver
        has_dun = 'D' in dun
        has_nd1 = 'nd1' in dun and 'D' not in dun
        has_flaxen = (extension == ('e', 'e') and flaxen == ('f', 'f'))
        has_sooty = 'STY' in sooty

        phenotype = self._apply_dilution(base_color, cr_count, prl_count)

        if has_champagne:
            phenotype = self._apply_champagne(phenotype, base_color)

        if has_silver and base_color != 'chestnut':
            phenotype = self._apply_silver(phenotype, base_color)

        if has_dun:
            phenotype = f"{phenotype} Dun"
        elif has_nd1:
            phenotype = f"{phenotype} (nd1)"

        if has_flaxen:
            phenotype = f"{phenotype} with Flaxen"

        if has_sooty:
            phenotype = f"Sooty {phenotype}"

        return phenotype

    def _apply_dilution(self, base_color, cr_count, prl_count):
        """
        Apply dilution based on SLC45A2 genotype.

        Genotypes and effects:
        - N/N: No dilution
        - N/Cr: Single cream dilution (Palomino, Buckskin, Smoky Black)
        - Cr/Cr: Double cream dilution (Cremello, Perlino, Smoky Cream)
        - N/Prl: Pearl carrier (no visible effect)
        - Prl/Prl: Double pearl dilution (Apricot, Pearl Bay, Pearl Black)
        - Cr/Prl: Compound heterozygote (pseudo-double dilute effect)

        Note: Cream is incomplete dominant, Pearl is recessive.
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
                return 'Pearl Black'

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
        Champagne dilutes both eumelanin (black) and pheomelanin (red).
        Gold Champagne = chestnut base
        Amber Champagne = bay base
        Classic Champagne = black base
        """
        champagne_map = {
            'Cremello': 'Ivory Champagne',
            'Perlino': 'Amber Cream Champagne',
            'Smoky Cream': 'Classic Cream Champagne',
            'Palomino': 'Gold Cream Champagne',
            'Buckskin': 'Amber Cream Champagne',
            'Smoky Black': 'Classic Cream Champagne',
            'Pseudo-Cremello': 'Ivory Pearl Champagne',
            'Pseudo-Perlino': 'Amber Pearl Champagne',
            'Pseudo-Smoky Cream': 'Classic Pearl Champagne',
            'Apricot': 'Gold Pearl Champagne',
            'Pearl Bay': 'Amber Pearl Champagne',
            'Pearl Black': 'Classic Pearl Champagne',
            'Chestnut': 'Gold Champagne',
            'Bay': 'Amber Champagne',
            'Black': 'Classic Champagne',
        }

        # Check if phenotype contains any of these base colors
        for base, champ_version in champagne_map.items():
            if base in phenotype:
                return phenotype.replace(base, champ_version)

        # Fallback - add Champagne prefix
        return f"Champagne {phenotype}"

    def _apply_silver(self, phenotype, base_color):
        """Apply silver dilution to phenotype (only affects eumelanin/black)."""
        # Silver dilutes black pigment, especially in mane and tail
        silver_map = {
            'Pseudo-Cremello': 'Silver Pseudo-Cremello',
            'Pseudo-Perlino': 'Silver Pseudo-Perlino',
            'Pseudo-Smoky Cream': 'Silver Pseudo-Smoky Cream',
            'Black': 'Silver Black',
            'Bay': 'Silver Bay',
            'Smoky Black': 'Silver Smoky Black',
            'Buckskin': 'Silver Buckskin',
            'Perlino': 'Silver Perlino',
            'Smoky Cream': 'Silver Smoky Cream',
            'Pearl Bay': 'Silver Pearl Bay',
            'Pearl Black': 'Silver Pearl Black',
            # Champagne colors with black/bay base
            'Classic Champagne': 'Silver Classic Champagne',
            'Amber Champagne': 'Silver Amber Champagne',
            'Amber Cream Champagne': 'Silver Amber Cream Champagne',
            'Classic Cream Champagne': 'Silver Classic Cream Champagne',
        }

        for base, silver_version in silver_map.items():
            if base in phenotype:
                return phenotype.replace(base, silver_version)

        if 'bay' in phenotype.lower() or 'black' in phenotype.lower() or 'classic' in phenotype.lower() or 'amber' in phenotype.lower():
            return f"Silver {phenotype}"

        return phenotype

    def format_genotype(self, genotype):
        """Format genotype for display."""
        ext = '/'.join(genotype['extension'])
        ag = '/'.join(genotype['agouti'])
        dil = '/'.join(genotype['dilution'])
        dn = '/'.join(genotype['dun'])
        slv = '/'.join(genotype['silver'])
        ch = '/'.join(genotype['champagne'])
        fl = '/'.join(genotype['flaxen'])
        sty = '/'.join(genotype['sooty'])

        return f"E: {ext}  A: {ag}  Dil: {dil}  D: {dn}  Z: {slv}  Ch: {ch}  F: {fl}  STY: {sty}"

    def generate_horse(self):
        """Generate a complete random horse with genotype and phenotype."""
        genotype = self.generate_genotype()
        phenotype = self.determine_phenotype(genotype)

        return {
            'genotype': genotype,
            'phenotype': phenotype
        }

    def breed_horses(self, parent1_genotype, parent2_genotype):
        """
        Breed two horses and return the offspring genotype.
        Each parent passes one random allele from each gene to offspring.
        Follows Mendelian inheritance.
        """
        offspring_genotype = {}

        for gene in ['extension', 'agouti', 'dilution', 'dun', 'silver', 'champagne', 'flaxen', 'sooty']:
            allele_from_parent1 = random.choice(parent1_genotype[gene])
            allele_from_parent2 = random.choice(parent2_genotype[gene])

            offspring_genotype[gene] = self._sort_alleles([allele_from_parent1, allele_from_parent2])

        return offspring_genotype

    def parse_genotype_input(self, genotype_str):
        """
        Parse user input genotype string.
        Expected format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty
        Note: Dil (dilution) contains N, Cr, and Prl alleles (same gene).
        """
        genotype = {}

        try:
            parts = genotype_str.strip().split()

            for part in parts:
                if ':' not in part:
                    continue

                gene_label, alleles_str = part.split(':', 1)
                alleles = alleles_str.split('/')

                if len(alleles) != 2:
                    raise ValueError(f"Each gene must have exactly 2 alleles: {part}")

                gene_map = {
                    'E': 'extension',
                    'A': 'agouti',
                    'Dil': 'dilution',
                    'D': 'dun',
                    'Z': 'silver',
                    'Ch': 'champagne',
                    'F': 'flaxen',
                    'STY': 'sooty'
                }

                if gene_label not in gene_map:
                    raise ValueError(f"Unknown gene label: {gene_label}")

                gene_name = gene_map[gene_label]
                genotype[gene_name] = self._sort_alleles(alleles)

            required_genes = ['extension', 'agouti', 'dilution', 'dun', 'silver', 'champagne', 'flaxen', 'sooty']
            for gene in required_genes:
                if gene not in genotype:
                    raise ValueError(f"Missing gene: {gene}")

            return genotype

        except Exception as e:
            raise ValueError(f"Error parsing genotype: {e}")


def print_horse(generator, horse, title="HORSE"):
    """Print a horse's genotype and phenotype."""
    print(f"\n{title}:")
    print(f"  GENOTYPE: {generator.format_genotype(horse['genotype'])}")
    print(f"  PHENOTYPE: {horse['phenotype']}")


def main():
    """Main function to run the horse genetics generator."""
    print("=" * 80)
    print("              HORSE COAT COLOR GENETICS GENERATOR")
    print("=" * 80)
    print()

    generator = HorseGeneticGenerator()

    while True:
        print("\nChoose an option:")
        print("  1. Generate a random horse")
        print("  2. Breed two horses (manual genotype input)")
        print("  3. Exit")
        print()

        choice = input("Enter your choice (1-3): ").strip()

        if choice == '1':
            print("\n" + "=" * 80)
            print("Generating random horse...\n")

            horse = generator.generate_horse()
            print_horse(generator, horse, "GENERATED HORSE")
            print("=" * 80)

        elif choice == '2':
            print("\n" + "=" * 80)
            print("BREEDING TWO HORSES")
            print("=" * 80)
            print("\nEnter genotypes in format:")
            print("E:E/e A:A/a Dil:N/Cr D:D/nd2 Z:n/n Ch:n/n F:F/f STY:STY/sty")
            print("\nAllele options:")
            print("  E: E, e")
            print("  A: A, a")
            print("  Dil: N, Cr, Prl  (Note: Cream and Pearl are in the same gene)")
            print("  D: D, nd1, nd2")
            print("  Z: Z, n")
            print("  Ch: Ch, n  (Champagne - dilutes both red and black)")
            print("  F: F, f  (Flaxen - lightens mane/tail on chestnuts only)")
            print("  STY: STY, sty")
            print()

            try:
                parent1_input = input("Parent 1 genotype: ").strip()
                if not parent1_input:
                    print("Error: Empty input. Returning to menu.")
                    continue

                parent1_genotype = generator.parse_genotype_input(parent1_input)
                parent1 = {
                    'genotype': parent1_genotype,
                    'phenotype': generator.determine_phenotype(parent1_genotype)
                }

                parent2_input = input("Parent 2 genotype: ").strip()
                if not parent2_input:
                    print("Error: Empty input. Returning to menu.")
                    continue

                parent2_genotype = generator.parse_genotype_input(parent2_input)
                parent2 = {
                    'genotype': parent2_genotype,
                    'phenotype': generator.determine_phenotype(parent2_genotype)
                }

                print("\n" + "-" * 80)
                print_horse(generator, parent1, "PARENT 1")
                print_horse(generator, parent2, "PARENT 2")
                print("-" * 80)

                offspring_genotype = generator.breed_horses(parent1_genotype, parent2_genotype)
                offspring = {
                    'genotype': offspring_genotype,
                    'phenotype': generator.determine_phenotype(offspring_genotype)
                }

                print_horse(generator, offspring, "OFFSPRING")
                print("=" * 80)

            except ValueError as e:
                print(f"\nError: {e}")
                print("Please check your input format and try again.")

        elif choice == '3':
            print("\nThank you for using the Horse Genetics Generator!")
            break

        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
