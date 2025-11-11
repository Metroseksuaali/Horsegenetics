"""
Horse Genetics Module

This module provides comprehensive horse coat color genetics simulation
with support for thousands of genetic combinations.

Main components:
- core: Gene pools and allele definitions
- phenotype: Phenotype determination from genotypes
- breeding: Breeding simulation and inheritance
"""

from genetics.core import GenePool
from genetics.breeding import BreedingSimulator
from genetics.phenotype import PhenotypeCalculator

__all__ = ['GenePool', 'BreedingSimulator', 'PhenotypeCalculator']
__version__ = '2.0.0'
