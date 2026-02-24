"""
Horse Genetics Module

This module provides comprehensive horse coat color genetics simulation
with support for thousands of genetic combinations across 17 genes.

Main components:
- horse: Main Horse class with fluent API
- gene_registry: Dynamic gene management (17 genes)
- gene_interaction: Phenotype calculation pipeline
- breeding_stats: Breeding probability calculations
"""

from genetics.horse import Horse
from genetics.gene_registry import GeneRegistry, get_default_registry
from genetics.gene_interaction import PhenotypeCalculator

__all__ = [
    'Horse',
    'GeneRegistry',
    'get_default_registry',
    'PhenotypeCalculator',
]
__version__ = '2.0.0'
