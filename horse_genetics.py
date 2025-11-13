#!/usr/bin/env python3
"""
Horse Coat Color Genetics Generator - CLI Version

Generates random horse genotypes and determines phenotypes based on
Extension, Agouti, Dilution (Cream/Pearl), Dun, Silver, Champagne,
Flaxen, Sooty, and Gray genes.

This is the command-line interface using the new modular Horse API.
"""

from genetics.horse import Horse
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator

# For backwards compatibility with old code
from genetics import BreedingSimulator, PhenotypeCalculator as OldPhenotypeCalculator


class HorseGeneticGenerator:
    """
    Wrapper class for backwards compatibility.

    This class maintains the same interface as before but delegates
    to the new Horse API.
    """

    def __init__(self):
        """Initialize with new API components."""
        self.registry = get_default_registry()
        self.calculator = PhenotypeCalculator(self.registry)

        # Old API for backwards compatibility
        self.breeding_sim = BreedingSimulator()
        self.phenotype_calc = OldPhenotypeCalculator()

    def generate_genotype(self):
        """Generate random genotype for all genes."""
        return self.registry.generate_random_genotype()

    def determine_phenotype(self, genotype):
        """Determine the phenotype (coat color name) from genotype."""
        return self.calculator.determine_phenotype(genotype)

    def determine_base_color(self, extension, agouti):
        """Determine base coat color from Extension and Agouti genes."""
        return self.breeding_sim.gene_pool.determine_base_color(extension, agouti)

    def count_alleles(self, genotype, allele):
        """Count copies of a specific allele in a genotype."""
        return self.registry.count_alleles(genotype, allele)

    def format_genotype(self, genotype):
        """Format genotype for display."""
        return self.registry.format_genotype(genotype, compact=True)

    def format_genotype_detailed(self, genotype):
        """Format genotype with detailed gene names for display."""
        return self.registry.format_genotype(genotype, compact=False)

    def generate_horse(self):
        """Generate a complete random horse with genotype and phenotype."""
        horse = Horse.random(self.registry, self.calculator)
        return horse.to_dict()

    def breed_horses(self, parent1_genotype, parent2_genotype):
        """
        Breed two horses and return the offspring genotype.
        Follows Mendelian inheritance.
        """
        return self.registry.breed(parent1_genotype, parent2_genotype)

    def parse_genotype_input(self, genotype_str):
        """
        Parse user input genotype string.
        Expected format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty G:G/g
        """
        return self.registry.parse_genotype_string(genotype_str)

    def _sort_alleles(self, alleles):
        """
        Sort alleles by dominance for consistent display.

        This is a wrapper for backwards compatibility with GUI.
        """
        # Use first gene for sorting (they all work the same way)
        gene = self.registry.get_gene('extension')
        return gene.sort_alleles(alleles)


def print_horse(generator, horse, title="HORSE"):
    """Print a horse's genotype and phenotype."""
    print(f"\n{title}:")
    print(f"  GENOTYPE: {generator.format_genotype(horse['genotype'])}")
    print(f"  PHENOTYPE: {horse['phenotype']}")


def batch_generate(count: int):
    """Generate multiple random horses in batch mode."""
    from genetics.horse import Horse

    print(f"\nGenerating {count} random horses:\n")
    print("=" * 80)

    for i in range(1, count + 1):
        horse = Horse.random()
        print(f"{i:3d}. {horse.phenotype}")
        print(f"     Genotype: {horse.genotype_string}")
        print()


def show_phenotype(genotype_str: str):
    """Show phenotype for a given genotype string."""
    from genetics.horse import Horse

    try:
        horse = Horse.from_string(genotype_str)
        print(f"\nGenotype: {horse.genotype_string}")
        print(f"Phenotype: {horse.phenotype}\n")
    except ValueError as e:
        print(f"\nError: {e}\n")
        return 1

    return 0


def show_probabilities(parent1_str: str, parent2_str: str):
    """Show breeding probability distribution."""
    from genetics.breeding_stats import calculate_offspring_probabilities, format_probability_report

    try:
        print("\n" + "=" * 80)
        print("BREEDING PROBABILITY CALCULATOR")
        print("=" * 80)
        print(f"\nParent 1: {parent1_str}")
        print(f"Parent 2: {parent2_str}")
        print("\nCalculating probabilities...")

        probabilities = calculate_offspring_probabilities(parent1_str, parent2_str)

        print("\n" + format_probability_report(probabilities))

    except ValueError as e:
        print(f"\nError: {e}\n")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}\n")
        return 1

    return 0


def simulate_breeding(count: int, parent1_str: str, parent2_str: str):
    """Simulate breeding multiple times and show statistics."""
    from genetics.horse import Horse
    from genetics.gene_registry import get_default_registry
    from genetics.gene_interaction import PhenotypeCalculator
    from collections import Counter

    registry = get_default_registry()
    calculator = PhenotypeCalculator(registry)

    try:
        # Parse parents
        parent1_geno = registry.parse_genotype_string(parent1_str)
        parent2_geno = registry.parse_genotype_string(parent2_str)

        parent1 = Horse(parent1_geno, registry, calculator)
        parent2 = Horse(parent2_geno, registry, calculator)

        print("\n" + "=" * 80)
        print(f"BREEDING SIMULATION - {count} offspring")
        print("=" * 80)
        print(f"\nParent 1: {parent1.phenotype}")
        print(f"  Genotype: {parent1.genotype_string}")
        print(f"\nParent 2: {parent2.phenotype}")
        print(f"  Genotype: {parent2.genotype_string}")
        print(f"\nSimulating {count} breedings...")

        # Simulate breedings
        phenotypes = []
        for _ in range(count):
            offspring = Horse.breed(parent1, parent2, registry, calculator)
            phenotypes.append(offspring.phenotype)

        # Count occurrences
        phenotype_counts = Counter(phenotypes)

        # Display results
        print("\n" + "=" * 80)
        print("SIMULATION RESULTS")
        print("=" * 80)
        print()

        # Sort by count (most common first)
        sorted_phenotypes = sorted(
            phenotype_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Find longest phenotype name for alignment
        max_name_length = max(len(name) for name, _ in sorted_phenotypes)

        for phenotype, count_value in sorted_phenotypes:
            percentage = (count_value / count) * 100
            bar_length = int(percentage / 2.5)  # Scale to fit 40 chars max
            bar = "█" * bar_length

            name_padded = phenotype.ljust(max_name_length)
            print(f"{name_padded} : {count_value:4d} ({percentage:5.1f}%)  {bar}")

        print()
        print(f"Total offspring: {count}")
        print(f"Unique phenotypes: {len(phenotype_counts)}")
        print("=" * 80)

    except ValueError as e:
        print(f"\nError: {e}\n")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}\n")
        return 1

    return 0


def find_genotypes_for_phenotype(target_phenotype: str, max_results: int = 10):
    """Find genotypes that produce a specific phenotype."""
    from genetics.horse import Horse
    from genetics.gene_registry import get_default_registry
    from genetics.gene_interaction import PhenotypeCalculator

    registry = get_default_registry()
    calculator = PhenotypeCalculator(registry)

    print("\n" + "=" * 80)
    print(f"GENOTYPE FINDER - Searching for: {target_phenotype}")
    print("=" * 80)
    print("\nSearching for genotypes that produce this phenotype...")
    print("(This may take a moment...)\n")

    found_genotypes = []
    attempts = 0
    max_attempts = 10000  # Try up to 10,000 random genotypes

    while len(found_genotypes) < max_results and attempts < max_attempts:
        genotype = registry.generate_random_genotype()
        phenotype = calculator.determine_phenotype(genotype)

        if phenotype == target_phenotype:
            genotype_str = registry.format_genotype(genotype, compact=True)
            if genotype_str not in [g[0] for g in found_genotypes]:
                found_genotypes.append((genotype_str, genotype))

        attempts += 1

    if found_genotypes:
        print(f"Found {len(found_genotypes)} unique genotype(s) after {attempts} attempts:\n")
        print("=" * 80)

        for i, (genotype_str, genotype) in enumerate(found_genotypes, 1):
            print(f"\n{i}. {genotype_str}")

            # Show detailed breakdown
            print("   Breakdown:")
            for gene_name in registry.get_all_gene_names():
                gene_def = registry.get_gene(gene_name)
                alleles = '/'.join(genotype[gene_name])
                print(f"     {gene_def.full_name} ({gene_def.symbol}): {alleles}")

        print("\n" + "=" * 80)
        print(f"\nYou can use any of these genotypes to create a {target_phenotype} horse!")
    else:
        print(f"No genotypes found for '{target_phenotype}' after {attempts} attempts.")
        print("This phenotype might be very rare or not exist.")
        print("\nTip: Check spelling and capitalization (e.g., 'Buckskin' not 'buckskin')")

    return 0 if found_genotypes else 1


def main():
    """Main function for CLI interface with argument support."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Horse Coat Color Genetics Simulator',
        epilog='For interactive mode, run without arguments'
    )

    parser.add_argument(
        '--batch', '-b',
        type=int,
        metavar='N',
        help='Generate N random horses and exit'
    )

    parser.add_argument(
        '--genotype', '-g',
        type=str,
        metavar='STR',
        help='Show phenotype for given genotype string and exit'
    )

    parser.add_argument(
        '--probabilities', '-p',
        nargs=2,
        metavar=('PARENT1', 'PARENT2'),
        help='Calculate breeding probabilities for two parents'
    )

    parser.add_argument(
        '--simulate', '-s',
        nargs=3,
        metavar=('N', 'PARENT1', 'PARENT2'),
        help='Simulate N breedings and show statistics'
    )

    parser.add_argument(
        '--find-genotypes', '-f',
        type=str,
        metavar='PHENOTYPE',
        help='Find genotypes that produce a specific phenotype'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Horse Genetics Simulator v2.0.0'
    )

    args = parser.parse_args()

    # Handle batch mode
    if args.batch:
        batch_generate(args.batch)
        return

    # Handle genotype mode
    if args.genotype:
        return show_phenotype(args.genotype)

    # Handle probability calculation
    if args.probabilities:
        parent1, parent2 = args.probabilities
        return show_probabilities(parent1, parent2)

    # Handle simulation
    if args.simulate:
        try:
            count = int(args.simulate[0])
            parent1 = args.simulate[1]
            parent2 = args.simulate[2]
            return simulate_breeding(count, parent1, parent2)
        except ValueError:
            print("Error: First argument to --simulate must be a number")
            return 1

    # Handle genotype finder
    if args.find_genotypes:
        return find_genotypes_for_phenotype(args.find_genotypes)

    # Interactive mode (original behavior)
    generator = HorseGeneticGenerator()

    print("=" * 60)
    print("HORSE COAT COLOR GENETICS SIMULATOR")
    print("=" * 60)
    print("\nThis simulator models 9 genetic traits:")
    print("  1. Extension (E/e) - Black or red pigment")
    print("  2. Agouti (A/a) - Bay or black distribution")
    print("  3. Dilution (N/Cr/Prl) - Cream and Pearl dilutions")
    print("  4. Dun (D/nd1/nd2) - Dun dilution with primitive markings")
    print("  5. Silver (Z/n) - Lightens black pigment")
    print("  6. Champagne (Ch/n) - Lightens both red and black pigment")
    print("  7. Flaxen (F/f) - Lightens mane/tail on chestnuts only")
    print("  8. Sooty (STY/sty) - Adds darker hairs")
    print("  9. Gray (G/g) - Progressive graying with age")

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
            print("Format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty G:G/g")
            print("\nExample: E:E/e A:A/a Dil:N/Cr D:nd1/nd2 Z:n/n Ch:n/n F:F/f STY:STY/sty G:g/g")

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
