"""
Breeding Statistics - Calculate offspring probabilities

This module calculates statistical probabilities for breeding outcomes.
Perfect for game projects where players want to know their chances!

Example usage:
    from genetics.breeding_stats import calculate_offspring_probabilities

    parent1 = "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"
    parent2 = "E:e/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"

    probabilities = calculate_offspring_probabilities(parent1, parent2)

    for phenotype, probability in probabilities.items():
        print(f"{phenotype}: {probability:.1%}")
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from genetics.horse import Horse
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator
import itertools


def calculate_gene_probabilities(
    parent1_alleles: Tuple[str, str],
    parent2_alleles: Tuple[str, str]
) -> Dict[Tuple[str, str], float]:
    """
    Calculate probabilities for a single gene's offspring genotypes.

    Uses Mendelian inheritance: each parent contributes one random allele.

    Args:
        parent1_alleles: Parent 1 genotype (e.g., ('E', 'e'))
        parent2_alleles: Parent 2 genotype (e.g., ('E', 'e'))

    Returns:
        dict: {genotype: probability}

    Example:
        >>> calculate_gene_probabilities(('E', 'e'), ('E', 'e'))
        {('E', 'E'): 0.25, ('E', 'e'): 0.5, ('e', 'e'): 0.25}
    """
    # All possible combinations (4 total)
    combinations = [
        (p1, p2)
        for p1 in parent1_alleles
        for p2 in parent2_alleles
    ]

    # Count occurrences of each genotype
    genotype_counts = defaultdict(int)
    for allele1, allele2 in combinations:
        # Sort alleles for consistency (dominant first)
        genotype = tuple(sorted([allele1, allele2], reverse=True))
        genotype_counts[genotype] += 1

    # Convert counts to probabilities
    total = len(combinations)
    probabilities = {
        genotype: count / total
        for genotype, count in genotype_counts.items()
    }

    return probabilities


def calculate_all_genotype_combinations(
    parent1_genotype: Dict[str, Tuple[str, str]],
    parent2_genotype: Dict[str, Tuple[str, str]],
    registry=None
) -> List[Tuple[Dict[str, Tuple[str, str]], float]]:
    """
    Calculate all possible offspring genotypes with their probabilities.

    This can generate many combinations (up to 4^9 = 262,144 for 9 genes),
    so we use a smart approach to combine probabilities.

    Args:
        parent1_genotype: Parent 1 complete genotype
        parent2_genotype: Parent 2 complete genotype
        registry: GeneRegistry instance

    Returns:
        List of (genotype, probability) tuples
    """
    if registry is None:
        registry = get_default_registry()

    # Calculate probabilities for each gene independently
    gene_probabilities = {}

    for gene_name in registry.get_all_gene_names():
        p1_alleles = parent1_genotype[gene_name]
        p2_alleles = parent2_genotype[gene_name]

        gene_probs = calculate_gene_probabilities(p1_alleles, p2_alleles)
        gene_probabilities[gene_name] = gene_probs

    # Generate all combinations using itertools.product
    # This creates a cartesian product of all gene possibilities
    gene_names = registry.get_all_gene_names()

    # Create list of (gene_name, [(genotype, probability), ...]) for each gene
    gene_options = [
        [(gene_name, genotype, prob) for genotype, prob in gene_probabilities[gene_name].items()]
        for gene_name in gene_names
    ]

    # Generate all combinations
    all_combinations = []

    for combination in itertools.product(*gene_options):
        # Build genotype from this combination
        genotype = {}
        total_probability = 1.0

        for gene_name, alleles, prob in combination:
            gene_def = registry.get_gene(gene_name)
            genotype[gene_name] = gene_def.sort_alleles(list(alleles))
            total_probability *= prob

        all_combinations.append((genotype, total_probability))

    return all_combinations


def calculate_offspring_probabilities(
    parent1: str,
    parent2: str,
    sample_size: Optional[int] = None,
    registry=None,
    calculator=None
) -> Dict[str, float]:
    """
    Calculate probability distribution of offspring phenotypes.

    This is the main function game developers will use!

    Args:
        parent1: Parent 1 genotype string
        parent2: Parent 2 genotype string
        sample_size: If provided, use Monte Carlo sampling instead of exact calculation
        registry: Optional GeneRegistry instance
        calculator: Optional PhenotypeCalculator instance

    Returns:
        dict: {phenotype: probability}
        Sorted by probability (most likely first)

    Example:
        >>> probs = calculate_offspring_probabilities(
        ...     "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g",
        ...     "E:e/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"
        ... )
        >>> print(f"Buckskin: {probs.get('Buckskin', 0):.1%}")
        Buckskin: 25.0%
    """
    if registry is None:
        registry = get_default_registry()
    if calculator is None:
        calculator = PhenotypeCalculator(registry)

    # Parse parent genotypes
    parent1_genotype = registry.parse_genotype_string(parent1)
    parent2_genotype = registry.parse_genotype_string(parent2)

    phenotype_probabilities = defaultdict(float)

    if sample_size:
        # Monte Carlo approach: simulate many breedings
        for _ in range(sample_size):
            offspring_genotype = registry.breed(parent1_genotype, parent2_genotype)
            phenotype = calculator.determine_phenotype(offspring_genotype)
            phenotype_probabilities[phenotype] += 1.0 / sample_size
    else:
        # Exact calculation: enumerate all possibilities
        all_combinations = calculate_all_genotype_combinations(
            parent1_genotype,
            parent2_genotype,
            registry
        )

        for genotype, probability in all_combinations:
            phenotype = calculator.determine_phenotype(genotype)
            phenotype_probabilities[phenotype] += probability

    # Sort by probability (highest first)
    sorted_probabilities = dict(
        sorted(
            phenotype_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

    return sorted_probabilities


def format_probability_report(
    probabilities: Dict[str, float],
    min_probability: float = 0.001
) -> str:
    """
    Format probability report for display.

    Args:
        probabilities: Dict of {phenotype: probability}
        min_probability: Minimum probability to show (default: 0.1%)

    Returns:
        str: Formatted report

    Example:
        >>> probs = {'Bay': 0.5, 'Black': 0.25, 'Chestnut': 0.25}
        >>> print(format_probability_report(probs))
        Bay        : 50.0%  ████████████████████
        Black      : 25.0%  ██████████
        Chestnut   : 25.0%  ██████████
    """
    lines = []
    lines.append("=" * 60)
    lines.append("OFFSPRING PROBABILITY DISTRIBUTION")
    lines.append("=" * 60)
    lines.append("")

    # Filter out very low probabilities
    filtered = {k: v for k, v in probabilities.items() if v >= min_probability}

    if not filtered:
        lines.append("No outcomes above minimum probability threshold.")
        return '\n'.join(lines)

    # Find longest phenotype name for alignment
    max_name_length = max(len(name) for name in filtered.keys())

    for phenotype, probability in filtered.items():
        # Calculate bar length (max 40 characters)
        bar_length = int(probability * 40)
        bar = "█" * bar_length

        # Format line
        name_padded = phenotype.ljust(max_name_length)
        lines.append(f"{name_padded} : {probability:5.1%}  {bar}")

    lines.append("")
    lines.append(f"Total outcomes shown: {len(filtered)}")
    lines.append(f"Combined probability: {sum(filtered.values()):.1%}")
    lines.append("=" * 60)

    return '\n'.join(lines)


def get_guaranteed_traits(
    parent1_genotype: Dict[str, Tuple[str, str]],
    parent2_genotype: Dict[str, Tuple[str, str]],
    registry=None
) -> Dict[str, str]:
    """
    Find traits that are guaranteed in all offspring.

    Example: If both parents are e/e (chestnut), all offspring will be e/e.

    Args:
        parent1_genotype: Parent 1 genotype dict
        parent2_genotype: Parent 2 genotype dict
        registry: Optional GeneRegistry instance

    Returns:
        dict: {gene_name: guaranteed_genotype_string}

    Example:
        >>> # Both parents are e/e
        >>> guaranteed = get_guaranteed_traits(
        ...     {'extension': ('e', 'e'), ...},
        ...     {'extension': ('e', 'e'), ...}
        ... )
        >>> print(guaranteed)
        {'extension': 'e/e'}
    """
    if registry is None:
        registry = get_default_registry()

    guaranteed = {}

    for gene_name in registry.get_all_gene_names():
        p1_alleles = parent1_genotype[gene_name]
        p2_alleles = parent2_genotype[gene_name]

        # Get all possible alleles offspring can inherit
        possible_alleles = set(p1_alleles) | set(p2_alleles)

        # If only one unique allele exists, offspring is guaranteed homozygous
        if len(possible_alleles) == 1:
            allele = list(possible_alleles)[0]
            guaranteed[gene_name] = f"{allele}/{allele}"

    return guaranteed


def calculate_single_gene_probability(
    parent1: str,
    parent2: str,
    gene_name: str,
    target_genotype: Tuple[str, str],
    registry=None
) -> float:
    """
    Calculate probability of specific genotype for a single gene.

    Useful for breeders targeting specific traits.

    Args:
        parent1: Parent 1 genotype string
        parent2: Parent 2 genotype string
        gene_name: Gene to analyze (e.g., 'extension')
        target_genotype: Target genotype (e.g., ('E', 'E'))
        registry: Optional GeneRegistry instance

    Returns:
        float: Probability (0.0 to 1.0)

    Example:
        >>> prob = calculate_single_gene_probability(
        ...     "E:E/e A:A/a ...",
        ...     "E:E/e A:A/a ...",
        ...     "extension",
        ...     ('E', 'E')
        ... )
        >>> print(f"Probability of E/E: {prob:.1%}")
        Probability of E/E: 25.0%
    """
    if registry is None:
        registry = get_default_registry()

    parent1_genotype = registry.parse_genotype_string(parent1)
    parent2_genotype = registry.parse_genotype_string(parent2)

    p1_alleles = parent1_genotype[gene_name]
    p2_alleles = parent2_genotype[gene_name]

    gene_probs = calculate_gene_probabilities(p1_alleles, p2_alleles)

    # Normalize target genotype (sort alleles)
    gene_def = registry.get_gene(gene_name)
    normalized_target = gene_def.sort_alleles(list(target_genotype))

    return gene_probs.get(normalized_target, 0.0)
