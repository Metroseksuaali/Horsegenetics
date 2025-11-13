# Game Integration Guide

**How to integrate the Horse Genetics Engine into your game, Discord bot, or application**

This guide shows you how to use **only the core genetics engine** without any of the web UI, visualization, or other optional dependencies. The genetics engine is completely standalone and requires only Python's standard library.

---

## 🎮 What You Need

You only need the **`genetics/` folder** - nothing else!

```
your_project/
├── genetics/           # Copy this entire folder
│   ├── __init__.py
│   ├── horse.py       # Main Horse class
│   ├── gene.py        # Gene definitions
│   ├── gene_registry.py
│   ├── gene_interaction.py
│   ├── breeding_stats.py
│   ├── pedigree.py    # Optional: for tracking lineage
│   └── io.py          # Optional: for save/load
└── your_game.py       # Your game code
```

**What you DON'T need:**
- ❌ `streamlit_app.py` (web UI)
- ❌ `rest_api.py` (REST API)
- ❌ `locales/` (translations)
- ❌ `Dockerfile` / `docker-compose.yml`
- ❌ `.streamlit/` folder

**Dependencies:** NONE! The core genetics engine uses only Python standard library.

---

## 📦 Installation

### Option 1: Copy the folder
```bash
# Copy just the genetics folder to your project
cp -r genetics/ /path/to/your/project/
```

### Option 2: Install as package (optional)
```bash
# If you want to install it as a Python package
pip install -e .  # Run from the Horsegenetics directory
```

---

## 🚀 Basic Usage

### 1. Generate Random Horses

```python
from genetics.horse import Horse

# Generate a random horse
horse = Horse.random()

print(f"Phenotype: {horse.phenotype}")
print(f"Genotype: {horse.genotype_string}")

# Access specific genes
print(f"Extension: {horse.genotype['Extension']}")  # e.g., ['E', 'e']
print(f"Agouti: {horse.genotype['Agouti']}")       # e.g., ['A', 'a']
```

**Output example:**
```
Phenotype: Bay
Genotype: E/e A/A N/N nd1/nd1 n/n n/n F/f sty/sty g/g
Extension: ['E', 'e']
Agouti: ['A', 'A']
```

### 2. Breed Two Horses

```python
from genetics.horse import Horse

# Generate foundation horses
sire = Horse.random()
dam = Horse.random()

# Breed them
foal = Horse.breed(sire, dam)

print(f"Sire: {sire.phenotype}")
print(f"Dam: {dam.phenotype}")
print(f"Foal: {foal.phenotype}")
```

### 3. Create Horse with Specific Genetics

```python
from genetics.horse import Horse
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator

registry = get_default_registry()
calculator = PhenotypeCalculator(registry)

# Define exact genotype
genotype = {
    'Extension': ['E', 'E'],      # Homozygous black pigment
    'Agouti': ['A', 'A'],         # Homozygous bay
    'Cream': ['N', 'N'],          # No cream dilution
    'Dun': ['nd1', 'nd1'],        # No dun
    'Silver': ['n', 'n'],         # No silver
    'Champagne': ['n', 'n'],      # No champagne
    'Flaxen': ['F', 'F'],         # No flaxen
    'Sooty': ['sty', 'sty'],      # No sooty
    'Gray': ['g', 'g']            # No gray
}

# Calculate phenotype
phenotype = calculator.calculate_phenotype(genotype)

# Create horse
horse = Horse(genotype, phenotype)
print(f"Created horse: {horse.phenotype}")  # Will be "Bay"
```

### 4. Calculate Breeding Probabilities

```python
from genetics.breeding_stats import calculate_offspring_probabilities

# Calculate what offspring colors are possible
probabilities = calculate_offspring_probabilities(
    sire.genotype_string,
    dam.genotype_string
)

# Show results
for phenotype, probability in probabilities.items():
    percentage = probability * 100
    print(f"{phenotype}: {percentage:.1f}%")
```

**Output example:**
```
Bay: 56.2%
Black: 18.8%
Chestnut: 12.5%
Seal Brown: 6.2%
...
```

---

## 🎲 Example Integrations

### Example 1: Simple Game Integration

```python
"""
Simple breeding game with the genetics engine.
"""
from genetics.horse import Horse
from genetics.io import save_horses_to_json, load_horses_from_json
import json

class HorseGame:
    def __init__(self):
        self.player_horses = []

    def generate_starter_horses(self, count=3):
        """Give player some random horses to start."""
        for _ in range(count):
            horse = Horse.random()
            self.player_horses.append({
                'horse': horse,
                'name': f"Horse {len(self.player_horses) + 1}",
                'age': 0
            })

    def breed_horses(self, sire_idx, dam_idx):
        """Breed two horses from player's stable."""
        sire = self.player_horses[sire_idx]['horse']
        dam = self.player_horses[dam_idx]['horse']

        foal = Horse.breed(sire, dam)

        self.player_horses.append({
            'horse': foal,
            'name': f"Foal {len(self.player_horses) + 1}",
            'age': 0,
            'parents': (sire_idx, dam_idx)
        })

        return foal

    def save_game(self, filename='savegame.json'):
        """Save player's horses."""
        horses_data = [item['horse'].to_dict() for item in self.player_horses]
        with open(filename, 'w') as f:
            json.dump(horses_data, f, indent=2)

    def load_game(self, filename='savegame.json'):
        """Load player's horses."""
        with open(filename, 'r') as f:
            horses_data = json.load(f)

        from genetics.gene_registry import get_default_registry
        from genetics.gene_interaction import PhenotypeCalculator

        registry = get_default_registry()
        calculator = PhenotypeCalculator(registry)

        self.player_horses = []
        for data in horses_data:
            horse = Horse.from_dict(data, registry, calculator)
            self.player_horses.append({
                'horse': horse,
                'name': f"Horse {len(self.player_horses) + 1}",
                'age': 0
            })

# Usage
game = HorseGame()
game.generate_starter_horses(3)

# Show player's horses
for i, item in enumerate(game.player_horses):
    print(f"{i+1}. {item['name']}: {item['horse'].phenotype}")

# Breed first two horses
foal = game.breed_horses(0, 1)
print(f"\nNew foal: {foal.phenotype}")

# Save progress
game.save_game()
```

### Example 2: Discord Bot Integration

```python
"""
Discord bot for horse breeding game.
Requires: pip install discord.py
"""
import discord
from discord.ext import commands
from genetics.horse import Horse
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store user horses in a file
HORSES_FILE = 'user_horses.json'

def load_user_horses():
    """Load all users' horses."""
    if os.path.exists(HORSES_FILE):
        with open(HORSES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_horses(data):
    """Save all users' horses."""
    with open(HORSES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@bot.command()
async def start(ctx):
    """Give user 3 random starter horses."""
    user_id = str(ctx.author.id)
    horses_db = load_user_horses()

    if user_id in horses_db:
        await ctx.send("You already have horses! Use !stable to see them.")
        return

    # Generate 3 random horses
    horses = []
    for i in range(3):
        horse = Horse.random()
        horses.append({
            'name': f"Horse {i+1}",
            'genotype': horse.genotype,
            'phenotype': horse.phenotype
        })

    horses_db[user_id] = horses
    save_user_horses(horses_db)

    await ctx.send(
        f"🐴 Welcome to Horse Genetics Game!\n\n"
        f"You received 3 starter horses:\n"
        f"1. {horses[0]['phenotype']}\n"
        f"2. {horses[1]['phenotype']}\n"
        f"3. {horses[2]['phenotype']}\n\n"
        f"Use `!breed 1 2` to breed them!"
    )

@bot.command()
async def stable(ctx):
    """Show user's horses."""
    user_id = str(ctx.author.id)
    horses_db = load_user_horses()

    if user_id not in horses_db or not horses_db[user_id]:
        await ctx.send("You don't have any horses yet! Use !start to begin.")
        return

    horses = horses_db[user_id]
    message = "🏇 **Your Stable:**\n\n"
    for i, h in enumerate(horses, 1):
        message += f"{i}. **{h['name']}** - {h['phenotype']}\n"

    await ctx.send(message)

@bot.command()
async def breed(ctx, sire_num: int, dam_num: int):
    """Breed two horses."""
    user_id = str(ctx.author.id)
    horses_db = load_user_horses()

    if user_id not in horses_db:
        await ctx.send("You don't have any horses! Use !start first.")
        return

    horses = horses_db[user_id]

    # Validate indices
    if sire_num < 1 or sire_num > len(horses) or dam_num < 1 or dam_num > len(horses):
        await ctx.send(f"Invalid horse numbers! You have {len(horses)} horses.")
        return

    # Get parents
    from genetics.gene_registry import get_default_registry
    from genetics.gene_interaction import PhenotypeCalculator

    registry = get_default_registry()
    calculator = PhenotypeCalculator(registry)

    sire_data = horses[sire_num - 1]
    dam_data = horses[dam_num - 1]

    sire = Horse(sire_data['genotype'], sire_data['phenotype'])
    dam = Horse(dam_data['genotype'], dam_data['phenotype'])

    # Breed
    foal = Horse.breed(sire, dam)

    # Add to stable
    horses.append({
        'name': f"Foal {len(horses) + 1}",
        'genotype': foal.genotype,
        'phenotype': foal.phenotype
    })

    horses_db[user_id] = horses
    save_user_horses(horses_db)

    await ctx.send(
        f"🎉 **Breeding successful!**\n\n"
        f"Sire: {sire_data['name']} ({sire_data['phenotype']})\n"
        f"Dam: {dam_data['name']} ({dam_data['phenotype']})\n"
        f"Foal: **{foal.phenotype}** 🐴\n\n"
        f"The foal was added to your stable as #{len(horses)}"
    )

@bot.command()
async def genetics(ctx, horse_num: int):
    """Show detailed genetics of a horse."""
    user_id = str(ctx.author.id)
    horses_db = load_user_horses()

    if user_id not in horses_db:
        await ctx.send("You don't have any horses!")
        return

    horses = horses_db[user_id]

    if horse_num < 1 or horse_num > len(horses):
        await ctx.send(f"Invalid horse number! You have {len(horses)} horses.")
        return

    horse = horses[horse_num - 1]

    message = f"🧬 **{horse['name']} - {horse['phenotype']}**\n\n"
    message += "**Genotype:**\n```"
    for gene, alleles in horse['genotype'].items():
        message += f"{gene}: {'/'.join(alleles)}\n"
    message += "```"

    await ctx.send(message)

# Run bot
bot.run('YOUR_BOT_TOKEN_HERE')
```

### Example 3: REST API Endpoint

```python
"""
Simple Flask API for horse genetics.
Requires: pip install flask
"""
from flask import Flask, jsonify, request
from genetics.horse import Horse
from genetics.breeding_stats import calculate_offspring_probabilities

app = Flask(__name__)

@app.route('/api/generate', methods=['POST'])
def generate_horse():
    """Generate a random horse."""
    data = request.get_json() or {}
    count = data.get('count', 1)

    horses = []
    for _ in range(min(count, 10)):  # Limit to 10
        horse = Horse.random()
        horses.append({
            'phenotype': horse.phenotype,
            'genotype': horse.genotype,
            'genotype_string': horse.genotype_string
        })

    return jsonify({'horses': horses})

@app.route('/api/breed', methods=['POST'])
def breed_horses():
    """Breed two horses."""
    data = request.get_json()

    from genetics.gene_registry import get_default_registry
    from genetics.gene_interaction import PhenotypeCalculator

    registry = get_default_registry()
    calculator = PhenotypeCalculator(registry)

    # Reconstruct parent horses
    sire = Horse(data['sire']['genotype'], data['sire']['phenotype'])
    dam = Horse(data['dam']['genotype'], data['dam']['phenotype'])

    # Breed
    foal = Horse.breed(sire, dam)

    return jsonify({
        'foal': {
            'phenotype': foal.phenotype,
            'genotype': foal.genotype,
            'genotype_string': foal.genotype_string
        }
    })

@app.route('/api/probabilities', methods=['POST'])
def calculate_probabilities():
    """Calculate breeding outcome probabilities."""
    data = request.get_json()

    # Get genotype strings
    sire_geno = data['sire_genotype']
    dam_geno = data['dam_genotype']

    # Calculate
    probs = calculate_offspring_probabilities(sire_geno, dam_geno)

    # Convert to list for JSON
    result = [
        {'phenotype': pheno, 'probability': prob}
        for pheno, prob in probs.items()
    ]

    return jsonify({'probabilities': result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 🧬 Understanding the Genetics

### Available Genes (9 total)

| Gene | Alleles | Effect |
|------|---------|--------|
| **Extension** | E (dominant), e (recessive) | Black vs red pigment |
| **Agouti** | A (dominant), a (recessive) | Distribution of black pigment |
| **Cream** | Cr (incomplete dominant), N | Dilutes red/black pigment |
| **Dun** | D (dominant), nd1, nd2 | Primitive dilution with markings |
| **Silver** | Z (dominant), n | Dilutes black pigment only |
| **Champagne** | Ch (dominant), n | Dilutes all pigment |
| **Flaxen** | f (recessive), F | Lightens mane and tail on chestnuts |
| **Sooty** | Sty (dominant), sty | Darkens coat |
| **Gray** | G (dominant), g | Progressive graying with age |

### Common Phenotypes

- **Bay** = E/- A/- (black pigment restricted to points)
- **Black** = E/- a/a (black all over)
- **Chestnut** = e/e -/- (red pigment only)
- **Buckskin** = E/- A/- Cr/N (diluted bay)
- **Palomino** = e/e Cr/N (diluted chestnut)
- **Cremello** = e/e Cr/Cr (double diluted chestnut)

### Inheritance Rules

- **Mendelian inheritance**: Each parent contributes one random allele per gene
- **Independent assortment**: All genes segregate independently
- **Dominance hierarchy**: Some alleles are dominant, recessive, or co-dominant
- **50+ possible phenotypes** from 9 genes

---

## 💾 Save/Load System

### JSON Format

```python
from genetics.io import save_horses_to_json, load_horses_from_json

# Save horses
horses = [horse1, horse2, horse3]
save_horses_to_json(horses, 'stable.json')

# Load horses
loaded_horses = load_horses_from_json('stable.json')
```

### Custom Save Format

```python
import json

# Save
horses_data = [horse.to_dict() for horse in my_horses]
with open('my_save.json', 'w') as f:
    json.dump(horses_data, f, indent=2)

# Load
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator

registry = get_default_registry()
calculator = PhenotypeCalculator(registry)

with open('my_save.json', 'r') as f:
    horses_data = json.load(f)

my_horses = [
    Horse.from_dict(data, registry, calculator)
    for data in horses_data
]
```

---

## 🎯 Performance Notes

- **Horse generation**: ~0.001 seconds per horse
- **Breeding**: ~0.001 seconds per foal
- **Probability calculation**: ~0.05 seconds (calculates all 16,384 combinations)
- **Memory**: ~1 KB per horse object

The engine is very fast and can handle thousands of horses without issues.

---

## 📚 API Reference

### `Horse` class

```python
from genetics.horse import Horse

# Create random horse
horse = Horse.random()

# Create with specific genetics
horse = Horse(genotype_dict, phenotype_string)

# Breed two horses
foal = Horse.breed(sire, dam)

# Access properties
horse.phenotype        # e.g., "Bay"
horse.genotype         # dict of genes
horse.genotype_string  # e.g., "E/e A/A N/N ..."

# Serialize
data = horse.to_dict()
horse = Horse.from_dict(data, registry, calculator)
```

### `calculate_offspring_probabilities()`

```python
from genetics.breeding_stats import calculate_offspring_probabilities

# Get breeding probabilities
probabilities = calculate_offspring_probabilities(
    parent1_genotype_string,
    parent2_genotype_string
)

# Returns: dict of {phenotype: probability}
# Example: {"Bay": 0.5625, "Black": 0.1875, ...}
```

### `PedigreeTree` class (optional)

```python
from genetics.pedigree import PedigreeTree

tree = PedigreeTree()

# Track breeding
tree.add_breeding(
    sire, dam, foal,
    sire_name="Thunder",
    dam_name="Lightning",
    foal_name="Storm"
)

# Get ancestors
ancestors = tree.get_ancestors(horse_id, generations=3)

# Check inbreeding
repeated = tree.detect_inbreeding(horse_id, depth=4)
```

---

## 🤝 Support

**Questions or issues?**
- GitHub: https://github.com/Metroseksuaali/Horsegenetics
- Check the README.md for more examples
- All genetics code is in `genetics/` folder - well documented!

**License:** MIT - Use freely in your projects!

---

## ✨ Credits

This genetics engine was designed for **realistic horse breeding simulation** with:
- 9 real horse coat color genes
- Scientifically accurate inheritance
- 50+ possible phenotypes
- Fast performance for game integration

Perfect for:
- Horse breeding games
- Discord bots
- Educational tools
- Genetics simulators
- Any application needing realistic horse genetics!
