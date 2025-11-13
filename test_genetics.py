"""
Comprehensive unit tests for horse coat color genetics simulator.

These tests verify scientific accuracy of genetic inheritance and phenotype
determination based on peer-reviewed equine genetics research.
"""

import unittest
from genetics.core import GenePool
from genetics.phenotype import PhenotypeCalculator
from genetics.breeding import BreedingSimulator


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
        """Test random genotype contains all required genes."""
        genotype = self.gene_pool.generate_random_genotype()
        required_genes = ['extension', 'agouti', 'dilution', 'dun',
                         'silver', 'champagne', 'flaxen', 'sooty']
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
                        sooty=('sty', 'sty'), gray=('g', 'g')):
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
            'gray': gray
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
            'gray': ('g', 'g')
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
            'gray': ('g', 'g')
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
            'gray': ('g', 'g')
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
            'gray': ('g', 'g')
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
            'gray': ('g', 'g')
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
            'gray': ('g', 'g')
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
        self.calc = PhenotypeCalculator()
        self.simulator = BreedingSimulator()

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
            'gray': ('G', 'g')
        }
        formatted = self.calc.format_genotype(genotype)

        # Check all genes are present
        self.assertIn('E: E/e', formatted)
        self.assertIn('A: A/a', formatted)
        self.assertIn('Dil: N/Cr', formatted)
        self.assertIn('D: D/nd2', formatted)
        self.assertIn('Z: Z/n', formatted)
        self.assertIn('Ch: Ch/n', formatted)
        self.assertIn('F: F/f', formatted)
        self.assertIn('STY: STY/sty', formatted)
        self.assertIn('G: G/g', formatted)

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
    suite.addTests(loader.loadTestsFromTestCase(TestBreeding))
    suite.addTests(loader.loadTestsFromTestCase(TestGenotypeFormatting))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
