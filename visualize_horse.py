#!/usr/bin/env python3
"""
Horse Visualizer CLI

Command-line tool to generate horse images from genotypes or phenotypes.

Usage:
    python visualize_horse.py --phenotype "Bay Tobiano" --output my_horse.svg
    python visualize_horse.py --random
    python visualize_horse.py --genotype "E:E/e A:A/a ..." --output horse.svg
"""

import argparse
import sys
from genetics.visualizer import HorseVisualizer
from genetics.horse import Horse


def main():
    parser = argparse.ArgumentParser(
        description='Generate visual representation of a horse based on genetics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate from phenotype
  python visualize_horse.py --phenotype "Bay Tobiano" --output bay_tobiano.svg

  # Generate random horse
  python visualize_horse.py --random --output random_horse.svg

  # Generate from genotype string
  python visualize_horse.py --genotype "E:E/e A:A/a Dil:N/N ..." --output horse.svg

  # Generate multiple examples
  python visualize_horse.py --examples
        '''
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--phenotype', '-p', type=str,
                       help='Phenotype string (e.g., "Bay Tobiano")')
    group.add_argument('--random', '-r', action='store_true',
                       help='Generate a random horse')
    group.add_argument('--genotype', '-g', type=str,
                       help='Full genotype string')
    group.add_argument('--examples', '-e', action='store_true',
                       help='Generate multiple example horses')

    parser.add_argument('--output', '-o', type=str, default='horse.svg',
                        help='Output filename (default: horse.svg)')

    args = parser.parse_args()

    visualizer = HorseVisualizer()

    try:
        if args.examples:
            # Generate multiple examples
            examples = [
                ("Bay", "example_bay.svg"),
                ("Chestnut", "example_chestnut.svg"),
                ("Black", "example_black.svg"),
                ("Palomino", "example_palomino.svg"),
                ("Buckskin", "example_buckskin.svg"),
                ("Grullo (Black Dun)", "example_grullo.svg"),
                ("Bay Roan", "example_bay_roan.svg"),
                ("Chestnut Roan", "example_chestnut_roan.svg"),
                ("Bay Tobiano", "example_tobiano.svg"),
                ("Bay Tovero", "example_tovero.svg"),
                ("Bay Leopard", "example_leopard.svg"),
                ("Bay Fewspot", "example_fewspot.svg"),
                ("Dominant White (W20)", "example_white.svg"),
            ]

            print("Generating example horses...")
            for phenotype, filename in examples:
                visualizer.save_svg(phenotype, filename)

            print(f"\n✓ Generated {len(examples)} example horses!")
            print("  Files: example_*.svg")

        elif args.random:
            # Generate random horse
            horse = Horse.random()
            print(f"Generated random horse: {horse.phenotype}")
            print(f"Genotype: {horse.genotype_string}\n")

            visualizer.save_svg(horse.phenotype, args.output, horse.genotype)

        elif args.genotype:
            # Parse genotype and generate
            horse = Horse.from_string(args.genotype)
            print(f"Phenotype: {horse.phenotype}\n")

            visualizer.save_svg(horse.phenotype, args.output, horse.genotype)

        elif args.phenotype:
            # Generate from phenotype only
            visualizer.save_svg(args.phenotype, args.output)

        print(f"\n✓ Horse visualization complete!")
        print(f"  Open {args.output} in a web browser or image viewer.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
