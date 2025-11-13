# Horse Coat Color Genetics Simulator

A scientifically accurate horse color genetics simulator that generates random horses and enables breeding between two horses. The program works both in terminal and with a graphical user interface.

**Version 2.0** - Refactored with modular architecture for scalability to thousands of genetic traits.

## Features

### 9 Genetic Traits
1. **Extension (E/e)** - Black or red pigment
2. **Agouti (A/a)** - Bay or black distribution
3. **Dilution (N/Cr/Prl)** - Cream and Pearl dilutions
4. **Dun (D/nd1/nd2)** - Dun dilution with primitive markings
5. **Silver (Z/n)** - Lightens black pigment (mane and tail)
6. **Champagne (Ch/n)** - Lightens both red and black pigment
7. **Flaxen (F/f)** - Lightens mane/tail on chestnuts only
8. **Sooty (STY/sty)** - Adds darker hairs
9. **Gray (G/g)** - Progressive graying with age (dominant)

## How to Use

### GUI Version (Recommended)

```bash
python3 horse_genetics_gui.py
```

**Requirements:**
- Python 3 with tkinter
- Works on Windows, macOS, and Linux

**Features:**
- **Random Generator** - Generate random horses with one click
- **Breeding Simulator** - Breed two horses using dropdown menus
- **Help** - Built-in genetics guide

### Terminal Version

```bash
python3 horse_genetics.py
```

Interactive menu:
1. Generate a random horse
2. Breed two horses (manual input required)

## Color Examples

### Base Colors
- **Chestnut** - Red coat
- **Bay** - Brown coat with black mane, tail, and legs
- **Black** - Black coat

### Dilutions
- **Palomino** - Golden chestnut
- **Buckskin** - Light brown with black points
- **Cremello** - Very light, almost white

### Champagne Colors
- **Gold Champagne** - Golden with amber eyes
- **Amber Champagne** - Amber colored
- **Classic Champagne** - Dark champagne

### Special Combinations
- **Flaxen Chestnut** - Chestnut with light mane/tail
- **Silver Bay** - Bay with silver mane and tail
- **Sooty Dun** - Dark dun with primitive markings

## Project Structure

```
genetics/
├── __init__.py              # Module initialization
├── gene_definitions.py      # Centralized gene data (NEW)
├── gene_registry.py         # Registry pattern for gene management (NEW)
├── gene_interaction.py      # Modular phenotype system (NEW)
├── horse.py                 # Fluent API for easy integration (NEW)
├── core.py                  # Legacy gene pools (maintained for compatibility)
├── phenotype.py             # Legacy phenotype calculator (maintained for compatibility)
└── breeding.py              # Legacy breeding simulator (maintained for compatibility)

horse_genetics.py            # Command-line interface
horse_genetics_gui.py        # Graphical user interface
test_genetics.py             # Comprehensive unit tests (55 tests)
```

**Why Modular?** The new structure separates genetics logic from UI, making it easier to:
- Add new genes and traits
- Fix genetic inaccuracies
- Scale to thousands of genetic combinations
- Test individual components
- **Integrate into game projects and other applications**

## API for Game Projects

**Version 2.0** includes a clean, fluent API perfect for game integration:

### Quick Start

```python
from genetics.horse import Horse

# Generate a random horse
horse = Horse.random()
print(horse.phenotype)        # "Silver Bay Dun"
print(horse.genotype_string)  # "E: E/e  A: A/A  Dil: N/N..."

# Breed two horses
mare = Horse.random()
stallion = Horse.random()
foal = Horse.breed(mare, stallion)
print(f"Foal: {foal.phenotype}")

# Check specific genes
if horse.has_allele('gray', 'G'):
    print("This horse will gray with age!")

# Create from genotype string
custom_horse = Horse.from_string(
    "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"
)
```

### Game Integration Example

```python
# In your game's horse generator
class GameHorse:
    def __init__(self):
        self.genetics = Horse.random()
        self.name = generate_name()
        self.color = self.genetics.phenotype

    def breed_with(self, other_horse):
        foal_genetics = Horse.breed(self.genetics, other_horse.genetics)
        return GameHorse.from_genetics(foal_genetics)
```

### Registry Pattern (Advanced)

For games that want to add custom genes or modifiers:

```python
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator

# Get registry
registry = get_default_registry()

# Add custom modifier to phenotype pipeline
def apply_custom_gene(ctx):
    if ctx.has_allele('custom_gene', 'X'):
        ctx.phenotype = f"Mystical {ctx.phenotype}"

calculator = PhenotypeCalculator(registry)
calculator.add_modifier(apply_custom_gene)
```

## About

This program simulates realistic horse coat color genetics using Mendelian inheritance patterns. All color combinations are based on real equine genetics research.

**Version 2.0 Improvements:**
- ✓ Fixed Sooty gene visibility (no longer appears on fully black horses)
- ✓ Corrected double Pearl on black: "Smoky Pearl" (not "Pearl Black")
- ✓ Fixed Champagne naming on double dilutes (e.g., "Perlino Champagne")
- ✓ Silver correctly shows on double cream dilutes (Perlino, Smoky Cream)
- ✓ Added Gray gene (STX17) - progressive graying with age
- ✓ Modular architecture with Registry pattern and fluent API
- ✓ Clean API for game integration and external applications
- ✓ 55 comprehensive unit tests ensuring genetic accuracy

**Note:** The Sooty and Flaxen genes are simplified in this simulator. In real horses, these traits are controlled by multiple genes.

---

**Enjoy exploring horse genetics!** 🐴
