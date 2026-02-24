"""
Comprehensive unit tests for horse coat color genetics simulator.

These tests verify scientific accuracy of genetic inheritance and phenotype
determination based on peer-reviewed equine genetics research.
"""

import unittest
import os
import csv
import tempfile
from genetics.gene_interaction import PhenotypeCalculator
from genetics.horse import Horse
from genetics.breeding_stats import (
    calculate_gene_probabilities,
    calculate_single_gene_probability,
    get_guaranteed_traits,
)
from genetics.gene_registry import get_default_registry
from genetics.io import horses_to_csv


class TestBasicColors(unittest.TestCase):
    """
    Test base coat colors (chestnut, bay, black).

    Scientific basis: MC1R (Extension) and ASIP (Agouti) interactions.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution=('N', 'N'),
                        dun=('nd2', 'nd2'), silver=('n', 'n'),
                        champagne=('n', 'n'), flaxen=('F', 'F'),
                        sooty=('sty', 'sty'), gray=('g', 'g'),
                        roan=('n', 'n'), tobiano=('n', 'n'),
                        frame=('n', 'n'), sabino=('n', 'n'),
                        dominant_white=('n', 'n'),
                        splash=('n', 'n'), leopard=('lp', 'lp'),
                        patn1=('n', 'n')):
        """Helper to create genotype dictionaries."""
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            'dun': dun,
            'silver': silver,
            'champagne': champagne,
            'flaxen': flaxen,
            'sooty': sooty,
            'gray': gray,
            'roan': roan,
            'tobiano': tobiano,
            'frame': frame,
            'sabino': sabino,
            'dominant_white': dominant_white,
            'splash': splash,
            'leopard': leopard,
            'patn1': patn1
        }

    def test_chestnut_base(self):
        """Test chestnut (e/e, any Agouti)."""
        # e/e A/A = chestnut
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Chestnut')

        # e/e a/a = chestnut (Agouti masked)
        genotype = self._create_genotype(('e', 'e'), ('a', 'a'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Chestnut')

    def test_bay_base(self):
        """Test bay (E/_, A/_) - black pigment restricted to points."""
        # E/E A/A = bay
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay')

        # E/e A/a = bay
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay')

    def test_black_base(self):
        """Test black (E/_, a/a) - uniform black pigment."""
        # E/E a/a = black
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Black')

        # E/e a/a = black
        genotype = self._create_genotype(('E', 'e'), ('a', 'a'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Black')


class TestCreamDilution(unittest.TestCase):
    """
    Test Cream dilution (SLC45A2 gene).

    Scientific basis: Incomplete dominance - single vs double copy effects.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution, **kwargs):
        """Helper to create genotype with optional modifiers."""
        defaults = {
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            **defaults
        }

    # Single Cream Dilution Tests
    def test_palomino(self):
        """Test palomino (chestnut + single Cream)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('N', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Palomino')

    def test_buckskin(self):
        """Test buckskin (bay + single Cream)."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('N', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Buckskin')

    def test_smoky_black(self):
        """Test smoky black (black + single Cream)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('N', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Smoky Black')

    # Double Cream Dilution Tests
    def test_cremello(self):
        """Test cremello (chestnut + double Cream)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Cr', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Cremello')

    def test_perlino(self):
        """Test perlino (bay + double Cream)."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Cr', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Perlino')

    def test_smoky_cream(self):
        """Test smoky cream (black + double Cream)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Cr', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Smoky Cream')


class TestPearlDilution(unittest.TestCase):
    """
    Test Pearl dilution and compound heterozygotes.

    Scientific basis: Pearl is recessive allele at same locus as Cream (SLC45A2).
    Compound heterozygotes (Cr/Prl) phenocopy double dilutes.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution, **kwargs):
        """Helper to create genotype with optional modifiers."""
        defaults = {
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            **defaults
        }

    def test_pearl_carrier_no_effect(self):
        """Test N/Prl carrier has no visible effect."""
        # Chestnut carrier
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('N', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Chestnut')

        # Bay carrier
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('N', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay')

    def test_double_pearl_apricot(self):
        """Test apricot (chestnut + double Pearl)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Prl', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Apricot')

    def test_double_pearl_bay(self):
        """Test pearl bay (bay + double Pearl)."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Prl', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Pearl Bay')

    def test_double_pearl_black(self):
        """Test smoky pearl (black + double Pearl)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Prl', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Smoky Pearl')

    def test_compound_heterozygote_chestnut(self):
        """Test Cr/Prl on chestnut = pseudo-cremello."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Cr', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Pseudo-Cremello')

    def test_compound_heterozygote_bay(self):
        """Test Cr/Prl on bay = pseudo-perlino."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Cr', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Pseudo-Perlino')

    def test_compound_heterozygote_black(self):
        """Test Cr/Prl on black = pseudo-smoky cream."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Cr', 'Prl'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Pseudo-Smoky Cream')


class TestChampagneDilution(unittest.TestCase):
    """
    Test Champagne dilution (SLC36A1 gene).

    Scientific basis: Dilutes both eumelanin and pheomelanin.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, champagne, **kwargs):
        """Helper to create genotype with champagne."""
        defaults = {
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'champagne': champagne,
            **defaults
        }

    def test_gold_champagne(self):
        """Test gold champagne (chestnut base)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Ch', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Gold Champagne')

    def test_amber_champagne(self):
        """Test amber champagne (bay base)."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Ch', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Amber Champagne')

    def test_classic_champagne(self):
        """Test classic champagne (black base)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Ch', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Classic Champagne')

    def test_champagne_with_cream(self):
        """Test champagne + cream interaction."""
        # Gold Cream Champagne (palomino + champagne)
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Ch', 'n'),
                                        dilution=('N', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Gold Cream Champagne')

        # Amber Cream Champagne (buckskin + champagne)
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Ch', 'n'),
                                        dilution=('N', 'Cr'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Amber Cream Champagne')


class TestSilverDilution(unittest.TestCase):
    """
    Test Silver dilution (PMEL17 gene).

    Scientific basis: Only affects eumelanin (black pigment).
    Does NOT affect pheomelanin (red/chestnut).
    DOES affect double cream dilutes (important for breeding).
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, silver, **kwargs):
        """Helper to create genotype with silver."""
        defaults = {
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'silver': silver,
            **defaults
        }

    def test_silver_no_effect_on_chestnut(self):
        """Test silver has NO effect on chestnut (no black pigment)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Z', 'n'))
        phenotype = self.calc.determine_phenotype(genotype)
        # Should still be chestnut, not "Silver Chestnut"
        self.assertEqual(phenotype, 'Chestnut')

    def test_silver_bay(self):
        """Test silver bay (bay with silver mane/tail)."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Z', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Silver Bay')

    def test_silver_black(self):
        """Test silver black (silver dapple)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Z', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Silver Black')

    def test_silver_on_perlino(self):
        """Test silver affects perlino (bay + double cream) - CRITICAL TEST."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('Z', 'n'),
                                        dilution=('Cr', 'Cr'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertEqual(phenotype, 'Silver Perlino')

    def test_silver_on_smoky_cream(self):
        """Test silver affects smoky cream (black + double cream)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Z', 'n'),
                                        dilution=('Cr', 'Cr'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertEqual(phenotype, 'Silver Smoky Cream')

    def test_silver_not_on_cremello(self):
        """Test silver has NO effect on cremello (chestnut base)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('Z', 'n'),
                                        dilution=('Cr', 'Cr'))
        phenotype = self.calc.determine_phenotype(genotype)
        # Should be Cremello, not Silver Cremello
        self.assertEqual(phenotype, 'Cremello')


class TestDunGene(unittest.TestCase):
    """
    Test Dun gene (TBX3) with three alleles.

    Scientific basis: D > nd1 > nd2 dominance hierarchy.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dun, **kwargs):
        """Helper to create genotype with dun."""
        defaults = {
            'dilution': ('N', 'N'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'dun': dun,
            **defaults
        }

    def test_bay_dun(self):
        """Test bay dun (D/_ on bay)."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('D', 'nd2'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Dun', phenotype)
        self.assertIn('Bay', phenotype)

    def test_red_dun(self):
        """Test red dun (D/_ on chestnut)."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('D', 'nd2'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Dun', phenotype)
        self.assertIn('Chestnut', phenotype)

    def test_grullo(self):
        """Test grullo/grulla (D/_ on black)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('D', 'nd1'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Dun', phenotype)
        self.assertIn('Black', phenotype)

    def test_nd1_notation(self):
        """Test nd1 shows in phenotype notation."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('nd1', 'nd2'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('(nd1)', phenotype)

    def test_nd2_no_dun(self):
        """Test nd2/nd2 has no dun effect."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('nd2', 'nd2'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertNotIn('Dun', phenotype)
        self.assertNotIn('(nd1)', phenotype)


class TestFlaxenAndSooty(unittest.TestCase):
    """
    Test Flaxen and Sooty modifiers.

    Scientific basis:
    - Flaxen: Only visible on chestnut (e/e), genetic basis unknown
    - Sooty: Adds black hairs, NOT visible on pure black horses
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, flaxen=('F', 'F'),
                        sooty=('sty', 'sty'), **kwargs):
        """Helper to create genotype."""
        defaults = {
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'gray': ('g', 'g'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'flaxen': flaxen,
            'sooty': sooty,
            **defaults
        }

    def test_flaxen_on_chestnut(self):
        """Test flaxen is visible on chestnut."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), flaxen=('f', 'f'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Flaxen', phenotype)

    def test_flaxen_not_on_bay(self):
        """Test flaxen NOT visible on bay."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), flaxen=('f', 'f'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertNotIn('Flaxen', phenotype)

    def test_flaxen_not_on_black(self):
        """Test flaxen NOT visible on black."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), flaxen=('f', 'f'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertNotIn('Flaxen', phenotype)

    def test_sooty_on_chestnut(self):
        """Test sooty is visible on chestnut."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), sooty=('STY', 'sty'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Sooty', phenotype)

    def test_sooty_on_bay(self):
        """Test sooty is visible on bay."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), sooty=('STY', 'STY'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Sooty', phenotype)

    def test_sooty_not_on_black(self):
        """Test sooty NOT visible on black (no red pigment to darken)."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), sooty=('STY', 'STY'))
        phenotype = self.calc.determine_phenotype(genotype)
        # Sooty should NOT appear on pure black
        self.assertNotIn('Sooty', phenotype)


class TestGrayGene(unittest.TestCase):
    """
    Test Gray gene (STX17) - progressive graying with age.

    Scientific basis: Dominant gene causing progressive depigmentation.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, gray, **kwargs):
        """Helper to create genotype with gray."""
        defaults = {
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'roan': ('n', 'n'),
            'tobiano': ('n', 'n'),
            'frame': ('n', 'n'),
            'sabino': ('n', 'n'),
            'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'),
            'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty')
        }
        defaults.update(kwargs)
        return {
            'extension': extension,
            'agouti': agouti,
            'gray': gray,
            **defaults
        }

    def test_gray_on_chestnut(self):
        """Test gray affects chestnut base."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('G', 'g'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Gray', phenotype)
        self.assertIn('will lighten with age', phenotype)
        self.assertIn('Chestnut', phenotype)

    def test_gray_on_bay(self):
        """Test gray affects bay base."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('G', 'G'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Gray', phenotype)
        self.assertIn('will lighten with age', phenotype)
        self.assertIn('Bay', phenotype)

    def test_gray_on_black(self):
        """Test gray affects black base."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('G', 'g'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Gray', phenotype)
        self.assertIn('will lighten with age', phenotype)
        self.assertIn('Black', phenotype)

    def test_gray_with_dilutions(self):
        """Test gray works with cream dilution."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'A'), ('G', 'g'),
                                        dilution=('N', 'Cr'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Gray', phenotype)
        self.assertIn('Palomino', phenotype)

    def test_gray_with_champagne(self):
        """Test gray works with champagne."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('G', 'g'),
                                        champagne=('Ch', 'n'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Gray', phenotype)
        self.assertIn('Amber Champagne', phenotype)

    def test_no_gray(self):
        """Test g/g shows no gray notation."""
        genotype = self._create_genotype(('E', 'E'), ('A', 'A'), ('g', 'g'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertNotIn('Gray', phenotype)
        self.assertNotIn('will lighten', phenotype)
        self.assertEqual(phenotype, 'Bay')


class TestBreeding(unittest.TestCase):
    """
    Test Mendelian inheritance in breeding simulation.

    Scientific basis: Each parent contributes one random allele per gene.
    """

    # Neutral base genotype string (no special patterns or dilutions)
    _NEUTRAL = "E:{ext} A:{ag} Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:{fl} STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"

    def test_homozygous_cross_produces_heterozygous(self):
        """Test E/E × e/e produces all E/e offspring."""
        parent1 = Horse.from_string(self._NEUTRAL.format(ext='E/E', ag='A/A', fl='F/F'))
        parent2 = Horse.from_string(self._NEUTRAL.format(ext='e/e', ag='a/a', fl='f/f'))

        for _ in range(100):
            offspring = Horse.breed(parent1, parent2)
            self.assertEqual(offspring.get_gene('extension'), ('E', 'e'))
            self.assertEqual(offspring.get_gene('agouti'), ('A', 'a'))
            self.assertEqual(offspring.get_gene('flaxen'), ('F', 'f'))

    def test_heterozygous_cross_ratios(self):
        """
        Test E/e × E/e produces ~25% E/E, 50% E/e, 25% e/e.

        Uses 1000 offspring to test statistical distribution.
        """
        parent1 = Horse.from_string(self._NEUTRAL.format(ext='E/e', ag='A/A', fl='F/F'))
        parent2 = Horse.from_string(self._NEUTRAL.format(ext='E/e', ag='A/A', fl='F/F'))

        counts = {'E/E': 0, 'E/e': 0, 'e/e': 0}
        for _ in range(1000):
            offspring = Horse.breed(parent1, parent2)
            ext = offspring.get_gene('extension')
            if ext == ('E', 'E'):
                counts['E/E'] += 1
            elif ext == ('E', 'e'):
                counts['E/e'] += 1
            elif ext == ('e', 'e'):
                counts['e/e'] += 1

        # Check ratios are approximately 1:2:1 (25%:50%:25%)
        # Allow 10% deviation due to randomness
        self.assertGreater(counts['E/E'], 150)  # ~25% of 1000 = 250, allow down to 150
        self.assertLess(counts['E/E'], 350)     # allow up to 350

        self.assertGreater(counts['E/e'], 350)  # ~50% of 1000 = 500, allow down to 350
        self.assertLess(counts['E/e'], 650)     # allow up to 650

        self.assertGreater(counts['e/e'], 150)  # ~25% of 1000 = 250
        self.assertLess(counts['e/e'], 350)

    def test_cream_inheritance(self):
        """Test cream inheritance: N/Cr × N/Cr produces Cr/Cr (Cremello) offspring."""
        parent1 = Horse.from_string(
            "E:e/e A:A/A Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/F STY:sty/sty G:g/g "
            "Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        parent2 = Horse.from_string(
            "E:e/e A:A/A Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/F STY:sty/sty G:g/g "
            "Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )

        got_double = False
        for _ in range(100):
            offspring = Horse.breed(parent1, parent2)
            if offspring.get_gene('dilution') == ('Cr', 'Cr'):
                got_double = True
                self.assertEqual(offspring.phenotype, 'Cremello')

        self.assertTrue(got_double, "Should produce some Cr/Cr offspring in 100 breedings")


class TestGenotypeFormatting(unittest.TestCase):
    """Test genotype formatting and parsing."""

    def setUp(self):
        """Initialize calculator and registry."""
        from genetics.gene_registry import get_default_registry
        self.calc = PhenotypeCalculator()
        self.registry = get_default_registry()

    def test_format_genotype(self):
        """Test genotype formatting for display."""
        genotype = {
            'extension': ('E', 'e'),
            'agouti': ('A', 'a'),
            'dilution': ('N', 'Cr'),
            'dun': ('D', 'nd2'),
            'silver': ('Z', 'n'),
            'champagne': ('Ch', 'n'),
            'flaxen': ('F', 'f'),
            'sooty': ('STY', 'sty'),
            'gray': ('G', 'g'),
            'roan': ('Rn', 'n'),
            'tobiano': ('To', 'n'),
            'frame': ('O', 'n'),
            'sabino': ('Sb1', 'n'),
            'dominant_white': ('W1', 'n'),
            'splash': ('Sw1', 'n'),
            'leopard': ('Lp', 'lp'),
            'patn1': ('PATN1', 'n')
        }
        formatted = self.registry.format_genotype(genotype)

        # Check all genes are present (format uses no space after colon)
        self.assertIn('E:E/e', formatted)
        self.assertIn('A:A/a', formatted)
        self.assertIn('Dil:N/Cr', formatted)
        self.assertIn('D:D/nd2', formatted)
        self.assertIn('Z:Z/n', formatted)
        self.assertIn('Ch:Ch/n', formatted)
        self.assertIn('F:F/f', formatted)
        self.assertIn('STY:STY/sty', formatted)
        self.assertIn('G:G/g', formatted)
        self.assertIn('Rn:Rn/n', formatted)
        self.assertIn('To:To/n', formatted)
        self.assertIn('O:O/n', formatted)
        self.assertIn('Sb:Sb1/n', formatted)
        self.assertIn('W:W1/n', formatted)
        self.assertIn('Spl:Sw1/n', formatted)
        self.assertIn('Lp:Lp/lp', formatted)
        self.assertIn('PATN1:PATN1/n', formatted)

    def test_parse_genotype_valid(self):
        """Test parsing valid genotype strings via Horse.from_string."""
        full_str = (
            "E:E/e A:A/a Dil:N/Cr D:D/nd2 Z:Z/n Ch:Ch/n F:F/f STY:STY/sty G:G/g "
            "Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        horse = Horse.from_string(full_str)

        self.assertEqual(horse.get_gene('extension'), ('E', 'e'))
        self.assertEqual(horse.get_gene('agouti'), ('A', 'a'))
        self.assertEqual(horse.get_gene('dilution'), ('N', 'Cr'))
        self.assertEqual(horse.get_gene('dun'), ('D', 'nd2'))
        self.assertEqual(horse.get_gene('silver'), ('Z', 'n'))
        self.assertEqual(horse.get_gene('champagne'), ('Ch', 'n'))
        self.assertEqual(horse.get_gene('flaxen'), ('F', 'f'))
        self.assertEqual(horse.get_gene('sooty'), ('STY', 'sty'))
        self.assertEqual(horse.get_gene('gray'), ('G', 'g'))

    def test_parse_genotype_invalid(self):
        """Test parsing invalid genotype strings raises ValueError."""
        # Invalid allele count (three alleles)
        with self.assertRaises(ValueError):
            Horse.from_string(
                "E:E/e/e A:A/a Dil:N/Cr D:D/nd2 Z:Z/n Ch:Ch/n F:F/f STY:STY/sty G:G/g "
                "Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
            )

        # Invalid allele value
        with self.assertRaises(ValueError):
            Horse.from_string(
                "E:X/Y A:A/a Dil:N/Cr D:D/nd2 Z:Z/n Ch:Ch/n F:F/f STY:STY/sty G:G/g "
                "Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
            )


class TestHorseAPI(unittest.TestCase):
    """
    Test Horse fluent API for game integration.

    Tests the new Horse class and its convenient methods.
    """

    def test_horse_random_generation(self):
        """Test Horse.random() creates valid horse."""
        from genetics.horse import Horse

        horse = Horse.random()

        # Should have phenotype
        self.assertIsInstance(horse.phenotype, str)
        self.assertTrue(len(horse.phenotype) > 0)

        # Should have genotype
        self.assertIsInstance(horse.genotype, dict)
        self.assertEqual(len(horse.genotype), 17)  # 17 genes (added white patterns + leopard + dominant white)

        # Should have genotype string
        self.assertIsInstance(horse.genotype_string, str)
        self.assertIn('E:', horse.genotype_string)

    def test_horse_from_string(self):
        """Test creating horse from genotype string."""
        from genetics.horse import Horse

        genotype_str = "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        horse = Horse.from_string(genotype_str)

        self.assertEqual(horse.genotype['extension'], ('E', 'e'))
        self.assertEqual(horse.genotype['dilution'], ('N', 'Cr'))
        self.assertIn('Buckskin', horse.phenotype)

    def test_horse_round_trip(self):
        """Test creating horse from string and converting back."""
        from genetics.horse import Horse

        original = Horse.random()
        string = original.genotype_string
        recreated = Horse.from_string(string)

        # Genotypes should match
        self.assertEqual(original.genotype, recreated.genotype)
        # Phenotypes should match
        self.assertEqual(original.phenotype, recreated.phenotype)

    def test_horse_breeding(self):
        """Test breeding two horses with fluent API."""
        from genetics.horse import Horse

        # Create specific parents
        mare_str = "E:E/e A:A/A Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/F STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        stallion_str = "E:e/e A:a/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:f/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"

        mare = Horse.from_string(mare_str)
        stallion = Horse.from_string(stallion_str)

        # Breed them
        foal = Horse.breed(mare, stallion)

        # Foal should exist with valid genotype
        self.assertIsNotNone(foal)
        self.assertEqual(len(foal.genotype), 17)

        # Extension should be E/e (mare E/e × stallion e/e)
        # Either E/e or e/e
        self.assertIn(foal.genotype['extension'], [('E', 'e'), ('e', 'e')])

    def test_horse_has_allele(self):
        """Test checking if horse has specific allele."""
        from genetics.horse import Horse

        horse_str = "E:E/E A:A/a Dil:N/Cr D:D/nd2 Z:Z/n Ch:n/n F:F/f STY:STY/sty G:G/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        horse = Horse.from_string(horse_str)

        # Should have E
        self.assertTrue(horse.has_allele('extension', 'E'))
        # Should not have e
        self.assertFalse(horse.has_allele('extension', 'e'))
        # Should have both A and a
        self.assertTrue(horse.has_allele('agouti', 'A'))
        self.assertTrue(horse.has_allele('agouti', 'a'))
        # Should have Gray
        self.assertTrue(horse.has_allele('gray', 'G'))

    def test_horse_is_homozygous(self):
        """Test checking if horse is homozygous for gene."""
        from genetics.horse import Horse

        horse_str = "E:E/E A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/F STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        horse = Horse.from_string(horse_str)

        # Extension is homozygous E/E
        self.assertTrue(horse.is_homozygous('extension'))
        # Agouti is heterozygous A/a
        self.assertFalse(horse.is_homozygous('agouti'))
        # Dilution is homozygous N/N
        self.assertTrue(horse.is_homozygous('dilution'))

    def test_horse_to_dict(self):
        """Test converting horse to dictionary."""
        from genetics.horse import Horse

        horse = Horse.random()
        data = horse.to_dict()

        # Should have required keys
        self.assertIn('genotype', data)
        self.assertIn('phenotype', data)
        self.assertIn('genotype_string', data)

        # Should be serializable
        import json
        json_str = json.dumps(data)  # Should not raise
        self.assertIsInstance(json_str, str)

    def test_horse_from_dict(self):
        """Test creating horse from dictionary."""
        from genetics.horse import Horse

        original = Horse.random()
        data = original.to_dict()

        # Create new horse from dict
        recreated = Horse.from_dict(data)

        self.assertEqual(original.genotype, recreated.genotype)
        self.assertEqual(original.phenotype, recreated.phenotype)

    def test_multiple_generation_breeding(self):
        """Test breeding multiple generations."""
        from genetics.horse import Horse

        # Generation 1
        mare1 = Horse.random()
        stallion1 = Horse.random()

        # Generation 2
        foal1 = Horse.breed(mare1, stallion1)
        foal2 = Horse.breed(mare1, stallion1)

        # Siblings may have different genotypes
        # (unless parents are homozygous for all genes)
        self.assertEqual(len(foal1.genotype), 17)
        self.assertEqual(len(foal2.genotype), 17)

        # Generation 3 - breed siblings
        foal3 = Horse.breed(foal1, foal2)
        self.assertEqual(len(foal3.genotype), 17)

    def test_convenience_functions(self):
        """Test convenience functions for functional style."""
        from genetics.horse import generate_random_horse, breed_horses, parse_horse

        # generate_random_horse
        horse1 = generate_random_horse()
        self.assertIsNotNone(horse1.phenotype)

        # breed_horses
        horse2 = generate_random_horse()
        foal = breed_horses(horse1, horse2)
        self.assertIsNotNone(foal.phenotype)

        # parse_horse
        genotype_str = "E:E/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/F STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        horse3 = parse_horse(genotype_str)
        self.assertEqual(horse3.genotype['extension'], ('E', 'e'))


class TestRoanGene(unittest.TestCase):
    """
    Test Roan gene (KIT).

    Scientific basis: Roan is controlled by KIT gene.
    Recent research (2020) shows Rn/Rn is viable, contrary to historical belief.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, roan, dilution=('N', 'N'),
                        dun=('nd2', 'nd2'), silver=('n', 'n'),
                        champagne=('n', 'n'), flaxen=('F', 'F'),
                        sooty=('sty', 'sty'), gray=('g', 'g'),
                        tobiano=('n', 'n'), frame=('n', 'n'),
                        sabino=('n', 'n'), dominant_white=('n', 'n'),
                        splash=('n', 'n'), leopard=('lp', 'lp'), patn1=('n', 'n')):
        """Helper to create genotype dictionaries."""
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            'dun': dun,
            'silver': silver,
            'champagne': champagne,
            'flaxen': flaxen,
            'sooty': sooty,
            'gray': gray,
            'roan': roan,
            'tobiano': tobiano,
            'frame': frame,
            'sabino': sabino,
            'dominant_white': dominant_white,
            'splash': splash,
            'leopard': leopard,
            'patn1': patn1
        }

    def test_bay_roan(self):
        """Test Bay Roan (E/_ A/_ Rn/n)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('Rn', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Roan')

    def test_chestnut_roan(self):
        """Test Chestnut Roan (e/e Rn/n) - often called Red Roan."""
        genotype = self._create_genotype(('e', 'e'), ('A', 'a'), ('Rn', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Chestnut Roan')

    def test_black_roan(self):
        """Test Black Roan (E/_ a/a Rn/n) - often called Blue Roan."""
        genotype = self._create_genotype(('E', 'E'), ('a', 'a'), ('Rn', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Black Roan')

    def test_homozygous_roan_viable(self):
        """Test that Rn/Rn is viable (based on recent research)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('Rn', 'Rn'))
        phenotype = self.calc.determine_phenotype(genotype)
        # Should be Bay Roan, not nonviable
        self.assertEqual(phenotype, 'Bay Roan')


class TestWhitePatterns(unittest.TestCase):
    """
    Test white spotting patterns (Tobiano, Overo, Sabino, Splash, Tovero).

    Scientific basis: Various white pattern genes create pinto/paint patterns.
    Tovero is the industry term for Tobiano + Overo combination.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, tobiano=('n', 'n'),
                        frame=('n', 'n'), sabino=('n', 'n'),
                        dominant_white=('n', 'n'),
                        splash=('n', 'n'), dilution=('N', 'N'),
                        dun=('nd2', 'nd2'), silver=('n', 'n'),
                        champagne=('n', 'n'), flaxen=('F', 'F'),
                        sooty=('sty', 'sty'), gray=('g', 'g'),
                        roan=('n', 'n'), leopard=('lp', 'lp'),
                        patn1=('n', 'n')):
        """Helper to create genotype dictionaries."""
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            'dun': dun,
            'silver': silver,
            'champagne': champagne,
            'flaxen': flaxen,
            'sooty': sooty,
            'gray': gray,
            'roan': roan,
            'tobiano': tobiano,
            'frame': frame,
            'sabino': sabino,
            'dominant_white': dominant_white,
            'splash': splash,
            'leopard': leopard,
            'patn1': patn1
        }

    def test_tobiano(self):
        """Test Tobiano pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), tobiano=('To', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Tobiano')

    def test_frame_overo(self):
        """Test Frame Overo pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), frame=('O', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Frame')

    def test_sabino(self):
        """Test Sabino pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), sabino=('Sb1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Sabino')

    def test_maximum_sabino(self):
        """Test homozygous Sabino (Maximum Sabino)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), sabino=('Sb1', 'Sb1'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Maximum Sabino')

    def test_splash_white(self):
        """Test Splash White pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), splash=('Sw1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Splash White')

    def test_tovero_tobiano_frame(self):
        """Test Tovero (Tobiano + Frame Overo)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), tobiano=('To', 'n'), frame=('O', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Tovero')

    def test_tovero_tobiano_sabino(self):
        """Test Tovero (Tobiano + Sabino)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), tobiano=('To', 'n'), sabino=('Sb1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Tovero')

    def test_tovero_tobiano_splash(self):
        """Test Tovero (Tobiano + Splash)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), tobiano=('To', 'n'), splash=('Sw1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Tovero')

    def test_multiple_overo_patterns(self):
        """Test multiple Overo patterns together (without Tobiano)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), frame=('O', 'n'), sabino=('Sb1', 'n'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Frame', phenotype)
        self.assertIn('Sabino', phenotype)

    def test_lethal_white_overo_syndrome(self):
        """Test that Frame Overo O/O is lethal (LWOS)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), frame=('O', 'O'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('NONVIABLE', phenotype)
        self.assertIn('LWOS', phenotype)


class TestLeopardComplex(unittest.TestCase):
    """
    Test Leopard Complex (Appaloosa) patterns.

    Scientific basis: TRPM1 gene (Lp) creates Appaloosa spotting.
    PATN1 modifies the pattern to create full leopard spotting.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, leopard, patn1,
                        dilution=('N', 'N'), dun=('nd2', 'nd2'),
                        silver=('n', 'n'), champagne=('n', 'n'),
                        flaxen=('F', 'F'), sooty=('sty', 'sty'),
                        gray=('g', 'g'), roan=('n', 'n'),
                        tobiano=('n', 'n'), frame=('n', 'n'),
                        sabino=('n', 'n'), dominant_white=('n', 'n'),
                        splash=('n', 'n')):
        """Helper to create genotype dictionaries."""
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            'dun': dun,
            'silver': silver,
            'champagne': champagne,
            'flaxen': flaxen,
            'sooty': sooty,
            'gray': gray,
            'roan': roan,
            'tobiano': tobiano,
            'frame': frame,
            'sabino': sabino,
            'dominant_white': dominant_white,
            'splash': splash,
            'leopard': leopard,
            'patn1': patn1
        }

    def test_leopard_heterozygous_with_patn1(self):
        """Test Lp/lp + PATN1 = Leopard pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('Lp', 'lp'), ('PATN1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Leopard')

    def test_leopard_homozygous_with_patn1(self):
        """Test Lp/Lp + PATN1 = Leopard pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('Lp', 'Lp'), ('PATN1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Leopard')

    def test_fewspot(self):
        """Test Lp/Lp without PATN1 = Fewspot."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('Lp', 'Lp'), ('n', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Fewspot')

    def test_blanket(self):
        """Test Lp/lp without PATN1 = Blanket."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('Lp', 'lp'), ('n', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay Blanket')

    def test_no_leopard(self):
        """Test lp/lp = no Appaloosa pattern."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('lp', 'lp'), ('n', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Bay')


class TestDominantWhite(unittest.TestCase):
    """
    Test Dominant White gene (KIT).

    Scientific basis: KIT gene mutations W1-W39.
    Most W alleles are lethal when homozygous, except W20.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dominant_white,
                        dilution=('N', 'N'), dun=('nd2', 'nd2'),
                        silver=('n', 'n'), champagne=('n', 'n'),
                        flaxen=('F', 'F'), sooty=('sty', 'sty'),
                        gray=('g', 'g'), roan=('n', 'n'),
                        tobiano=('n', 'n'), frame=('n', 'n'),
                        sabino=('n', 'n'), splash=('n', 'n'),
                        leopard=('lp', 'lp'), patn1=('n', 'n')):
        """Helper to create genotype dictionaries."""
        return {
            'extension': extension,
            'agouti': agouti,
            'dilution': dilution,
            'dun': dun,
            'silver': silver,
            'champagne': champagne,
            'flaxen': flaxen,
            'sooty': sooty,
            'gray': gray,
            'roan': roan,
            'tobiano': tobiano,
            'frame': frame,
            'sabino': sabino,
            'dominant_white': dominant_white,
            'splash': splash,
            'leopard': leopard,
            'patn1': patn1
        }

    def test_w1_heterozygous(self):
        """Test W1/n = Dominant White."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W1', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Dominant White (W1)')

    def test_w5_heterozygous(self):
        """Test W5/n = Dominant White."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W5', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Dominant White (W5)')

    def test_w20_heterozygous(self):
        """Test W20/n = Dominant White."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W20', 'n'))
        self.assertEqual(self.calc.determine_phenotype(genotype), 'Dominant White (W20)')

    def test_w20_homozygous_viable(self):
        """Test W20/W20 is viable (exception to lethality rule)."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W20', 'W20'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Dominant White', phenotype)
        self.assertNotIn('NONVIABLE', phenotype)

    def test_w1_homozygous_lethal(self):
        """Test W1/W1 is lethal."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W1', 'W1'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('NONVIABLE', phenotype)
        self.assertIn('W1/W1', phenotype)

    def test_w5_homozygous_lethal(self):
        """Test W5/W5 is lethal."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W5', 'W5'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('NONVIABLE', phenotype)

    def test_w10_homozygous_lethal(self):
        """Test W10/W10 is lethal."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W10', 'W10'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('NONVIABLE', phenotype)

    def test_w13_homozygous_lethal(self):
        """Test W13/W13 is lethal."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W13', 'W13'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('NONVIABLE', phenotype)

    def test_w22_homozygous_lethal(self):
        """Test W22/W22 is lethal."""
        genotype = self._create_genotype(('E', 'e'), ('A', 'a'), ('W22', 'W22'))
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('NONVIABLE', phenotype)


class TestSootyOnDoubleDilutes(unittest.TestCase):
    """Test that sooty modifier is masked on double-dilute horses.

    Scientific basis: Sooty darkens red pigment areas. Double dilutes
    (Cremello, Perlino, Smoky Cream) have extremely pale pigment where
    sooty darkening has no visible effect.
    Reference: HORSE_GENETICS_REFERENCE.md section 16 (Sooty).
    """

    def setUp(self):
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution=('N', 'N'),
                         dun=('nd2', 'nd2'), silver=('n', 'n'),
                         champagne=('n', 'n'), flaxen=('F', 'F'),
                         sooty=('sty', 'sty'), gray=('g', 'g'),
                         roan=('n', 'n'), tobiano=('n', 'n'),
                         frame=('n', 'n'), sabino=('n', 'n'),
                         dominant_white=('n', 'n'),
                         splash=('n', 'n'), leopard=('lp', 'lp'),
                         patn1=('n', 'n')):
        return {
            'extension': extension, 'agouti': agouti, 'dilution': dilution,
            'dun': dun, 'silver': silver, 'champagne': champagne,
            'flaxen': flaxen, 'sooty': sooty, 'gray': gray,
            'roan': roan, 'tobiano': tobiano, 'frame': frame,
            'sabino': sabino, 'dominant_white': dominant_white,
            'splash': splash, 'leopard': leopard, 'patn1': patn1
        }

    def test_sooty_not_on_cremello(self):
        """Sooty must not appear on Cremello (e/e + Cr/Cr).

        Cremello is a double dilute — no visible red pigment remains for
        sooty to darken. Phenotype must stay 'Cremello', not 'Sooty Cremello'.
        """
        genotype = self._create_genotype(
            ('e', 'e'), ('A', 'A'),
            dilution=('Cr', 'Cr'),
            sooty=('STY', 'sty')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertEqual(phenotype, 'Cremello')
        self.assertNotIn('Sooty', phenotype)

    def test_sooty_not_on_perlino(self):
        """Sooty must not appear on Perlino (E_ + A_ + Cr/Cr).

        Perlino (bay + double cream) has extremely diluted pigment.
        Sooty darkening is scientifically not visible on double dilutes.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('A', 'a'),
            dilution=('Cr', 'Cr'),
            sooty=('STY', 'sty')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertEqual(phenotype, 'Perlino')
        self.assertNotIn('Sooty', phenotype)

    def test_sooty_not_on_smoky_cream(self):
        """Sooty must not appear on Smoky Cream (E_ + aa + Cr/Cr).

        Smoky Cream (black + double cream) is too pale for sooty to show.
        Reference: Sooty 'EI NAKYVA: Double dilutes (Cremello, Perlino, Smoky Cream)'.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('a', 'a'),
            dilution=('Cr', 'Cr'),
            sooty=('STY', 'sty')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertEqual(phenotype, 'Smoky Cream')
        self.assertNotIn('Sooty', phenotype)


class TestFlaxenEdgeCases(unittest.TestCase):
    """Test flaxen gene edge cases.

    Scientific basis: Flaxen (locus unknown) is recessive.
    F/f heterozygotes are unaffected carriers — no visible change.
    f/f only lightens mane and tail on chestnut (e/e) horses.
    Reference: HORSE_GENETICS_REFERENCE.md section 15 (Flaxen).
    """

    def setUp(self):
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution=('N', 'N'),
                         dun=('nd2', 'nd2'), silver=('n', 'n'),
                         champagne=('n', 'n'), flaxen=('F', 'F'),
                         sooty=('sty', 'sty'), gray=('g', 'g'),
                         roan=('n', 'n'), tobiano=('n', 'n'),
                         frame=('n', 'n'), sabino=('n', 'n'),
                         dominant_white=('n', 'n'),
                         splash=('n', 'n'), leopard=('lp', 'lp'),
                         patn1=('n', 'n')):
        return {
            'extension': extension, 'agouti': agouti, 'dilution': dilution,
            'dun': dun, 'silver': silver, 'champagne': champagne,
            'flaxen': flaxen, 'sooty': sooty, 'gray': gray,
            'roan': roan, 'tobiano': tobiano, 'frame': frame,
            'sabino': sabino, 'dominant_white': dominant_white,
            'splash': splash, 'leopard': leopard, 'patn1': patn1
        }

    def test_flaxen_heterozygous_no_effect(self):
        """Heterozygous F/f carrier must NOT show flaxen phenotype.

        Flaxen is recessive: only f/f expresses the trait.
        F/f is a silent carrier — horse looks like a plain Chestnut.
        Reference: 'F/f: EI nakyva vaikutusta (kantaja)'.
        """
        genotype = self._create_genotype(
            ('e', 'e'), ('A', 'A'),
            flaxen=('F', 'f')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertNotIn('Flaxen', phenotype)

    def test_flaxen_on_palomino(self):
        """Flaxen f/f on Palomino (chestnut + N/Cr) should produce Palomino.

        Palomino is a diluted chestnut (e/e). Flaxen further lightens the
        mane/tail. The result should still be identified as a Palomino.
        """
        genotype = self._create_genotype(
            ('e', 'e'), ('A', 'A'),
            dilution=('N', 'Cr'),
            flaxen=('f', 'f')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Palomino', phenotype)

    def test_flaxen_on_red_dun(self):
        """Flaxen f/f on Red Dun (chestnut + Dun) should note the modifier.

        Red Dun is chestnut (e/e) with Dun dilution. Since base is e/e,
        flaxen applies and should be reflected in phenotype or at minimum
        the base Red Dun identification must be correct.
        """
        genotype = self._create_genotype(
            ('e', 'e'), ('A', 'A'),
            dun=('D', 'nd2'),
            flaxen=('f', 'f')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertTrue(
            'Red Dun' in phenotype or 'Dun' in phenotype,
            f"Expected Red Dun base color, got: {phenotype}"
        )


class TestDunCombinations(unittest.TestCase):
    """Test Dun gene combined with dilution and silver genes.

    Scientific basis: TBX3 locus. Dun dilutes coat and adds primitive
    markings (dorsal stripe, leg bars). Industry names for combinations:
    - Chestnut + Cream + Dun = Dunalino
    - Bay + Cream + Dun = Dunskin
    - Black + Cream + Dun = Smoky Grullo
    - Black + Silver + Dun = Silver Grullo
    Reference: HORSE_GENETICS_REFERENCE.md section 4 (Dun).
    """

    def setUp(self):
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution=('N', 'N'),
                         dun=('nd2', 'nd2'), silver=('n', 'n'),
                         champagne=('n', 'n'), flaxen=('F', 'F'),
                         sooty=('sty', 'sty'), gray=('g', 'g'),
                         roan=('n', 'n'), tobiano=('n', 'n'),
                         frame=('n', 'n'), sabino=('n', 'n'),
                         dominant_white=('n', 'n'),
                         splash=('n', 'n'), leopard=('lp', 'lp'),
                         patn1=('n', 'n')):
        return {
            'extension': extension, 'agouti': agouti, 'dilution': dilution,
            'dun': dun, 'silver': silver, 'champagne': champagne,
            'flaxen': flaxen, 'sooty': sooty, 'gray': gray,
            'roan': roan, 'tobiano': tobiano, 'frame': frame,
            'sabino': sabino, 'dominant_white': dominant_white,
            'splash': splash, 'leopard': leopard, 'patn1': patn1
        }

    def test_dunalino(self):
        """Chestnut + N/Cr + Dun must produce Dunalino.

        Dunalino = Palomino + Dun. Dun over a palomino creates a very
        pale yellow horse with primitive markings (dorsal stripe).
        """
        genotype = self._create_genotype(
            ('e', 'e'), ('A', 'A'),
            dilution=('N', 'Cr'),
            dun=('D', 'nd2')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Dunalino', phenotype)

    def test_dunskin(self):
        """Bay + N/Cr + Dun must produce Dunskin.

        Dunskin = Buckskin + Dun. Bay horse with one cream allele and
        one Dun allele produces a distinctly primitive buckskin.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('A', 'a'),
            dilution=('N', 'Cr'),
            dun=('D', 'nd2')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Dunskin', phenotype)

    def test_smoky_grullo(self):
        """Black + N/Cr + Dun must produce Smoky Grullo.

        Grullo = Black + Dun. Adding one cream allele to a Grullo creates
        Smoky Grullo — a rare and distinctive combination.
        Reference: 'Smoky Black + D/_ = Smoky Grullo'.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('a', 'a'),
            dilution=('N', 'Cr'),
            dun=('D', 'nd2')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Grullo', phenotype)

    def test_silver_grullo(self):
        """Black + Silver + Dun must produce a Silver Grullo.

        Silver (Z) dilutes black pigment, especially mane and tail.
        Dun over black = Grullo. Combined: Silver Grullo.
        Note: Silver has no visible effect on chestnut (e/e) horses.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('a', 'a'),
            silver=('Z', 'n'),
            dun=('D', 'nd2')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Grullo', phenotype)
        self.assertIn('Silver', phenotype)


class TestPATN1WithoutLeopard(unittest.TestCase):
    """Test that PATN1 has no visible effect without an Lp allele.

    Scientific basis: PATN1 modifies the Leopard Complex (TRPM1) pattern.
    Without at least one Lp allele, PATN1 produces no visible spotting.
    Reference: 'PATN1 ilman Lp: EI nakyva vaikutusta'.
    """

    def setUp(self):
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution=('N', 'N'),
                         dun=('nd2', 'nd2'), silver=('n', 'n'),
                         champagne=('n', 'n'), flaxen=('F', 'F'),
                         sooty=('sty', 'sty'), gray=('g', 'g'),
                         roan=('n', 'n'), tobiano=('n', 'n'),
                         frame=('n', 'n'), sabino=('n', 'n'),
                         dominant_white=('n', 'n'),
                         splash=('n', 'n'), leopard=('lp', 'lp'),
                         patn1=('n', 'n')):
        return {
            'extension': extension, 'agouti': agouti, 'dilution': dilution,
            'dun': dun, 'silver': silver, 'champagne': champagne,
            'flaxen': flaxen, 'sooty': sooty, 'gray': gray,
            'roan': roan, 'tobiano': tobiano, 'frame': frame,
            'sabino': sabino, 'dominant_white': dominant_white,
            'splash': splash, 'leopard': leopard, 'patn1': patn1
        }

    def test_patn1_no_effect_without_lp(self):
        """PATN1/PATN1 with no Lp allele must produce a solid Bay horse.

        Epistatic rule: PATN1 is only expressed when at least one Lp
        allele is present. Without Lp, PATN1/PATN1 = plain Bay.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('A', 'a'),
            leopard=('lp', 'lp'),
            patn1=('PATN1', 'PATN1')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertEqual(phenotype, 'Bay')
        self.assertNotIn('Appaloosa', phenotype)
        self.assertNotIn('Leopard', phenotype)
        self.assertNotIn('Blanket', phenotype)


class TestBreedingStats(unittest.TestCase):
    """Test breeding probability calculations (BUG-09 fix verification).

    Scientific basis: Mendelian inheritance — each parent contributes
    one random allele per locus with equal probability.

    BUG-09: calculate_gene_probabilities() used alphabetical sorted()
    instead of dominance-based sort_alleles(). This caused key mismatch:
    - alphabetical: ('e', 'E') because ord('e')=101 > ord('E')=69
    - dominance:    ('E', 'e') because E dominance_order=10 > e=1
    Lookups then returned 0.0 instead of the correct probability.
    """

    def setUp(self):
        self.registry = get_default_registry()
        self.ext_gene = self.registry.get_gene('extension')

    def test_homozygous_cross_all_heterozygous(self):
        """E/E x e/e must produce 100% E/e offspring for extension gene."""
        probs = calculate_gene_probabilities(
            ('E', 'E'), ('e', 'e'), self.ext_gene
        )
        self.assertAlmostEqual(probs.get(('E', 'e'), 0.0), 1.0, places=5)
        self.assertEqual(len(probs), 1)

    def test_heterozygous_cross_ratios(self):
        """E/e x E/e must produce 25% E/E, 50% E/e, 25% e/e (Mendel's law)."""
        probs = calculate_gene_probabilities(
            ('E', 'e'), ('E', 'e'), self.ext_gene
        )
        self.assertAlmostEqual(probs.get(('E', 'E'), 0.0), 0.25, places=5)
        self.assertAlmostEqual(probs.get(('E', 'e'), 0.0), 0.50, places=5)
        self.assertAlmostEqual(probs.get(('e', 'e'), 0.0), 0.25, places=5)

    def test_dominance_sorted_keys(self):
        """Keys must be sorted by dominance order, not alphabetically.

        BUG-09: alphabetical reverse sort gives ('e', 'E') because
        ord('e')=101 > ord('E')=69. Dominance sort gives ('E', 'e')
        because E has dominance_order=10 and e has dominance_order=1.
        """
        probs = calculate_gene_probabilities(
            ('E', 'e'), ('E', 'e'), self.ext_gene
        )
        self.assertIn(('E', 'e'), probs,
                      "Expected dominance-sorted key ('E','e') in probabilities")
        self.assertNotIn(('e', 'E'), probs,
                         "Found alphabetically sorted key ('e','E') — BUG-09 not fixed")

    def test_single_gene_probability_lookup(self):
        """calculate_single_gene_probability must return correct probability.

        BUG-09: After the fix, E/e x E/e should return 0.50 for target ('E','e').
        Before fix it returned 0.0 due to key mismatch in the probability dict.
        """
        parent_str = (
            "E:E/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n "
            "F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n "
            "Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        prob = calculate_single_gene_probability(
            parent_str, parent_str, 'extension', ('E', 'e')
        )
        self.assertAlmostEqual(prob, 0.50, places=5,
                               msg="BUG-09: E/e x E/e should give 50% E/e offspring")

    def test_guaranteed_traits(self):
        """e/e x e/e must guarantee e/e extension in all offspring.

        When both parents are homozygous e/e, every offspring must be e/e.
        get_guaranteed_traits() should detect and return this certainty.
        """
        chestnut_genotype = {
            'extension': ('e', 'e'), 'agouti': ('A', 'a'),
            'dilution': ('N', 'N'), 'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'), 'champagne': ('n', 'n'),
            'flaxen': ('F', 'f'), 'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'), 'roan': ('n', 'n'),
            'tobiano': ('n', 'n'), 'frame': ('n', 'n'),
            'sabino': ('n', 'n'), 'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'), 'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        chestnut2_genotype = {
            'extension': ('e', 'e'), 'agouti': ('a', 'a'),
            'dilution': ('N', 'N'), 'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'), 'champagne': ('n', 'n'),
            'flaxen': ('f', 'f'), 'sooty': ('sty', 'sty'),
            'gray': ('g', 'g'), 'roan': ('n', 'n'),
            'tobiano': ('n', 'n'), 'frame': ('n', 'n'),
            'sabino': ('n', 'n'), 'dominant_white': ('n', 'n'),
            'splash': ('n', 'n'), 'leopard': ('lp', 'lp'),
            'patn1': ('n', 'n')
        }
        guaranteed = get_guaranteed_traits(
            chestnut_genotype, chestnut2_genotype, self.registry
        )
        self.assertIn('extension', guaranteed,
                      "e/e x e/e should guarantee extension genotype")
        self.assertEqual(guaranteed['extension'], 'e/e')


class TestCSVRoundTrip(unittest.TestCase):
    """Test CSV export functionality (BUG-03 fix verification).

    BUG-03: The original CSV export used wrong gene names ('Extension'
    capitalized, 'Cream' instead of 'dilution') and only exported 9 genes
    instead of all 17. The fixed version uses lowercase keys with gene_ prefix.
    """

    def setUp(self):
        self.horse = Horse.from_string(
            "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n "
            "F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n "
            "Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        self.temp_file = tempfile.mktemp(suffix='.csv')

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def _get_csv_header(self):
        """Export horse to temp CSV and return the header row."""
        horses_to_csv([self.horse], self.temp_file)
        with open(self.temp_file, 'r') as f:
            reader = csv.reader(f)
            return next(reader)

    def test_export_has_17_genes(self):
        """CSV export must contain columns for all 17 genes.

        BUG-03: Only 9 genes were exported. Fixed version exports all 17
        using gene_<name> columns.
        """
        expected_gene_keys = [
            'extension', 'agouti', 'dilution', 'dun', 'silver',
            'champagne', 'flaxen', 'sooty', 'gray', 'roan',
            'tobiano', 'frame', 'sabino', 'dominant_white',
            'splash', 'leopard', 'patn1'
        ]
        header = self._get_csv_header()
        for gene in expected_gene_keys:
            col = f'gene_{gene}'
            self.assertIn(col, header, f"Missing CSV column: {col}")

    def test_export_correct_keys(self):
        """CSV must use lowercase gene names with gene_ prefix.

        BUG-03: CSV used 'Extension' (capitalized, wrong) and 'Cream'
        (wrong gene name) instead of 'gene_extension' and 'gene_dilution'.
        """
        header = self._get_csv_header()
        self.assertIn('gene_extension', header)
        self.assertIn('gene_dilution', header)
        self.assertNotIn('gene_Extension', header,
                         "Capitalized key found — BUG-03 not fixed")
        self.assertNotIn('gene_Cream', header,
                         "Wrong key 'Cream' found — BUG-03 not fixed")

    def test_import_export_round_trip(self):
        """Export horse to CSV, reconstruct from CSV — phenotype must match.

        Verifies that exported genotype data is sufficient and correct
        to fully reconstruct a Horse object with identical phenotype.
        """
        original_phenotype = self.horse.phenotype
        horses_to_csv([self.horse], self.temp_file)

        gene_names = [
            'extension', 'agouti', 'dilution', 'dun', 'silver',
            'champagne', 'flaxen', 'sooty', 'gray', 'roan',
            'tobiano', 'frame', 'sabino', 'dominant_white',
            'splash', 'leopard', 'patn1'
        ]
        with open(self.temp_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        genotype = {}
        for gene in gene_names:
            col = f'gene_{gene}'
            if col in row:
                alleles = tuple(row[col].split('/'))
                genotype[gene] = alleles

        reconstructed = Horse.from_dict({'genotype': genotype})
        self.assertEqual(reconstructed.phenotype, original_phenotype,
                         "Phenotype changed after CSV round-trip — data loss in export")


class TestLethalBreedingOutcomes(unittest.TestCase):
    """Test that breeding carrier horses can produce lethal offspring.

    Scientific basis:
    - Frame Overo O/n x O/n = 25% O/O offspring = Lethal White Overo (LWOS)
    - W1/n x W1/n = 25% W1/W1 offspring = embryonic lethal
    Reference: HORSE_GENETICS_REFERENCE.md section 'Letaalit kombinaatiot'.
    """

    def test_frame_carrier_breeding_can_produce_lwos(self):
        """O/n x O/n breeding must produce some NONVIABLE/LWOS offspring.

        25% of offspring from two Frame Overo carriers will be O/O,
        which causes Lethal White Overo Syndrome (LWOS). With 400
        simulations, at least one NONVIABLE foal is virtually certain.
        """
        parent1 = Horse.from_string(
            "E:E/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n "
            "F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:O/n "
            "Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        parent2 = Horse.from_string(
            "E:e/e A:a/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n "
            "F:f/f STY:sty/sty G:g/g Rn:n/n To:n/n O:O/n "
            "Sb:n/n W:n/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        nonviable_count = sum(
            1 for _ in range(400)
            if 'NONVIABLE' in Horse.breed(parent1, parent2).phenotype
        )
        self.assertGreater(
            nonviable_count, 0,
            "Expected NONVIABLE (LWOS) offspring from O/n x O/n — none produced in 400 trials"
        )

    def test_w1_carrier_breeding_can_produce_lethal(self):
        """W1/n x W1/n must produce some NONVIABLE offspring.

        25% of W1/n x W1/n offspring are W1/W1 = embryonic lethal.
        With 400 simulations, at least one lethal foal is virtually certain.
        """
        parent1 = Horse.from_string(
            "E:E/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n "
            "F:F/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n "
            "Sb:n/n W:W1/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        parent2 = Horse.from_string(
            "E:e/e A:a/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n "
            "F:f/f STY:sty/sty G:g/g Rn:n/n To:n/n O:n/n "
            "Sb:n/n W:W1/n Spl:n/n Lp:lp/lp PATN1:n/n"
        )
        nonviable_count = sum(
            1 for _ in range(400)
            if 'NONVIABLE' in Horse.breed(parent1, parent2).phenotype
        )
        self.assertGreater(
            nonviable_count, 0,
            "Expected NONVIABLE offspring from W1/n x W1/n — none produced in 400 trials"
        )


class TestMultiGeneInteractions(unittest.TestCase):
    """Test interactions between multiple genes simultaneously.

    Scientific basis: Multiple genes interact to create rare but real coat
    color combinations documented in equine genetics literature.
    """

    def setUp(self):
        self.calc = PhenotypeCalculator()

    def _create_genotype(self, extension, agouti, dilution=('N', 'N'),
                         dun=('nd2', 'nd2'), silver=('n', 'n'),
                         champagne=('n', 'n'), flaxen=('F', 'F'),
                         sooty=('sty', 'sty'), gray=('g', 'g'),
                         roan=('n', 'n'), tobiano=('n', 'n'),
                         frame=('n', 'n'), sabino=('n', 'n'),
                         dominant_white=('n', 'n'),
                         splash=('n', 'n'), leopard=('lp', 'lp'),
                         patn1=('n', 'n')):
        return {
            'extension': extension, 'agouti': agouti, 'dilution': dilution,
            'dun': dun, 'silver': silver, 'champagne': champagne,
            'flaxen': flaxen, 'sooty': sooty, 'gray': gray,
            'roan': roan, 'tobiano': tobiano, 'frame': frame,
            'sabino': sabino, 'dominant_white': dominant_white,
            'splash': splash, 'leopard': leopard, 'patn1': patn1
        }

    def test_cream_champagne_combination(self):
        """Bay + Cream + Champagne must include Champagne and Amber in phenotype.

        Champagne dilutes both pigment types and creates amber eyes / pink skin.
        Adding one Cream allele to an Amber Champagne (bay + Ch) creates
        an 'Amber Cream Champagne' — a recognizable compound dilute.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('A', 'a'),
            dilution=('N', 'Cr'),
            champagne=('Ch', 'n')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Champagne', phenotype)
        self.assertIn('Amber', phenotype)

    def test_silver_champagne_combination(self):
        """Black + Silver + Champagne must include Champagne in phenotype.

        Both Silver (PMEL17) and Champagne (SLC36A1) affect eumelanin.
        Combined on a black horse: Silver creates chocolate tones,
        Champagne creates pale skin and amber eyes.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('a', 'a'),
            silver=('Z', 'n'),
            champagne=('Ch', 'n')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Champagne', phenotype)

    def test_gray_with_leopard_complex(self):
        """Gray + Lp/lp horse must mention Gray in phenotype.

        Gray (STX17) is dominant and progressively depigments the horse.
        A horse born with Lp/lp shows Appaloosa pattern before graying.
        The phenotype should acknowledge the Gray gene at minimum.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('A', 'a'),
            gray=('G', 'g'),
            leopard=('Lp', 'lp')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Gray', phenotype)

    def test_roan_with_tobiano(self):
        """Roan + Tobiano combination must include both in phenotype.

        A horse can carry both Roan (KIT) and Tobiano (KIT inversion)
        simultaneously. The phenotype should acknowledge both patterns.
        """
        genotype = self._create_genotype(
            ('E', 'e'), ('A', 'a'),
            roan=('Rn', 'n'),
            tobiano=('To', 'n')
        )
        phenotype = self.calc.determine_phenotype(genotype)
        self.assertIn('Roan', phenotype)
        self.assertIn('Tobiano', phenotype)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBasicColors))
    suite.addTests(loader.loadTestsFromTestCase(TestCreamDilution))
    suite.addTests(loader.loadTestsFromTestCase(TestPearlDilution))
    suite.addTests(loader.loadTestsFromTestCase(TestChampagneDilution))
    suite.addTests(loader.loadTestsFromTestCase(TestSilverDilution))
    suite.addTests(loader.loadTestsFromTestCase(TestDunGene))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaxenAndSooty))
    suite.addTests(loader.loadTestsFromTestCase(TestGrayGene))
    suite.addTests(loader.loadTestsFromTestCase(TestRoanGene))
    suite.addTests(loader.loadTestsFromTestCase(TestWhitePatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestDominantWhite))
    suite.addTests(loader.loadTestsFromTestCase(TestLeopardComplex))
    suite.addTests(loader.loadTestsFromTestCase(TestBreeding))
    suite.addTests(loader.loadTestsFromTestCase(TestGenotypeFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestHorseAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestSootyOnDoubleDilutes))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaxenEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDunCombinations))
    suite.addTests(loader.loadTestsFromTestCase(TestPATN1WithoutLeopard))
    suite.addTests(loader.loadTestsFromTestCase(TestBreedingStats))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVRoundTrip))
    suite.addTests(loader.loadTestsFromTestCase(TestLethalBreedingOutcomes))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiGeneInteractions))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
