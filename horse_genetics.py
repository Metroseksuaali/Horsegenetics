#!/usr/bin/env python3
"""
Horse Coat Color Genetics Generator - CLI Version

Generates random horse genotypes and determines phenotypes based on
Extension, Agouti, Dilution (Cream/Pearl), Dun, Silver, Champagne,
Flaxen, and Sooty genes.

This is the command-line interface. The genetics logic is in the
'genetics' module for better organization and scalability.
"""

from genetics import BreedingSimulator, PhenotypeCalculator


class HorseGeneticGenerator:
    """
    Wrapper class for backwards compatibility.

    This class maintains the same interface as before but delegates
    to the new modular genetics system.
    """

    def __init__(self):
        """Initialize with breeding simulator and phenotype calculator."""
        self.breeding_sim = BreedingSimulator()
        self.phenotype_calc = PhenotypeCalculator()

    def generate_genotype(self):
        """Generate random genotype for all eight genes."""
        return self.breeding_sim.gene_pool.generate_random_genotype()

    def determine_phenotype(self, genotype):
        """Determine the phenotype (coat color name) from genotype."""
        return self.phenotype_calc.determine_phenotype(genotype)

    def determine_base_color(self, extension, agouti):
        """Determine base coat color from Extension and Agouti genes."""
        return self.breeding_sim.gene_pool.determine_base_color(extension, agouti)

    def count_alleles(self, genotype, allele):
        """Count copies of a specific allele in a genotype."""
        return self.breeding_sim.gene_pool.count_alleles(genotype, allele)

    def format_genotype(self, genotype):
        """Format genotype for display."""
        return self.phenotype_calc.format_genotype(genotype)

    def format_genotype_detailed(self, genotype):
        """Format genotype with detailed gene names for display."""
        return self.phenotype_calc.format_genotype_detailed(genotype)

    def generate_horse(self):
        """Generate a complete random horse with genotype and phenotype."""
        return self.breeding_sim.generate_random_horse()

    def breed_horses(self, parent1_genotype, parent2_genotype):
        """
        Breed two horses and return the offspring genotype.
        Follows Mendelian inheritance.
        """
        return self.breeding_sim.breed_horses(parent1_genotype, parent2_genotype)

    def parse_genotype_input(self, genotype_str):
        """
        Parse user input genotype string.
        Expected format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty
        """
        return self.breeding_sim.parse_genotype_input(genotype_str)


def print_horse(generator, horse, title="HORSE"):
    """Print a horse's genotype and phenotype."""
    print(f"\n{title}:")
    print(f"  GENOTYPE: {generator.format_genotype(horse['genotype'])}")
    print(f"  PHENOTYPE: {horse['phenotype']}")


def main():
    """Main function for CLI interface."""
    generator = HorseGeneticGenerator()

    print("=" * 60)
    print("HORSE COAT COLOR GENETICS SIMULATOR")
    print("=" * 60)
    print("\nThis simulator models 8 genetic traits:")
    print("  1. Extension (E/e) - Black or red pigment")
    print("  2. Agouti (A/a) - Bay or black distribution")
    print("  3. Dilution (N/Cr/Prl) - Cream and Pearl dilutions")
    print("  4. Dun (D/nd1/nd2) - Dun dilution with primitive markings")
    print("  5. Silver (Z/n) - Lightens black pigment")
    print("  6. Champagne (Ch/n) - Lightens both red and black pigment")
    print("  7. Flaxen (F/f) - Lightens mane/tail on chestnuts only")
    print("  8. Sooty (STY/sty) - Adds darker hairs")

    while True:
        print("\n" + "=" * 60)
        print("MENU:")
        print("  1. Generate a random horse")
        print("  2. Breed two horses")
        print("  3. Exit")
        print("=" * 60)

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '1':
            horse = generator.generate_horse()
            print_horse(generator, horse, "RANDOMLY GENERATED HORSE")

        elif choice == '2':
            print("\n" + "-" * 60)
            print("BREEDING SIMULATOR")
            print("-" * 60)
            print("\nEnter genotypes for two parent horses.")
            print("Format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty")
            print("\nExample: E:E/e A:A/a Dil:N/Cr D:nd1/nd2 Z:n/n Ch:n/n F:F/f STY:STY/sty")

            try:
                print("\n--- PARENT 1 (Sire) ---")
                parent1_str = input("Enter genotype: ").strip()
                parent1_geno = generator.parse_genotype_input(parent1_str)
                parent1_pheno = generator.determine_phenotype(parent1_geno)
                print(f"  PHENOTYPE: {parent1_pheno}")

                print("\n--- PARENT 2 (Dam) ---")
                parent2_str = input("Enter genotype: ").strip()
                parent2_geno = generator.parse_genotype_input(parent2_str)
                parent2_pheno = generator.determine_phenotype(parent2_geno)
                print(f"  PHENOTYPE: {parent2_pheno}")

                offspring_geno = generator.breed_horses(parent1_geno, parent2_geno)
                offspring_pheno = generator.determine_phenotype(offspring_geno)

                print("\n" + "=" * 60)
                print("BREEDING RESULT:")
                print("=" * 60)
                print(f"\nParent 1 ({parent1_pheno})")
                print(f"  × Parent 2 ({parent2_pheno})")
                print(f"\n→ OFFSPRING:")
                print(f"  GENOTYPE: {generator.format_genotype(offspring_geno)}")
                print(f"  PHENOTYPE: {offspring_pheno}")

            except ValueError as e:
                print(f"\nError: {e}")
                print("Please check your genotype format and try again.")

        elif choice == '3':
            print("\nExiting simulator. Thank you!")
            break

        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == '__main__':
    main()
