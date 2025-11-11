# Horse Coat Color Genetics Simulator

Hevosen värigenetiikka simulaattori, joka generoi satunnaisia hevosia ja mahdollistaa kahden hevosen jalostamisen. Ohjelma toimii sekä terminaalissa että graafisella käyttöliittymällä.

## Ominaisuudet

### Genetiikka (8 geeniä)
1. **Extension (E/e)** - Määrittää onko pigmentti mustaa vai punaista
2. **Agouti (A/a)** - Määrittää mustan jakautumisen (bay vs black)
3. **Dilution (N/Cr/Prl)** - Laimennusgeeni kolmella alleelilla (Cream ja Pearl SAMASSA geenissä!)
4. **Dun (D/nd1/nd2)** - Dun-laimennus primitiivisillä merkeillä
5. **Silver (Z/n)** - Vaalentaa mustaa pigmenttiä (erityisesti harja ja häntä)
6. **Champagne (Ch/n)** - Vaalentaa SEKÄ punaista ETTÄ mustaa pigmenttiä (SLC36A1)
7. **Flaxen (F/f)** - Vaalentaa harjaa/häntää VAIN ruunikoilla (resessiivinen)
8. **Sooty (STY/sty)** - Lisää tummempia karvoja

### Tärkeä biologinen korjaus
**Cream ja Pearl ovat samassa geenissä (SLC45A2), eivät erillisiä geenejä!**

Mahdolliset genotyypit: N/N, N/Cr, Cr/Cr, N/Prl, Prl/Prl, Cr/Prl

Cr/Prl-yhdistelmä tuottaa "pseudo-double dilute" -efektin!

## Käyttö

### GUI-versio (Suositeltu)

```bash
python3 horse_genetics_gui.py
```

**Vaatimukset:**
- Python 3 (tkinter tulee mukana)
- Toimii Windowsissa, macOS:ssä ja Linux-työpöytäympäristöissä
- EI toimi WSL:ssä ilman X-serveriä (normaalia)

**Kolme välilehteä:**
1. **Random Generator** - Generoi satunnainen hevonen yhdellä klikkauksella
2. **Breeding Simulator** - Jalosta kaksi hevosta pudotusvalikoiden avulla
3. **Help** - Kattava genetiikka-opas

### Terminaaliversio

```bash
python3 horse_genetics.py
```

Interaktiivinen tekstipohjainen käyttöliittymä:
1. Generoi satunnainen hevonen
2. Jalosta kaksi hevosta (syötä genotyypit manuaalisesti)

## Genotyypin syöttöformaatti

```
E:E/e A:A/a Dil:N/Cr D:D/nd1 Z:n/n Ch:n/n F:F/f STY:STY/sty
```

**Alleelien vaihtoehdot:**
- E: E, e
- A: A, a
- Dil: N, Cr, Prl (kolme vaihtoehtoa!)
- D: D, nd1, nd2
- Z: Z, n
- Ch: Ch, n
- F: F, f
- STY: STY, sty

## Esimerkkejä fenotyypeistä

### Perusvärit
- **Chestnut** - e/e (punainen)
- **Bay** - E/- A/- (ruskea, musta vain pistoissa)
- **Black** - E/- a/a (musta)

### Cream-laimennukset
- **Palomino** - e/e N/Cr (kullanvärinen ruunikko)
- **Buckskin** - E/- A/- N/Cr (vaalean ruskea)
- **Cremello** - e/e Cr/Cr (hyvin vaalea, melkein valkoinen)

### Pearl ja yhdistelmät
- **Pseudo-Cremello** - e/e Cr/Prl (Cream + Pearl yhdistelmä!)
- **Apricot** - e/e Prl/Prl (aprikoosi väri)

### Champagne-värit
- **Gold Champagne** - e/e Ch/- (kultainen, champagne-silmät)
- **Amber Champagne** - E/- A/- Ch/- (meripihkan värinen)
- **Classic Champagne** - E/- a/a Ch/- (tummempi champagne)
- **Gold Cream Champagne** - e/e N/Cr Ch/- (Palomino + Champagne)

### Flaxen ja muut modifioijat
- **Flaxen Chestnut** - e/e f/f (ruunikko vaalean harjan/hännän kanssa)
- **Flaxen Palomino** - e/e N/Cr f/f (hyvin vaalea harja/häntä)
- **Silver Bay** - E/- A/- Z/- (hopeanvärinen harja ja häntä)
- **Sooty Dun** - STY/- D/- (tumma dunväri primitiivisillä merkeillä)
- **Gold Champagne with Flaxen Dun** - e/e Ch/- f/f D/- (monimutkainen yhdistelmä!)

## Tekninen toteutus

- **Kieli:** Python 3
- **GUI:** tkinter (sisäänrakennettu, cross-platform)
- **Genetiikka:** Biologisesti tarkka Mendelin periytyminen
- **Epistasia:** Extension epistaattinen Agoutille
- **Compound heterozygote:** Cr/Prl yhdistelmä toimii oikein

## Tiedostot

- `horse_genetics.py` - Genetiikka-moottori ja terminaaliversio
- `horse_genetics_gui.py` - Graafinen käyttöliittymä
- `CLAUDE.md` - Tekninen dokumentaatio kehittäjille
- `README.md` - Tämä tiedosto

## Testaus

```bash
# Testaa satunnainen generointi
python3 -c "from horse_genetics import HorseGeneticGenerator; g = HorseGeneticGenerator(); print(g.generate_horse())"

# Testaa jalostus
python3 -c "from horse_genetics import HorseGeneticGenerator; g = HorseGeneticGenerator(); p1 = g.parse_genotype_input('E:E/E A:A/A Dil:Cr/Cr D:D/D Z:n/n STY:sty/sty'); p2 = g.parse_genotype_input('E:e/e A:a/a Dil:Prl/Prl D:nd2/nd2 Z:Z/Z STY:STY/STY'); offspring = g.breed_horses(p1, p2); print(f'Offspring: {g.determine_phenotype(offspring)}')"
```

## Lisenssi ja käyttö

Ohjelma on luotu opetus- ja harrastustarkoituksiin. Genetiikka perustuu tieteelliseen tutkimukseen.

## Huomioita

- **Sooty-geeni on yksinkertaistettu** - Todellisuudessa se on polygeeninen (useita geenejä)
- **GUI vaatii näyttöpalvelimen** - Ei toimi WSL:ssä ilman X-serveriä
- **Biologisesti tarkka** - Cream ja Pearl on korjattu samaan geeniin kuten oikeassa genetiikassa

## Lähteet

Genetiikka perustuu tutkimukseen hevosen värigeeneistä, erityisesti:
- SLC45A2 (Cream/Pearl -geeni)
- MC1R (Extension)
- ASIP (Agouti)
- TBX3 (Dun)
- PMEL17 (Silver)

---

**Nauti hevosgenetiikan tutkimisesta!** 🐴
