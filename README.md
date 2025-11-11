# Horse Coat Color Genetics Simulator

A horse color genetics simulator that generates random horses and enables breeding between two horses. The program works both in terminal and with a graphical user interface.

## Features

### Genetics (8 genes)
1. **Extension (E/e)** - Determines whether pigment is black or red
2. **Agouti (A/a)** - Controls black pigment distribution (bay vs black)
3. **Dilution (N/Cr/Prl)** - Dilution gene with three alleles (Cream and Pearl in the SAME gene!)
4. **Dun (D/nd1/nd2)** - Dun dilution with primitive markings
5. **Silver (Z/n)** - Lightens black pigment (especially mane and tail)
6. **Champagne (Ch/n)** - Lightens BOTH red AND black pigment (SLC36A1)
7. **Flaxen (F/f)** - Lightens mane/tail ONLY on chestnuts (recessive)
8. **Sooty (STY/sty)** - Adds darker hairs

### Important Biological Correction
**Cream and Pearl are in the same gene (SLC45A2), not separate genes!**

Possible genotypes: N/N, N/Cr, Cr/Cr, N/Prl, Prl/Prl, Cr/Prl

Cr/Prl combination produces a "pseudo-double dilute" effect!

## Usage

### GUI Version (Recommended)

```bash
python3 horse_genetics_gui.py
```

**Requirements:**
- Python 3 (tkinter comes built-in)
- Works on Windows, macOS, and Linux desktop environments
- Does NOT work in WSL without X server (this is normal)

**Three tabs:**
1. **Random Generator** - Generate a random horse with one click
2. **Breeding Simulator** - Breed two horses using dropdown menus
3. **Help** - Comprehensive genetics guide

### Terminal Version

```bash
python3 horse_genetics.py
```

Interactive text-based interface:
1. Generate a random horse
2. Breed two horses (manually input genotypes)

## Genotype Input Format

```
E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty
```

**Allele options:**
- E: E, e
- A: A, a
- Dil: N, Cr, Prl (three options!)
- D: D, nd1, nd2
- Z: Z, n
- Ch: Ch, n
- F: F, f
- STY: STY, sty

## Phenotype Examples

### Base Colors
- **Chestnut** - e/e (red)
- **Bay** - E/- A/- (brown, black only on points)
- **Black** - E/- a/a (black)

### Cream Dilutions
- **Palomino** - e/e N/Cr (golden chestnut)
- **Buckskin** - E/- A/- N/Cr (light brown)
- **Cremello** - e/e Cr/Cr (very light, almost white)

### Pearl and Combinations
- **Pseudo-Cremello** - e/e Cr/Prl (Cream + Pearl combination!)
- **Apricot** - e/e Prl/Prl (apricot color)

### Champagne Colors
- **Gold Champagne** - e/e Ch/- (golden with champagne eyes)
- **Amber Champagne** - E/- A/- Ch/- (amber colored)
- **Classic Champagne** - E/- a/a Ch/- (darker champagne)
- **Gold Cream Champagne** - e/e N/Cr Ch/- (Palomino + Champagne)

### Flaxen and Other Modifiers
- **Flaxen Chestnut** - e/e f/f (chestnut with light mane/tail)
- **Flaxen Palomino** - e/e N/Cr f/f (very light mane/tail)
- **Silver Bay** - E/- A/- Z/- (silver mane and tail)
- **Sooty Dun** - STY/- D/- (dark dun with primitive markings)
- **Gold Champagne with Flaxen Dun** - e/e Ch/- f/f D/- (complex combination!)

## Technical Implementation

- **Language:** Python 3
- **GUI:** tkinter (built-in, cross-platform)
- **Genetics:** Biologically accurate Mendelian inheritance
- **Epistasis:** Extension is epistatic to Agouti
- **Compound heterozygote:** Cr/Prl combination works correctly

## Files

- `horse_genetics.py` - Genetics engine and terminal version
- `horse_genetics_gui.py` - Graphical user interface
- `README.md` - This file

## Testing

```bash
# Test random generation
python3 -c "from horse_genetics import HorseGeneticGenerator; g = HorseGeneticGenerator(); print(g.generate_horse())"

# Test breeding
python3 -c "from horse_genetics import HorseGeneticGenerator; g = HorseGeneticGenerator(); p1 = g.parse_genotype_input('E:E/E A:A/A Dil:Cr/Cr D:D/D Z:n/n Ch:n/n F:F/F STY:sty/sty'); p2 = g.parse_genotype_input('E:e/e A:a/a Dil:Prl/Prl D:nd2/nd2 Z:Z/Z Ch:Ch/Ch F:f/f STY:STY/STY'); offspring = g.breed_horses(p1, p2); print(f'Offspring: {g.determine_phenotype(offspring)}')"
```

## License and Usage

This program is created for educational and hobby purposes. Genetics are based on scientific research.

## Notes

- **Sooty gene is simplified** - In reality it is polygenic (multiple genes)
- **GUI requires display server** - Does not work in WSL without X server
- **Biologically accurate** - Cream and Pearl have been corrected to the same gene as in real genetics

## Sources

Genetics are based on research into equine color genes, especially:
- SLC45A2 (Cream/Pearl gene)
- MC1R (Extension)
- ASIP (Agouti)
- TBX3 (Dun)
- PMEL17 (Silver)
- SLC36A1 (Champagne)

---

**Enjoy exploring horse genetics!** 🐴
