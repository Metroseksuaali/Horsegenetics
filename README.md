# Horse Coat Color Genetics Simulator

A scientifically accurate horse color genetics simulator that generates random horses and enables breeding between two horses. The program works both in terminal and with a graphical user interface.

**Version 2.0** - Refactored with modular architecture for scalability to thousands of genetic traits.

## Features

### 8 Genetic Traits
1. **Extension (E/e)** - Black or red pigment
2. **Agouti (A/a)** - Bay or black distribution
3. **Dilution (N/Cr/Prl)** - Cream and Pearl dilutions
4. **Dun (D/nd1/nd2)** - Dun dilution with primitive markings
5. **Silver (Z/n)** - Lightens black pigment (mane and tail)
6. **Champagne (Ch/n)** - Lightens both red and black pigment
7. **Flaxen (F/f)** - Lightens mane/tail on chestnuts only
8. **Sooty (STY/sty)** - Adds darker hairs

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
├── __init__.py          # Module initialization
├── core.py              # Gene pools and allele definitions
├── phenotype.py         # Phenotype calculation and color nomenclature
└── breeding.py          # Breeding simulation (Mendelian inheritance)

horse_genetics.py        # Command-line interface
horse_genetics_gui.py    # Graphical user interface
```

**Why Modular?** The new structure separates genetics logic from UI, making it easier to:
- Add new genes and traits
- Fix genetic inaccuracies
- Scale to thousands of genetic combinations
- Test individual components

## About

This program simulates realistic horse coat color genetics using Mendelian inheritance patterns. All color combinations are based on real equine genetics research.

**Version 2.0 Improvements:**
- ✓ Fixed Sooty gene visibility (no longer appears on fully black horses)
- ✓ Corrected double Pearl on black: "Smoky Pearl" (not "Pearl Black")
- ✓ Fixed Champagne naming on double dilutes (e.g., "Perlino Champagne")
- ✓ Silver no longer shows on double cream dilutes (minimal visible effect)
- ✓ Modular architecture for future expansion

**Note:** The Sooty and Flaxen genes are simplified in this simulator. In real horses, these traits are controlled by multiple genes.

---

**Enjoy exploring horse genetics!** 🐴
