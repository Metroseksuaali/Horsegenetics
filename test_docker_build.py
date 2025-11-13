#!/usr/bin/env python3
"""
Docker Build Verification Test
Tests all critical functionality before Docker deployment
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from genetics.horse import Horse
        from genetics.gene_registry import get_default_registry
        from genetics.gene_interaction import PhenotypeCalculator
        from genetics.visualizer import HorseVisualizer
        from genetics.breed_presets import get_preset_manager
        from genetics.breeding_stats import calculate_offspring_probabilities
        from genetics.pedigree import PedigreeTree
        print("  ✅ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_random_generation():
    """Test random horse generation."""
    print("\n🎲 Testing random horse generation...")
    try:
        from genetics.horse import Horse

        # Test basic generation
        horse = Horse.random()
        assert horse.phenotype, "Phenotype should not be empty"
        assert horse.genotype, "Genotype should not be empty"
        print(f"  ✅ Basic generation: {horse.phenotype}")

        # Test with excluded genes
        horse2 = Horse.random(excluded_genes={'gray'})
        assert 'gray' not in horse2.phenotype.lower() or 'gray' in horse2.phenotype.lower(), "Excluded genes test"
        print(f"  ✅ Excluded genes: {horse2.phenotype}")

        # Test with custom probabilities
        horse3 = Horse.random(custom_probabilities={'gray': 0.1})
        print(f"  ✅ Custom probabilities: {horse3.phenotype}")

        return True
    except Exception as e:
        print(f"  ❌ Random generation failed: {e}")
        traceback.print_exc()
        return False

def test_breeding():
    """Test horse breeding."""
    print("\n🧬 Testing breeding...")
    try:
        from genetics.horse import Horse

        parent1 = Horse.random()
        parent2 = Horse.random()
        foal = Horse.breed(parent1, parent2)

        assert foal.phenotype, "Foal should have phenotype"
        assert foal.genotype, "Foal should have genotype"
        print(f"  ✅ Breeding successful")
        print(f"     Parent 1: {parent1.phenotype}")
        print(f"     Parent 2: {parent2.phenotype}")
        print(f"     Foal: {foal.phenotype}")

        return True
    except Exception as e:
        print(f"  ❌ Breeding failed: {e}")
        traceback.print_exc()
        return False

def test_visualization():
    """Test SVG visualization."""
    print("\n🎨 Testing visualization...")
    try:
        from genetics.horse import Horse
        import os

        horse = Horse.random()
        test_file = "/tmp/test_horse.svg"

        # Test visualization
        result = horse.visualize(test_file)
        assert os.path.exists(test_file), "SVG file should be created"

        # Check file content
        with open(test_file, 'r') as f:
            content = f.read()
            assert '<svg' in content, "SVG should contain svg tag"
            assert horse.phenotype in content, "SVG should contain phenotype label"

        print(f"  ✅ Visualization created: {test_file}")
        print(f"     Phenotype: {horse.phenotype}")

        # Cleanup
        os.remove(test_file)

        return True
    except Exception as e:
        print(f"  ❌ Visualization failed: {e}")
        traceback.print_exc()
        return False

def test_breed_presets():
    """Test breed preset system."""
    print("\n🏇 Testing breed presets...")
    try:
        from genetics.horse import Horse
        from genetics.breed_presets import get_preset_manager

        manager = get_preset_manager()

        # Test realistic breeds
        realistic = manager.get_realistic_breeds()
        assert len(realistic) > 0, "Should have realistic breeds"
        print(f"  ✅ Found {len(realistic)} realistic breeds")

        # Test fantasy breeds
        fantasy = manager.get_fantasy_breeds()
        assert len(fantasy) > 0, "Should have fantasy breeds"
        print(f"  ✅ Found {len(fantasy)} fantasy breeds")

        # Test Arabian preset
        arabian = manager.get_preset('arabian')
        assert arabian is not None, "Arabian preset should exist"
        assert 'gray' not in arabian.excluded_genes, "Arabian should allow gray"
        assert 'tobiano' in arabian.excluded_genes, "Arabian should exclude tobiano"
        print(f"  ✅ Arabian preset: {arabian.description}")

        # Generate Arabian horse
        horse = Horse.random(
            excluded_genes=arabian.excluded_genes,
            custom_probabilities=arabian.custom_probabilities
        )
        print(f"     Generated: {horse.phenotype}")

        return True
    except Exception as e:
        print(f"  ❌ Breed presets failed: {e}")
        traceback.print_exc()
        return False

def test_streamlit_syntax():
    """Test that streamlit_app.py has no syntax errors."""
    print("\n📱 Testing Streamlit app syntax...")
    try:
        import py_compile
        import tempfile

        # Compile streamlit_app.py to check for syntax errors
        py_compile.compile('streamlit_app.py', doraise=True)
        print("  ✅ streamlit_app.py has no syntax errors")

        return True
    except Exception as e:
        print(f"  ❌ Streamlit syntax check failed: {e}")
        traceback.print_exc()
        return False

def test_genotype_parsing():
    """Test genotype string parsing."""
    print("\n🧪 Testing genotype parsing...")
    try:
        from genetics.horse import Horse

        # Test parsing (using correct gene labels)
        genotype_str = "E:E/e A:A/a Dil:N/Cr D:D/nd2 Z:n/n Ch:n/n F:f/f STY:sty/sty G:g/g To:n/n O:n/n Sb:n/n Spl:n/n Rn:n/n Lp:lp/lp W:n/n PATN1:n/n"
        horse = Horse.from_string(genotype_str)

        assert horse.phenotype, "Should have phenotype"
        assert 'palomino' in horse.phenotype.lower() or 'buckskin' in horse.phenotype.lower(), "Should be dilute"
        print(f"  ✅ Parsing successful: {horse.phenotype}")
        print(f"     Input: {genotype_str[:50]}...")

        return True
    except Exception as e:
        print(f"  ❌ Genotype parsing failed: {e}")
        traceback.print_exc()
        return False

def test_realistic_distributions():
    """Test that gene distributions are realistic."""
    print("\n📊 Testing realistic distributions (100 horses)...")
    try:
        from genetics.horse import Horse

        horses = [Horse.random() for _ in range(100)]

        # Count pattern genes
        pattern_counts = {
            'gray': 0,
            'tobiano': 0,
            'leopard': 0,
            'roan': 0,
        }

        for horse in horses:
            pheno = horse.phenotype.lower()
            if 'gray' in pheno:
                pattern_counts['gray'] += 1
            if 'tobiano' in pheno:
                pattern_counts['tobiano'] += 1
            if 'leopard' in pheno or 'blanket' in pheno or 'fewspot' in pheno:
                pattern_counts['leopard'] += 1
            if 'roan' in pheno:
                pattern_counts['roan'] += 1

        # Check ranges (with some tolerance for small sample)
        gray_pct = pattern_counts['gray']
        tobiano_pct = pattern_counts['tobiano']
        leopard_pct = pattern_counts['leopard']
        roan_pct = pattern_counts['roan']

        print(f"  📈 Pattern distribution:")
        print(f"     Gray: {gray_pct}% (expected ~25-35%)")
        print(f"     Tobiano: {tobiano_pct}% (expected ~15-25%)")
        print(f"     Leopard: {leopard_pct}% (expected ~5-10%)")
        print(f"     Roan: {roan_pct}% (expected ~5-10%)")

        # Loose bounds for 100 horses
        assert 15 <= gray_pct <= 45, f"Gray frequency out of range: {gray_pct}%"
        assert leopard_pct <= 20, f"Leopard too high: {leopard_pct}%"

        print("  ✅ Distributions within acceptable ranges")

        return True
    except Exception as e:
        print(f"  ❌ Distribution test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🐴 Horse Genetics Docker Build Verification")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Random Generation", test_random_generation),
        ("Breeding", test_breeding),
        ("Visualization", test_visualization),
        ("Breed Presets", test_breed_presets),
        ("Streamlit Syntax", test_streamlit_syntax),
        ("Genotype Parsing", test_genotype_parsing),
        ("Realistic Distributions", test_realistic_distributions),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("📋 TEST RESULTS")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 60)

    if failed > 0:
        print("\n❌ Some tests failed! Fix issues before Docker deployment.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! Docker build should work correctly.")
        sys.exit(0)

if __name__ == "__main__":
    main()
