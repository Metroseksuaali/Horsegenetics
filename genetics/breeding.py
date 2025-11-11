"""
Breeding simulation module - Mendelian inheritance and genotype parsing

This module handles breeding simulation following Mendelian genetics
and provides utilities for genotype input/output.
"""

import random
from genetics.core import GenePool
from genetics.phenotype import PhenotypeCalculator


class BreedingSimulator:
    """
    Simulates horse breeding following Mendelian inheritance patterns.

    Each parent contributes one random allele from each gene to offspring.
    """

    def __init__(self):
        """Initialize with gene pool and phenotype calculator."""
        self.gene_pool = GenePool()
        self.phenotype_calculator = PhenotypeCalculator()

    def generate_random_horse(self):
        """
        Generate a complete random horse with genotype and phenotype.

        Returns:
            dict: Horse with 'genotype' and 'phenotype' keys
        """
        genotype = self.gene_pool.generate_random_genotype()
        phenotype = self.phenotype_calculator.determine_phenotype(genotype)

        return {
            'genotype': genotype,
            'phenotype': phenotype
        }

    def breed_horses(self, parent1_genotype, parent2_genotype):
        """
        Breed two horses and return offspring genotype.

        Each parent passes one random allele from each gene to offspring,
        following Mendelian inheritance.

        Args:
            parent1_genotype: Complete genotype dict for parent 1
            parent2_genotype: Complete genotype dict for parent 2

        Returns:
            dict: Offspring genotype
        """
        offspring_genotype = {}

        # For each gene, offspring gets one allele from each parent
        for gene in ['extension', 'agouti', 'dilution', 'dun', 'silver',
                     'champagne', 'flaxen', 'sooty']:
            # Random allele from parent 1
            allele_from_parent1 = random.choice(parent1_genotype[gene])
            # Random allele from parent 2
            allele_from_parent2 = random.choice(parent2_genotype[gene])

            # Sort alleles by dominance
            offspring_genotype[gene] = self.gene_pool._sort_alleles(
                [allele_from_parent1, allele_from_parent2]
            )

        return offspring_genotype

    def parse_genotype_input(self, genotype_str):
        """
        Parse user input genotype string.

        Expected format: E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty

        Note: Dil (dilution) contains N, Cr, and Prl alleles (same gene).

        Args:
            genotype_str: String representation of genotype

        Returns:
            dict: Parsed genotype dictionary

        Raises:
            ValueError: If genotype string is invalid
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

                # Map gene labels to internal gene names
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
                genotype[gene_name] = self.gene_pool._sort_alleles(alleles)

            # Verify all required genes are present
            required_genes = ['extension', 'agouti', 'dilution', 'dun',
                            'silver', 'champagne', 'flaxen', 'sooty']
            for gene in required_genes:
                if gene not in genotype:
                    raise ValueError(f"Missing gene: {gene}")

            return genotype

        except Exception as e:
            raise ValueError(f"Error parsing genotype: {e}")

    def validate_genotype(self, genotype):
        """
        Validate that a genotype dictionary is properly formed.

        Args:
            genotype: Genotype dictionary to validate

        Returns:
            bool: True if valid

        Raises:
            ValueError: If genotype is invalid
        """
        required_genes = ['extension', 'agouti', 'dilution', 'dun',
                         'silver', 'champagne', 'flaxen', 'sooty']

        for gene in required_genes:
            if gene not in genotype:
                raise ValueError(f"Missing gene: {gene}")

            if not isinstance(genotype[gene], tuple) or len(genotype[gene]) != 2:
                raise ValueError(f"Invalid {gene} genotype: must be tuple of 2 alleles")

        return True
