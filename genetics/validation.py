"""
Validation utilities - User-friendly genotype validation

This module provides helpful validation functions with clear error messages.
Perfect for user input validation in games or interactive applications.

Example usage:
    from genetics.validation import validate_genotype_string, suggest_fixes

    result = validate_genotype_string("E:E/e A:A/a Dil:N/Cr")
    if result['errors']:
        print("Errors:", result['errors'])
        print("Suggestions:", suggest_fixes(result))
"""

from typing import Dict, List, Tuple
import re


def validate_genotype_string(genotype_str: str) -> Dict[str, List[str]]:
    """
    Validate genotype string and return helpful errors and warnings.

    Args:
        genotype_str: Genotype string to validate

    Returns:
        dict: {'errors': [...], 'warnings': [...], 'info': [...]}

    Example:
        >>> from genetics.validation import validate_genotype_string
        >>> result = validate_genotype_string("E:E/e A:A/a")
        >>> print(result['errors'])  # doctest: +SKIP
        ['Missing required genes...']
    """
    errors = []
    warnings = []
    info = []

    # Check if string is empty
    if not genotype_str.strip():
        errors.append("Genotype string is empty")
        info.append("Expected format: E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n Spl:n/n Lp:lp/lp PATN1:n/n")
        return {'errors': errors, 'warnings': warnings, 'info': info}

    # Check for basic format
    if ':' not in genotype_str:
        errors.append("Missing ':' separator between gene labels and alleles")
        info.append("Format should be: GeneName:allele1/allele2")
        return {'errors': errors, 'warnings': warnings, 'info': info}

    if '/' not in genotype_str:
        errors.append("Missing '/' separator between alleles")
        info.append("Each gene needs exactly 2 alleles separated by '/'")
        return {'errors': errors, 'warnings': warnings, 'info': info}

    # Parse and check each gene
    parts = genotype_str.strip().split()

    # Get required genes dynamically from gene definitions
    from genetics.gene_definitions import get_all_gene_symbols
    required_genes = set(get_all_gene_symbols())
    found_genes = set()

    for part in parts:
        if ':' not in part:
            warnings.append(f"Skipping malformed part: '{part}' (missing ':')")
            continue

        gene_label, alleles_str = part.split(':', 1)
        found_genes.add(gene_label)

        # Check allele count
        alleles = alleles_str.split('/')
        if len(alleles) < 2:
            errors.append(f"Gene {gene_label} has only 1 allele, needs exactly 2")
        elif len(alleles) > 2:
            errors.append(f"Gene {gene_label} has {len(alleles)} alleles, needs exactly 2")
            info.append("Common mistake: 'Cr/Cr/Cr' should be 'Cr/Cr'")

        # Check for empty alleles
        for i, allele in enumerate(alleles):
            if not allele.strip():
                errors.append(f"Gene {gene_label}: allele {i+1} is empty")

        # Check for valid gene labels
        if gene_label not in required_genes:
            errors.append(f"Unknown gene label: '{gene_label}'")
            # Suggest similar gene names
            suggestions = _suggest_similar_gene(gene_label, required_genes)
            if suggestions:
                info.append(f"Did you mean: {', '.join(suggestions)}?")

    # Check for missing genes
    missing_genes = required_genes - found_genes
    if missing_genes:
        errors.append(f"Missing required genes: {', '.join(sorted(missing_genes))}")
        info.append(f"All {len(required_genes)} genes are required for a complete genotype")

    # Check for common typos
    if 'dilution' in genotype_str.lower() or 'cream' in genotype_str.lower():
        warnings.append("Use 'Dil' as the gene label, not 'dilution' or 'cream'")

    if 'sooty' in genotype_str.lower() and 'STY' not in genotype_str:
        warnings.append("Use 'STY' as the gene label for Sooty, not 'sooty'")

    # Check for duplicate genes
    gene_counts = {}
    for part in parts:
        if ':' in part:
            gene_label = part.split(':')[0]
            gene_counts[gene_label] = gene_counts.get(gene_label, 0) + 1

    for gene, count in gene_counts.items():
        if count > 1:
            errors.append(f"Gene {gene} appears {count} times (should appear only once)")

    return {
        'errors': errors,
        'warnings': warnings,
        'info': info
    }


def _suggest_similar_gene(gene: str, valid_genes: set) -> List[str]:
    """Suggest similar gene names based on edit distance."""
    suggestions = []
    gene_lower = gene.lower()

    for valid in valid_genes:
        valid_lower = valid.lower()
        # Simple similarity check
        if gene_lower in valid_lower or valid_lower in gene_lower:
            suggestions.append(valid)
        elif len(gene) > 1 and len(valid) > 1:
            # Check first letter match
            if gene[0].upper() == valid[0].upper():
                suggestions.append(valid)

    return suggestions[:3]  # Return top 3 suggestions


def suggest_fixes(validation_result: Dict[str, List[str]]) -> List[str]:
    """
    Generate fix suggestions based on validation errors.

    Args:
        validation_result: Output from validate_genotype_string()

    Returns:
        List of suggested fixes

    Example:
        >>> from genetics.validation import validate_genotype_string, suggest_fixes
        >>> result = validate_genotype_string("E:E/e A:A/a")
        >>> fixes = suggest_fixes(result)
        >>> print(fixes[0])  # doctest: +SKIP
        'Add missing genes: Dil, D, Z, Ch, F, STY, G'
    """
    suggestions = []
    errors = validation_result.get('errors', [])

    for error in errors:
        if 'Missing required genes:' in error:
            # Extract missing genes from error message
            match = re.search(r'Missing required genes: (.+)', error)
            if match:
                missing = match.group(1)
                suggestions.append(
                    f"Add these genes with default values:\n"
                    f"  Example: Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/F STY:sty/sty G:g/g"
                )

        elif 'has only 1 allele' in error or 'alleles, needs exactly 2' in error:
            suggestions.append(
                "Each gene must have exactly 2 alleles separated by '/'\n"
                "  Example: E:E/e (correct) not E:E (wrong)"
            )

        elif 'appears' in error and 'times' in error:
            suggestions.append(
                "Remove duplicate gene entries - each gene should appear only once"
            )

        elif 'Unknown gene label' in error:
            suggestions.append(
                "Valid gene labels are: E, A, Dil, D, Z, Ch, F, STY, G"
            )

    return suggestions


def validate_allele_values(genotype_str: str) -> Dict[str, List[str]]:
    """
    Validate that allele values are valid for each gene.

    This is a deeper validation that checks actual allele values.

    Args:
        genotype_str: Genotype string to validate

    Returns:
        dict: {'errors': [...], 'warnings': [...]}

    Example:
        >>> from genetics.validation import validate_allele_values
        >>> result = validate_allele_values("E:E/e A:A/a Dil:N/X D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g")
        >>> 'X' in str(result['errors'])  # doctest: +SKIP
        True
    """
    from genetics.gene_definitions import GENES_BY_SYMBOL

    errors = []
    warnings = []

    # First do basic validation
    basic_result = validate_genotype_string(genotype_str)
    if basic_result['errors']:
        return {'errors': basic_result['errors'], 'warnings': basic_result['warnings']}

    # Parse genes
    parts = genotype_str.strip().split()

    for part in parts:
        if ':' not in part:
            continue

        gene_label, alleles_str = part.split(':', 1)
        alleles = alleles_str.split('/')

        # Get valid alleles for this gene
        if gene_label in GENES_BY_SYMBOL:
            gene_def = GENES_BY_SYMBOL[gene_label]
            valid_alleles = set(gene_def.alleles)

            for allele in alleles:
                if allele not in valid_alleles:
                    errors.append(
                        f"Invalid allele '{allele}' for gene {gene_label}. "
                        f"Valid alleles: {', '.join(sorted(valid_alleles))}"
                    )

    return {'errors': errors, 'warnings': warnings}


def quick_validate(genotype_str: str) -> Tuple[bool, str]:
    """
    Quick validation that returns simple True/False with error message.

    Convenience function for simple validation checks.

    Args:
        genotype_str: Genotype string to validate

    Returns:
        tuple: (is_valid, error_message)

    Example:
        >>> from genetics.validation import quick_validate
        >>> is_valid, msg = quick_validate("E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n Spl:n/n Lp:lp/lp PATN1:n/n")
        >>> is_valid
        True
    """
    result = validate_genotype_string(genotype_str)

    if result['errors']:
        error_msg = "; ".join(result['errors'])
        return False, error_msg

    # Also check allele values
    allele_result = validate_allele_values(genotype_str)
    if allele_result['errors']:
        error_msg = "; ".join(allele_result['errors'])
        return False, error_msg

    return True, "Valid genotype"


def get_example_genotype() -> str:
    """
    Get an example of a valid genotype string.

    Useful for showing users the correct format.

    Returns:
        str: Example genotype string

    Example:
        >>> from genetics.validation import get_example_genotype
        >>> print(get_example_genotype())
        E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n Spl:n/n Lp:lp/lp PATN1:n/n
    """
    return "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
