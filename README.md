# 🐴 Horse Coat Color Genetics Simulator

A scientifically accurate horse color genetics simulator that generates random horses and enables breeding between two horses. The program works both in terminal and with a graphical user interface.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Custom](https://img.shields.io/badge/License-Horse%20Genetics%201.0-green.svg)](LICENSE)


## ✨ Features

### Core Genetics
- **17 Genetic Traits**: Extension, Agouti, Dilution (Cream/Pearl), Dun, Silver, Champagne, Flaxen, Sooty, Gray, Roan, Tobiano, Frame Overo, Sabino, Dominant White, Splash White, Leopard Complex, PATN1
- **100+ Phenotypes**: Including rare colors like Smoky Cream, Pearl Bay, Silver Dapple, Tovero, and Leopard Appaloosa
- **Scientifically Accurate**: Based on peer-reviewed equine genetics research
- **Mendelian Inheritance**: Realistic breeding simulation with lethal combinations (Frame Overo LWOS)

### Advanced Features (NEW in v2.1!)
- **📊 Probability Calculator**: See breeding outcome chances before breeding
- **📈 Statistics Simulator**: Run thousands of simulations for analysis
- **🔍 Genotype Finder**: Find all ways to produce a specific phenotype
- **🌳 Pedigree Tracking**: Build and visualize family trees
- **🌐 REST API**: HTTP endpoints for web/mobile game integration
- **⚡ Performance Optimized**: >50,000 horses/second generation speed
- **💾 JSON/CSV I/O**: Game save/load functionality
- **✅ Input Validation**: Helpful error messages with suggestions

### Developer Tools
- **Fluent API**: `Horse.random()`, `Horse.breed(parent1, parent2)`
- **Type Hints**: Full typing support for IDE autocomplete
- **CLI Arguments**: Batch mode, probability calculation, simulation
- **Performance Benchmarks**: Ensure fast performance for games

## 🚀 Quick Start

### 🐳 Docker (Easiest - Recommended!)

**Before building, test that everything works:**
```bash
python3 test_docker_build.py
```

**Then start the application:**
```bash
# Start web interface
docker-compose up web

# Open browser to http://localhost:8501
```

**Or build and run manually:**
```bash
docker build -t horse-genetics .
docker run -p 8501:8501 horse-genetics
```

### 🌐 Web Interface (Streamlit)

**Install and run:**
```bash
pip install streamlit
streamlit run streamlit_app.py
```

**Features:**
- 🎲 Random horse generator
- 🧬 Interactive breeding simulator
- 📊 Probability calculator with charts
- 📚 My Stable - save/load your horses
- 💾 Export to JSON
- 🎨 Modern, responsive UI
- 📱 Works on mobile!

### Terminal Version

```bash
# Interactive mode
python3 horse_genetics.py

# Generate 10 random horses
python3 horse_genetics.py --batch 10

# Show phenotype for genotype
python3 horse_genetics.py --genotype "E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g"

# Calculate breeding probabilities
python3 horse_genetics.py --probabilities "E:E/e A:A/a ..." "E:e/e A:A/a ..."

# Simulate 1000 breedings
python3 horse_genetics.py --simulate 1000 "E:E/e A:A/a ..." "E:e/e A:A/a ..."

# Find genotypes producing Buckskin
python3 horse_genetics.py --find-genotypes "Buckskin"

# Show help
python3 horse_genetics.py --help
```

### REST API Server

```bash
# Install dependencies
pip install fastapi uvicorn

# Start API server
python3 api/main.py

# API documentation at http://localhost:8000/docs
```

**API Endpoints**:
- `POST /api/random` - Generate random horse
- `POST /api/breed` - Breed two horses
- `POST /api/probabilities` - Calculate breeding probabilities
- `POST /api/batch` - Generate multiple horses
- `GET /api/genes` - List all genes

## Color Examples

### Base Colors
- **Chestnut** - Red coat
- **Bay** - Brown coat with black mane, tail, and legs
- **Black** - Black coat

### Dilutions
- **Palomino** - Golden chestnut (single cream on chestnut)
- **Buckskin** - Light brown with black points (single cream on bay)
- **Cremello** - Very light, almost white (double cream on chestnut)
- **Perlino** - Cream with darker points (double cream on bay)

### Dun Colors (Industry Names)
- **Grullo (Black Dun)** - Mouse gray with primitive markings
- **Red Dun (Chestnut Dun)** - Red/tan with primitive markings
- **Dunalino (Palomino Dun)** - Gold dun with primitive markings
- **Dunskin (Buckskin Dun)** - Buckskin with primitive markings
- **Bay Dun** - Bay with primitive markings

### Champagne Colors
- **Gold Champagne** - Golden with amber eyes (chestnut + champagne)
- **Amber Champagne** - Amber colored (bay + champagne)
- **Classic Champagne** - Dark champagne (black + champagne)

### Special Combinations
- **Chestnut with Flaxen** - Chestnut with light mane/tail
- **Silver Bay** - Bay with silver mane and tail
- **Silver Grullo (Silver Black Dun)** - Gray with silver and dun
- **Sooty Red Dun (Sooty Chestnut Dun)** - Dark red dun

### Roan Patterns
- **Bay Roan (Red Roan)** - Bay with intermingled white hairs
- **Chestnut Roan** - Chestnut with white hairs (also called Red Roan or Strawberry Roan)
- **Black Roan (Blue Roan)** - Black with white hairs, appears blue-gray

### White Spotting Patterns
- **Tobiano** - Large white patches with rounded edges, white crosses back
- **Frame Overo** - White usually horizontal, rarely crosses back (LETHAL when homozygous - LWOS)
- **Sabino 1** - Irregular white edges, high white on legs, white face
- **Maximum Sabino** - Homozygous Sabino 1, often mostly white
- **Dominant White (W)** - White or mostly white coat. Multiple alleles (W1, W5, W10, W13, W20, W22). Most LETHAL when homozygous except W20.
- **Splash White** - White from bottom up (legs, belly), often blue eyes
- **Tovero** - Combination of Tobiano + any Overo pattern (Frame, Sabino, or Splash)

### Appaloosa (Leopard Complex)
- **Leopard** - White coat with colored spots all over (Lp + PATN1)
- **Fewspot** - Mostly white with minimal spots (Lp/Lp without PATN1)
- **Blanket** - White blanket over hip with base color spots (Lp/lp without PATN1)

## 📁 Project Structure

```
Horsegenetics/
├── genetics/
│   ├── __init__.py              # Module initialization
│   ├── gene_definitions.py      # Centralized gene data
│   ├── gene_registry.py         # Registry pattern for gene management
│   ├── gene_interaction.py      # Modular phenotype system
│   ├── horse.py                 # Fluent API for easy integration
│   ├── breeding_stats.py        # Probability calculator (NEW v2.1)
│   ├── pedigree.py              # Pedigree tracking (NEW v2.1)
│   ├── validation.py            # Input validation (NEW v2.1)
│   ├── io.py                    # JSON/CSV I/O (NEW v2.1)
│   ├── core.py                  # Legacy gene pools (backwards compatibility)
│   ├── phenotype.py             # Legacy phenotype calculator
│   └── breeding.py              # Legacy breeding simulator
├── api/
│   ├── __init__.py
│   └── main.py                  # FastAPI REST API (NEW v2.1)
├── streamlit_app.py             # Web UI (Streamlit) (NEW v2.1)
├── horse_genetics.py            # CLI with advanced features
├── test_genetics.py             # Unit tests
├── test_performance.py          # Performance benchmarks (NEW v2.1)
├── Dockerfile                   # Docker container (NEW v2.1)
├── docker-compose.yml           # Docker Compose (NEW v2.1)
├── requirements.txt             # Python dependencies (NEW v2.1)
├── pyproject.toml               # Package metadata (NEW v2.1)
├── LICENSE                      # MIT License
└── README.md                    # This file
```

**Why Modular?** The architecture separates genetics logic from UI:
- ✅ Add new genes and traits easily
- ✅ Fix genetic inaccuracies without breaking UI
- ✅ Scale to thousands of genetic combinations
- ✅ Test individual components independently
- ✅ **Perfect for game integration and external applications**

## 🎮 Game & Bot Integration

**Want to integrate horse genetics into your game, Discord bot, or application?**

👉 **[See the complete GAME INTEGRATION GUIDE](GAME_INTEGRATION.md)** 👈

The core genetics engine requires **ZERO dependencies** (only Python standard library) and is completely standalone!

### Quick Example

```python
from genetics.horse import Horse

# Generate random horses
horse = Horse.random()
print(horse.phenotype)  # "Buckskin"

# Breed horses
foal = Horse.breed(parent1, parent2)
print(f"Foal: {foal.phenotype}")
```

### What You Get

The [GAME_INTEGRATION.md](GAME_INTEGRATION.md) guide includes:
- ✅ What files you need (just `genetics/` folder!)
- ✅ Complete Discord bot example with commands
- ✅ Simple breeding game example
- ✅ REST API integration example
- ✅ Save/load system examples
- ✅ Full API reference

**Perfect for:**
- 🎮 Horse breeding games
- 🤖 Discord/Telegram bots
- 🌐 Web applications
- 📱 Mobile games
- 🎓 Educational tools

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

**For more examples, see [GAME_INTEGRATION.md](GAME_INTEGRATION.md)**

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

## 📊 Performance Benchmarks

Tested performance on standard hardware:

| Operation | Speed |
|-----------|-------|
| Horse generation | >50,000 ops/sec |
| Breeding | >40,000 ops/sec |
| Phenotype calculation | >150,000 ops/sec |
| JSON serialization | >500,000 ops/sec |
| Memory usage | ~184 bytes/horse |

**Perfect for games!** Can handle thousands of horses without performance issues.

Run benchmarks yourself:
```bash
python3 test_performance.py
```

## 🧪 Testing

```bash
# Run all unit tests (65 tests)
python3 test_genetics.py

# Run performance benchmarks
python3 test_performance.py

# Run verbose
python3 test_genetics.py -v
```

All tests pass with 100% accuracy! ✅

## 📦 Installation

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/Metroseksuaali/Horsegenetics.git
cd Horsegenetics

# Start web UI
docker-compose up web

# Or start REST API
docker-compose up api

# Or build manually
docker build -t horse-genetics .
docker run -p 8501:8501 horse-genetics
```

### Option 2: Python (Local Installation)

```bash
# Clone repository
git clone https://github.com/Metroseksuaali/Horsegenetics.git
cd Horsegenetics

# Install core package
pip install -e .

# Install optional dependencies
pip install -r requirements.txt  # All features
# OR selectively:
pip install streamlit            # Web UI
pip install fastapi uvicorn      # REST API
pip install matplotlib           # Pedigree graphs
```

### Option 3: PyPI (when published)

```bash
pip install horse-genetics
pip install streamlit  # For web UI
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional genes (e.g., additional Appaloosa pattern genes)
- More phenotype variations and combinations
- Performance optimizations
- Additional language translations
- GUI improvements
- Enhanced pedigree visualization

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Metroseksuaali/Horsegenetics/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Metroseksuaali/Horsegenetics/discussions)

## 🎓 About

This program simulates realistic horse coat color genetics using Mendelian inheritance patterns. All color combinations are based on real equine genetics research.

**Color Naming:** The simulator uses industry-standard equestrian names (like "Grullo", "Red Dun", "Dunalino") alongside genetic descriptions in parentheses. This makes it familiar for horse enthusiasts while remaining scientifically accurate. For example, a black horse with dun dilution displays as "Grullo (Black Dun)" - the industry name with genetic explanation.

**Version History:**

**v2.2** (Latest) - White Patterns & Appaloosa Update:
- ✅ **17 genes total** - Added Roan, Tobiano, Frame Overo, Sabino, Dominant White (W1-W39), Splash White, Leopard Complex, PATN1
- ✅ **Dominant White alleles** - W1, W5, W10, W13, W20, W22 with lethality checks (W20 viable)
- ✅ **Tovero pattern** - Automatic detection of Tobiano + Overo combinations
- ✅ **Appaloosa patterns** - Leopard, Fewspot, and Blanket patterns
- ✅ **Lethal gene warnings** - Frame Overo LWOS and Dominant White homozygous detection
- ✅ **Industry-standard names** - Blue Roan, Red Roan, Tovero, etc.
- ✅ **118 comprehensive tests** - All pattern combinations tested including Dominant White
- ✅ **Roan viability** - Based on 2020 research showing Rn/Rn is viable

**v2.1** - Production-Ready Release:
- ✅ **Streamlit web UI** - Modern browser-based interface
- ✅ **Docker support** - One-command deployment
- ✅ **Industry-standard color names** - Grullo, Red Dun, Dunalino, etc. with genetic descriptions
- ✅ Breeding probability calculator
- ✅ REST API for game integration
- ✅ Statistics simulation tools
- ✅ Genotype finder
- ✅ Pedigree tracking and visualization
- ✅ Performance benchmarks (>50k ops/sec)
- ✅ JSON/CSV I/O for game saves
- ✅ Input validation with helpful errors

**v2.0** - Modular Architecture:
- ✅ Fixed Sooty gene visibility
- ✅ Corrected Pearl and Champagne interactions
- ✅ Added Gray gene (STX17)
- ✅ Registry pattern for extensibility
- ✅ Fluent API for game integration
- ✅ 65 unit tests ensuring accuracy

**Note:** The Sooty and Flaxen genes are simplified in this simulator. In real horses, these traits are controlled by multiple genes.

---

**Tehty ❤️:llä hevosharrastajille ja pelinkehittäjille**

---

## 📋 License

This project uses the **Horse Genetics License 1.0** — free to use, modify, and distribute.

**If you use this in a published project** (game, app, website, etc.), please include a visible credit:

> Horse genetics powered by [Horse Genetics](https://github.com/Metroseksuaali/Horsegenetics) by Metroseksuaali

See [LICENSE](LICENSE) for the full terms.

## 🏆 Using Horse Genetics in your project?

If you've built something with this library, please
[open a Show and Tell issue](https://github.com/Metroseksuaali/Horsegenetics/issues/new?template=using-this-project.md)!
It helps the author track usage and showcase what people have built.

See [USERS.md](USERS.md) for the list of known projects.

