#!/usr/bin/env python3
"""
Performance Benchmarks for Horse Genetics Simulator

Measures performance of key operations to ensure the simulator
runs efficiently in game environments.

Run with:
    python3 test_performance.py

Or for specific benchmark:
    python3 test_performance.py TestPerformance.test_horse_generation_speed
"""

import unittest
import time
from genetics.horse import Horse
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator
from genetics.breeding_stats import calculate_offspring_probabilities


class TestPerformance(unittest.TestCase):
    """Performance benchmarks for horse genetics operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.registry = get_default_registry()
        cls.calculator = PhenotypeCalculator(cls.registry)

    def benchmark(self, operation_name: str, operation, iterations: int = 1000):
        """
        Run a benchmark and print results.

        Args:
            operation_name: Name of the operation being benchmarked
            operation: Callable to benchmark
            iterations: Number of iterations to run
        """
        start_time = time.time()

        for _ in range(iterations):
            operation()

        end_time = time.time()
        total_time = end_time - start_time
        ops_per_second = iterations / total_time
        time_per_op = total_time / iterations * 1000  # Convert to milliseconds

        print(f"\n{operation_name}:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Operations/second: {ops_per_second:.1f}")
        print(f"  Time per operation: {time_per_op:.3f}ms")

        return ops_per_second

    def test_horse_generation_speed(self):
        """
        Benchmark: Random horse generation speed.

        Target: >1000 horses/second
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Random Horse Generation")
        print("=" * 60)

        def generate():
            return Horse.random(self.registry, self.calculator)

        ops_per_second = self.benchmark("Random Horse Generation", generate, iterations=1000)

        # Assert performance target
        self.assertGreater(
            ops_per_second, 1000,
            f"Horse generation too slow: {ops_per_second:.1f} ops/sec (target: >1000)"
        )

    def test_breeding_speed(self):
        """
        Benchmark: Horse breeding speed.

        Target: >5000 breedings/second
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Horse Breeding")
        print("=" * 60)

        # Pre-generate parents
        parent1 = Horse.random(self.registry, self.calculator)
        parent2 = Horse.random(self.registry, self.calculator)

        def breed():
            return Horse.breed(parent1, parent2, self.registry, self.calculator)

        ops_per_second = self.benchmark("Horse Breeding", breed, iterations=5000)

        # Assert performance target
        self.assertGreater(
            ops_per_second, 5000,
            f"Breeding too slow: {ops_per_second:.1f} ops/sec (target: >5000)"
        )

    def test_phenotype_calculation_speed(self):
        """
        Benchmark: Phenotype calculation speed.

        Target: >10000 calculations/second
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Phenotype Calculation")
        print("=" * 60)

        # Pre-generate genotype
        genotype = self.registry.generate_random_genotype()

        def calculate():
            return self.calculator.determine_phenotype(genotype)

        ops_per_second = self.benchmark(
            "Phenotype Calculation",
            calculate,
            iterations=10000
        )

        # Assert performance target
        self.assertGreater(
            ops_per_second, 10000,
            f"Phenotype calculation too slow: {ops_per_second:.1f} ops/sec (target: >10000)"
        )

    def test_genotype_validation_speed(self):
        """
        Benchmark: Genotype string validation speed.

        Target: >1000 validations/second
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Genotype Validation")
        print("=" * 60)

        genotype_str = "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"

        def validate():
            return self.registry.parse_genotype_string(genotype_str)

        ops_per_second = self.benchmark("Genotype Validation", validate, iterations=1000)

        # Assert performance target
        self.assertGreater(
            ops_per_second, 1000,
            f"Validation too slow: {ops_per_second:.1f} ops/sec (target: >1000)"
        )

    def test_probability_calculation_speed(self):
        """
        Benchmark: Probability calculation speed (Monte Carlo).

        Target: Complete in <5 seconds for 1000 samples
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Probability Calculation (Monte Carlo)")
        print("=" * 60)

        parent1 = "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"
        parent2 = "E:e/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"

        start_time = time.time()
        probabilities = calculate_offspring_probabilities(
            parent1,
            parent2,
            sample_size=1000
        )
        end_time = time.time()

        total_time = end_time - start_time

        print(f"\nProbability Calculation (1000 samples):")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Samples/second: {1000/total_time:.1f}")

        # Assert performance target
        self.assertLess(
            total_time, 5.0,
            f"Probability calculation too slow: {total_time:.3f}s (target: <5s)"
        )

    def test_json_serialization_speed(self):
        """
        Benchmark: JSON serialization/deserialization speed.

        Target: >1000 operations/second
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: JSON Serialization")
        print("=" * 60)

        horse = Horse.random(self.registry, self.calculator)

        def to_dict():
            return horse.to_dict()

        ops_per_second = self.benchmark("JSON Serialization", to_dict, iterations=1000)

        # Assert performance target
        self.assertGreater(
            ops_per_second, 1000,
            f"JSON serialization too slow: {ops_per_second:.1f} ops/sec (target: >1000)"
        )

    def test_batch_generation_speed(self):
        """
        Benchmark: Batch generation of 1000 horses.

        Target: Complete in <5 seconds
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Batch Generation (1000 horses)")
        print("=" * 60)

        start_time = time.time()
        horses = [Horse.random(self.registry, self.calculator) for _ in range(1000)]
        end_time = time.time()

        total_time = end_time - start_time

        print(f"\nBatch Generation (1000 horses):")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Horses/second: {1000/total_time:.1f}")

        # Assert performance target
        self.assertLess(
            total_time, 5.0,
            f"Batch generation too slow: {total_time:.3f}s (target: <5s)"
        )

    def test_memory_efficiency(self):
        """
        Benchmark: Memory usage for large populations.

        Creates 10,000 horses and measures memory.
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Memory Efficiency (10,000 horses)")
        print("=" * 60)

        import sys

        # Generate horses
        horses = []
        for _ in range(10000):
            horses.append(Horse.random(self.registry, self.calculator))

        # Estimate memory usage
        total_size = sum(sys.getsizeof(h.to_dict()) for h in horses)
        avg_size = total_size / len(horses)

        print(f"\nMemory Usage:")
        print(f"  Total: {total_size / 1024 / 1024:.2f} MB")
        print(f"  Per horse: {avg_size:.1f} bytes")
        print(f"  Horses per MB: {1024 * 1024 / avg_size:.0f}")

        # Assert reasonable memory usage (< 500 bytes per horse)
        self.assertLess(
            avg_size, 500,
            f"Memory usage too high: {avg_size:.1f} bytes/horse (target: <500)"
        )


class TestScalability(unittest.TestCase):
    """Test scalability with increasing loads."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.registry = get_default_registry()
        cls.calculator = PhenotypeCalculator(cls.registry)

    def test_breeding_chain_performance(self):
        """
        Benchmark: Multi-generation breeding chain.

        Simulates 10 generations of breeding.
        """
        print("\n" + "=" * 60)
        print("BENCHMARK: Multi-Generation Breeding Chain")
        print("=" * 60)

        start_time = time.time()

        # Start with foundation horses
        current_gen = [
            Horse.random(self.registry, self.calculator) for _ in range(10)
        ]

        # Breed 10 generations
        for gen in range(10):
            next_gen = []

            for i in range(0, len(current_gen) - 1, 2):
                parent1 = current_gen[i]
                parent2 = current_gen[i + 1]
                offspring = Horse.breed(parent1, parent2, self.registry, self.calculator)
                next_gen.append(offspring)

            current_gen = next_gen

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n10-Generation Breeding Chain:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Final generation size: {len(current_gen)}")

        # Assert reasonable performance
        self.assertLess(
            total_time, 10.0,
            f"Breeding chain too slow: {total_time:.3f}s (target: <10s)"
        )


def run_all_benchmarks():
    """Run all benchmarks and print summary."""
    print("\n" + "=" * 60)
    print("HORSE GENETICS SIMULATOR - PERFORMANCE BENCHMARKS")
    print("=" * 60)

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestScalability))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ All performance targets met!")
    else:
        print("\n✗ Some performance targets not met")

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_all_benchmarks())
