"""
Comprehensive unit tests for horse coat color genetics simulator.

These tests verify scientific accuracy of genetic inheritance and phenotype
determination based on peer-reviewed equine genetics research.
"""

import unittest
import os
from genetics.core import GenePool
from genetics.phenotype import PhenotypeCalculator as LegacyPhenotypeCalculator
from genetics.gene_interaction import PhenotypeCalculator
from genetics.breeding import BreedingSimulator
from genetics.visualizer import HorseVisualizer
from genetics.horse import Horse


class TestGenePool(unittest.TestCase):
    """Test core genetic operations and allele management."""

    def setUp(self):
        """Initialize gene pool for each test."""
        self.gene_pool = GenePool()

    def test_allele_definitions(self):
        """Test that all alleles are correctly defined."""
        self.assertEqual(self.gene_pool.extension_alleles, ['E', 'e'])
        self.assertEqual(self.gene_pool.agouti_alleles, ['A', 'a'])
        self.assertEqual(self.gene_pool.dilution_alleles, ['N', 'Cr', 'Prl'])
        self.assertEqual(self.gene_pool.dun_alleles, ['D', 'nd1', 'nd2'])
        self.assertEqual(self.gene_pool.silver_alleles, ['Z', 'n'])
        self.assertEqual(self.gene_pool.champagne_alleles, ['Ch', 'n'])
        self.assertEqual(self.gene_pool.flaxen_alleles, ['F', 'f'])
        self.assertEqual(self.gene_pool.sooty_alleles, ['STY', 'sty'])

    def test_allele_sorting_extension(self):
        """Test alleles are sorted by dominance (Extension gene)."""
        sorted_pair = self.gene_pool._sort_alleles(['e', 'E'])
        self.assertEqual(sorted_pair, ('E', 'e'))

    def test_allele_sorting_dilution(self):
        """Test dilution alleles sort correctly: N > Cr > Prl."""
        self.assertEqual(self.gene_pool._sort_alleles(['Prl', 'N']), ('N', 'Prl'))
        self.assertEqual(self.gene_pool._sort_alleles(['Prl', 'Cr']), ('Cr', 'Prl'))
        self.assertEqual(self.gene_pool._sort_alleles(['Cr', 'N']), ('N', 'Cr'))

    def test_allele_sorting_dun(self):
        """Test dun alleles sort correctly: D > nd1 > nd2."""
        self.assertEqual(self.gene_pool._sort_alleles(['nd2', 'D']), ('D', 'nd2'))
        self.assertEqual(self.gene_pool._sort_alleles(['nd2', 'nd1']), ('nd1', 'nd2'))
        self.assertEqual(self.gene_pool._sort_alleles(['nd1', 'D']), ('D', 'nd1'))

    def test_count_alleles(self):
        """Test allele counting in genotypes."""
        self.assertEqual(self.gene_pool.count_alleles(('E', 'e'), 'E'), 1)
        self.assertEqual(self.gene_pool.count_alleles(('e', 'e'), 'E'), 0)
        self.assertEqual(self.gene_pool.count_alleles(('Cr', 'Cr'), 'Cr'), 2)

    def test_random_genotype_structure(self):
        """Test random genotype contains all required genes (legacy system)."""
        genotype = self.gene_pool.generate_random_genotype()
        # Legacy GenePool only has the original 9 genes
        required_genes = ['extension', 'agouti', 'dilution', 'dun',
                         'silver', 'champagne', 'flaxen', 'sooty', 'gray']
        for gene in required_genes:
            self.assertIn(gene, genotype)
            self.assertEqual(len(genotype[gene]), 2)


class TestBasicColors(unittest.TestCase):
    """
    Test base coat colors (chestnut, bay, black).

    Scientific basis: MC1R (Extension) and ASIP (Agouti) interactions.
    """

    def setUp(self):
        """Initialize calculator for each test."""
        self.calc = PhenotypeCalculator()
        self.gene_pool = GenePool()

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

    def setUp(self):
        """Initialize breeding simulator."""
        self.simulator = BreedingSimulator()

    def test_homozygous_cross_produces_heterozygous(self):
        """Test E/E × e/e produces all E/e offspring."""
        parent1 = {
            'extension': ('E', 'E'),
            'agouti': ('A', 'A'),
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g')
        }
        parent2 = {
            'extension': ('e', 'e'),
            'agouti': ('a', 'a'),
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('f', 'f'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g')
        }

        # Test 100 offspring - all should be heterozygous
        for _ in range(100):
            offspring = self.simulator.breed_horses(parent1, parent2)
            # Extension: all E/e
            self.assertEqual(offspring['extension'], ('E', 'e'))
            # Agouti: all A/a
            self.assertEqual(offspring['agouti'], ('A', 'a'))
            # Flaxen: all F/f
            self.assertEqual(offspring['flaxen'], ('F', 'f'))

    def test_heterozygous_cross_ratios(self):
        """
        Test E/e × E/e produces ~25% E/E, 50% E/e, 25% e/e.

        Uses 1000 offspring to test statistical distribution.
        """
        parent1 = {
            'extension': ('E', 'e'),
            'agouti': ('A', 'A'),
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g')
        }
        parent2 = {
            'extension': ('E', 'e'),
            'agouti': ('A', 'A'),
            'dilution': ('N', 'N'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g')
        }

        # Count genotypes in 1000 offspring
        counts = {'E/E': 0, 'E/e': 0, 'e/e': 0}
        for _ in range(1000):
            offspring = self.simulator.breed_horses(parent1, parent2)
            ext = offspring['extension']
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
        """Test cream inheritance: Cr/N × Cr/N produces Cr/Cr offspring."""
        parent1 = {
            'extension': ('e', 'e'),
            'agouti': ('A', 'A'),
            'dilution': ('N', 'Cr'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g')
        }
        parent2 = {
            'extension': ('e', 'e'),
            'agouti': ('A', 'A'),
            'dilution': ('N', 'Cr'),
            'dun': ('nd2', 'nd2'),
            'silver': ('n', 'n'),
            'champagne': ('n', 'n'),
            'flaxen': ('F', 'F'),
            'sooty': ('sty', 'sty'),
            'gray': ('g', 'g')
        }

        # Test 100 breedings - should get some Cr/Cr offspring
        got_double = False
        for _ in range(100):
            offspring = self.simulator.breed_horses(parent1, parent2)
            if offspring['dilution'] == ('Cr', 'Cr'):
                got_double = True
                # Verify phenotype is cremello
                phenotype = self.simulator.phenotype_calculator.determine_phenotype(offspring)
                self.assertEqual(phenotype, 'Cremello')

        self.assertTrue(got_double, "Should produce some Cr/Cr offspring in 100 breedings")


class TestGenotypeFormatting(unittest.TestCase):
    """Test genotype formatting and parsing."""

    def setUp(self):
        """Initialize calculator and simulator."""
        from genetics.gene_registry import get_default_registry
        self.calc = PhenotypeCalculator()
        self.simulator = BreedingSimulator()
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
        """Test parsing valid genotype strings."""
        genotype_str = "E:E/e A:A/a Dil:N/Cr D:D/nd2 Z:Z/n Ch:Ch/n F:F/f STY:STY/sty G:G/g"
        genotype = self.simulator.parse_genotype_input(genotype_str)

        self.assertEqual(genotype['extension'], ('E', 'e'))
        self.assertEqual(genotype['agouti'], ('A', 'a'))
        self.assertEqual(genotype['dilution'], ('N', 'Cr'))
        self.assertEqual(genotype['dun'], ('D', 'nd2'))
        self.assertEqual(genotype['silver'], ('Z', 'n'))
        self.assertEqual(genotype['champagne'], ('Ch', 'n'))
        self.assertEqual(genotype['flaxen'], ('F', 'f'))
        self.assertEqual(genotype['sooty'], ('STY', 'sty'))
        self.assertEqual(genotype['gray'], ('G', 'g'))

    def test_parse_genotype_invalid(self):
        """Test parsing invalid genotype strings raises ValueError."""
        # Missing gene
        with self.assertRaises(ValueError):
            self.simulator.parse_genotype_input("E:E/e A:A/a")

        # Invalid allele count
        with self.assertRaises(ValueError):
            self.simulator.parse_genotype_input("E:E/e/e A:A/a Dil:N/Cr D:D/nd2 Z:Z/n Ch:Ch/n F:F/f STY:STY/sty")


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


class TestVisualizer(unittest.TestCase):
    """Test horse visualization functionality."""

    def setUp(self):
        """Initialize visualizer for each test."""
        self.visualizer = HorseVisualizer()

    def test_generate_svg_returns_string(self):
        """Test that generate_svg returns a string."""
        svg = self.visualizer.generate_svg("Bay")
        self.assertIsInstance(svg, str)
        self.assertIn('<?xml', svg)
        self.assertIn('svg', svg)

    def test_svg_contains_phenotype_label(self):
        """Test that SVG contains the phenotype label."""
        svg = self.visualizer.generate_svg("Chestnut Roan")
        self.assertIn('Chestnut Roan', svg)

    def test_base_color_bay(self):
        """Test Bay color is correctly mapped."""
        svg = self.visualizer.generate_svg("Bay")
        self.assertIn('#654321', svg)  # Bay brown color

    def test_base_color_chestnut(self):
        """Test Chestnut color is correctly mapped."""
        svg = self.visualizer.generate_svg("Chestnut")
        self.assertIn('#8b4513', svg)  # Chestnut brown color

    def test_white_pattern_detection(self):
        """Test white patterns are detected and rendered."""
        svg = self.visualizer.generate_svg("Bay Tobiano")
        # Pixel art should have rect elements and white (#ffffff) pixels for pattern
        self.assertIn('rect', svg)
        self.assertIn('Bay Tobiano', svg)  # Phenotype label

    def test_leopard_pattern_detection(self):
        """Test leopard patterns are detected and rendered."""
        svg = self.visualizer.generate_svg("Bay Leopard")
        # Pixel art should contain the phenotype and spots
        self.assertIn('rect', svg)
        self.assertIn('Leopard', svg)

    def test_roan_pattern_detection(self):
        """Test roan patterns are detected and rendered."""
        svg = self.visualizer.generate_svg("Bay Roan")
        # Pixel art should have rect elements for roan pattern
        self.assertIn('rect', svg)
        self.assertIn('Roan', svg)  # Phenotype label

    def test_dominant_white_renders_white(self):
        """Test Dominant White renders as pure white."""
        svg = self.visualizer.generate_svg("Dominant White (W20)")
        self.assertIn('#ffffff', svg)  # Pure white color

    def test_save_svg_creates_file(self):
        """Test that save_svg creates a file."""
        test_file = "test_output.svg"
        try:
            self.visualizer.save_svg("Bay", test_file)
            self.assertTrue(os.path.exists(test_file))

            # Verify file contents
            with open(test_file, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('Bay', content)
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_horse_visualize_method(self):
        """Test Horse.visualize() method works."""
        horse = Horse.random()
        test_file = "test_horse_viz.svg"
        try:
            result = horse.visualize(test_file)
            self.assertEqual(result, test_file)
            self.assertTrue(os.path.exists(test_file))

            # Verify file contains horse phenotype
            with open(test_file, 'r') as f:
                content = f.read()
                self.assertIn(horse.phenotype, content)
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGenePool))
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
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizer))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
