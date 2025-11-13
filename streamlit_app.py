#!/usr/bin/env python3
"""
Horse Genetics Simulator - Web Interface (Streamlit)

Modern, beautiful web-based interface for the horse genetics simulator.
No installation required - just run and open in browser!

Run with:
    pip install streamlit
    streamlit run streamlit_app.py

Or with Docker:
    docker-compose up web
    # Open http://localhost:8501
"""

import os
import streamlit as st
from genetics.horse import Horse
from genetics.breeding_stats import calculate_offspring_probabilities
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator
from genetics.pedigree import PedigreeTree
from genetics.io import save_horses_to_json, load_horses_from_json
import json
from datetime import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import io
import csv

# Load translations
def load_translations(lang='en'):
    """Load translation file for the specified language."""
    locale_path = os.path.join(os.path.dirname(__file__), 'locales', f'{lang}.json')
    try:
        with open(locale_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English if translation not found
        fallback_path = os.path.join(os.path.dirname(__file__), 'locales', 'en.json')
        with open(fallback_path, 'r', encoding='utf-8') as f:
            return json.load(f)

def t(key, lang='en', **kwargs):
    """
    Get translation for a dot-notation key.

    Args:
        key: Dot-notation key like "nav.generator"
        lang: Language code (default 'en')
        **kwargs: Placeholder replacements

    Returns:
        Translated string with placeholders replaced
    """
    translations = load_translations(lang)

    # Navigate through nested dict using dot notation
    keys = key.split('.')
    value = translations
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return key  # Return key if translation not found

    # Replace placeholders
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return value

def generate_random_horse_name() -> str:
    """
    Generate a random horse name by combining prefixes and suffixes.

    Returns:
        A randomly generated horse name
    """
    prefixes = [
        "Thunder", "Storm", "Star", "Moon", "Shadow", "Silver", "Golden",
        "Wild", "Spirit", "Midnight", "Dawn", "Sunset", "Lightning", "Frost",
        "Crystal", "Diamond", "Ruby", "Amber", "Ebony", "Pearl", "Mystic",
        "Royal", "Noble", "Brave", "Swift", "Mighty", "Majestic", "Elegant",
        "Dancing", "Running", "Flying", "Soaring", "Galloping", "Whispering"
    ]

    suffixes = [
        "Runner", "Dancer", "Wind", "Fire", "Sky", "Dream", "Hope", "Pride",
        "Glory", "Spirit", "Heart", "Soul", "Blaze", "Flash", "Storm", "Star",
        "Knight", "Prince", "Princess", "King", "Queen", "Warrior", "Legend",
        "Magic", "Wonder", "Beauty", "Grace", "Power", "Freedom", "Victory",
        "Champion", "Hero", "Destiny", "Fortune"
    ]

    # Also include some single-word names
    single_names = [
        "Thunderbolt", "Stardust", "Moonlight", "Shadowfax", "Starfire",
        "Nightshade", "Sunburst", "Avalanche", "Hurricane", "Tornado",
        "Comet", "Phoenix", "Pegasus", "Apollo", "Athena", "Zeus", "Hercules",
        "Valkyrie", "Odin", "Thor", "Artemis", "Aurora", "Eclipse", "Nebula"
    ]

    # 40% chance of single name, 60% chance of prefix + suffix
    if random.random() < 0.4:
        return random.choice(single_names)
    else:
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"

def get_phenotype_color(phenotype: str) -> tuple[str, str]:
    """
    Get CSS gradient color and text color for a phenotype.

    Args:
        phenotype: The horse's phenotype name

    Returns:
        Tuple of (gradient_css, text_color)
    """
    phenotype_lower = phenotype.lower()

    # Bay colors (brown tones)
    if any(x in phenotype_lower for x in ['bay', 'buckskin', 'amber champagne', 'gold champagne']):
        return "linear-gradient(135deg, #8B4513 0%, #A0522D 100%)", "white"

    # Black colors (dark tones)
    elif any(x in phenotype_lower for x in ['black', 'smoky black', 'smoky cream', 'classic champagne']):
        return "linear-gradient(135deg, #2C3E50 0%, #34495E 100%)", "white"

    # Chestnut colors (red/gold tones)
    elif any(x in phenotype_lower for x in ['chestnut', 'flaxen', 'palomino', 'apricot', 'gold pearl']):
        return "linear-gradient(135deg, #CD853F 0%, #DAA520 100%)", "white"

    # Cream colors (light tones)
    elif any(x in phenotype_lower for x in ['cremello', 'perlino', 'pearl']):
        return "linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%)", "#2C3E50"

    # Gray colors (gray tones)
    elif any(x in phenotype_lower for x in ['gray', 'grey', 'silver']):
        return "linear-gradient(135deg, #A9A9A9 0%, #C0C0C0 100%)", "white"

    # Champagne colors not covered above (gold tones)
    elif 'champagne' in phenotype_lower:
        return "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)", "white"

    # Default (purple gradient)
    else:
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "white"

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple (0-1 range for matplotlib)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))

def get_phenotype_color_hex(phenotype: str) -> str:
    """Get a solid hex color for phenotype (for matplotlib)."""
    phenotype_lower = phenotype.lower()

    # Bay colors (brown)
    if any(x in phenotype_lower for x in ['bay', 'buckskin', 'amber champagne', 'gold champagne']):
        return '#8B4513'
    # Black colors
    elif any(x in phenotype_lower for x in ['black', 'smoky black', 'smoky cream', 'classic champagne']):
        return '#2C3E50'
    # Chestnut colors (red/gold)
    elif any(x in phenotype_lower for x in ['chestnut', 'flaxen', 'palomino', 'apricot', 'gold pearl']):
        return '#CD853F'
    # Cream colors (light)
    elif any(x in phenotype_lower for x in ['cremello', 'perlino', 'pearl']):
        return '#FFF8DC'
    # Gray colors
    elif any(x in phenotype_lower for x in ['gray', 'grey', 'silver']):
        return '#A9A9A9'
    # Champagne
    elif 'champagne' in phenotype_lower:
        return '#FFD700'
    # Default
    else:
        return '#667eea'

def check_breeding_risks(parent1, parent2):
    """
    Check for potential lethal combinations in breeding.

    Args:
        parent1: First parent Horse object
        parent2: Second parent Horse object

    Returns:
        dict with 'has_risk', 'risk_type', 'risk_percentage', 'warning_message'
    """
    risks = []

    # Check Frame Overo (LWOS risk)
    parent1_frame = parent1.genotype.get('frame', ('n', 'n'))
    parent2_frame = parent2.genotype.get('frame', ('n', 'n'))

    if 'O' in parent1_frame and 'O' in parent2_frame:
        risks.append({
            'type': 'LWOS',
            'percentage': 25,
            'message': '⚠️ **LWOS RISK**: Both parents carry Frame Overo (O). 25% chance of lethal white foal that will not survive.'
        })

    # Check Dominant White lethal combinations
    lethal_w_alleles = ['W1', 'W5', 'W10', 'W13', 'W22']
    parent1_w = parent1.genotype.get('dominant_white', ('n', 'n'))
    parent2_w = parent2.genotype.get('dominant_white', ('n', 'n'))

    parent1_has_lethal_w = any(allele in lethal_w_alleles for allele in parent1_w)
    parent2_has_lethal_w = any(allele in lethal_w_alleles for allele in parent2_w)

    if parent1_has_lethal_w and parent2_has_lethal_w:
        # Check if they have the same lethal W allele
        for allele in lethal_w_alleles:
            if allele in parent1_w and allele in parent2_w:
                risks.append({
                    'type': 'Dominant White',
                    'percentage': 25,
                    'message': f'⚠️ **DOMINANT WHITE RISK**: Both parents carry {allele}. 25% chance of lethal homozygous {allele}/{allele} embryo.'
                })
                break

    if risks:
        return {
            'has_risk': True,
            'risks': risks,
            'total_survival_rate': 100 - sum(r['percentage'] for r in risks)
        }
    else:
        return {'has_risk': False, 'risks': []}


def generate_pedigree_tree_image(pedigree_tree, horse_id, depth=3):
    """
    Generate a modern, beautiful pedigree tree using matplotlib.

    Args:
        pedigree_tree: PedigreeTree object
        horse_id: ID of the horse to visualize
        depth: Number of generations to show

    Returns:
        BytesIO buffer containing PNG image
    """
    selected_horse = pedigree_tree.horses[horse_id]
    ancestors = pedigree_tree.get_ancestors(horse_id, depth)

    # Organize horses by generation
    by_generation = {0: [selected_horse]}
    for ancestor in ancestors:
        gen_dist = selected_horse.generation - ancestor.generation
        if gen_dist not in by_generation:
            by_generation[gen_dist] = []
        by_generation[gen_dist].append(ancestor)

    # Create figure with modern styling
    fig, ax = plt.subplots(figsize=(16, 12), facecolor='#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    ax.set_xlim(-0.7, depth + 0.7)
    ax.set_ylim(-1.5, len(by_generation.get(max(by_generation.keys()), [])) + 1.5)
    ax.axis('off')

    # Calculate positions for each horse
    positions = {}

    def calculate_positions_recursive(horse, gen_level, y_position):
        """Recursively calculate positions for the tree."""
        positions[horse.horse_id] = (gen_level, y_position)

        if gen_level < depth:
            # Get parents
            sire = pedigree_tree.horses.get(horse.sire_id) if horse.sire_id else None
            dam = pedigree_tree.horses.get(horse.dam_id) if horse.dam_id else None

            if sire:
                calculate_positions_recursive(sire, gen_level + 1, y_position + 0.6)
            if dam:
                calculate_positions_recursive(dam, gen_level + 1, y_position - 0.6)

    # Start from selected horse
    calculate_positions_recursive(selected_horse, 0, 0)

    # Draw connections with modern gradient style
    for horse_id, (x, y) in positions.items():
        horse = pedigree_tree.horses[horse_id]
        if horse.sire_id and horse.sire_id in positions:
            sire_x, sire_y = positions[horse.sire_id]
            # Draw curved connection to sire
            ax.plot([x + 0.45, (x + sire_x)/2, sire_x - 0.45],
                   [y, (y + sire_y)/2, sire_y],
                   color='#667eea', alpha=0.4, linewidth=2.5, zorder=1)
        if horse.dam_id and horse.dam_id in positions:
            dam_x, dam_y = positions[horse.dam_id]
            # Draw curved connection to dam
            ax.plot([x + 0.45, (x + dam_x)/2, dam_x - 0.45],
                   [y, (y + dam_y)/2, dam_y],
                   color='#f093fb', alpha=0.4, linewidth=2.5, zorder=1)

    # Draw horse boxes with modern card design
    for horse_id, (x, y) in positions.items():
        horse = pedigree_tree.horses[horse_id]

        # Get color
        color_hex = get_phenotype_color_hex(horse.phenotype)
        color_rgb = hex_to_rgb(color_hex)

        # Determine text color based on background brightness
        brightness = (color_rgb[0] * 299 + color_rgb[1] * 587 + color_rgb[2] * 114) / 1000
        text_color = 'white' if brightness < 0.5 else '#2d3748'

        # Draw shadow for depth
        shadow = FancyBboxPatch(
            (x - 0.42, y - 0.22),
            0.9, 0.42,
            boxstyle="round,pad=0.03",
            facecolor='#00000020',
            edgecolor='none',
            zorder=2
        )
        ax.add_patch(shadow)

        # Draw main card with gradient effect
        box = FancyBboxPatch(
            (x - 0.45, y - 0.2),
            0.9, 0.4,
            boxstyle="round,pad=0.03",
            facecolor=color_rgb,
            edgecolor='white' if x == 0 else '#e2e8f0',
            linewidth=4 if x == 0 else 2,
            zorder=3
        )
        ax.add_patch(box)

        # Add gender icon
        gender_icon = '♂' if 'sire' in horse.name.lower() or x > 0 and y > 0 else '♀'
        if x == 0:
            gender_icon = '🐴'

        ax.text(x - 0.38, y + 0.12, gender_icon, ha='left', va='center',
                fontsize=11, color=text_color, zorder=4)

        # Add name with better typography
        name_text = horse.name if len(horse.name) <= 15 else horse.name[:13] + '...'
        ax.text(x, y + 0.08, name_text, ha='center', va='center',
                fontsize=10, fontweight='bold', color=text_color,
                fontfamily='sans-serif', zorder=4)

        # Add phenotype with truncation
        phenotype_text = horse.phenotype if len(horse.phenotype) <= 20 else horse.phenotype[:18] + '...'
        ax.text(x, y - 0.08, phenotype_text, ha='center', va='center',
                fontsize=8, color=text_color, style='italic',
                fontfamily='sans-serif', alpha=0.9, zorder=4)

        # Add generation badge for subject
        if x == 0:
            badge = FancyBboxPatch(
                (x - 0.15, y + 0.22),
                0.3, 0.12,
                boxstyle="round,pad=0.01",
                facecolor='#48bb78',
                edgecolor='white',
                linewidth=1.5,
                zorder=5
            )
            ax.add_patch(badge)
            ax.text(x, y + 0.28, 'Subject', ha='center', va='center',
                    fontsize=7, fontweight='bold', color='white', zorder=6)

    # Add modern generation labels with better styling
    for gen_level in range(depth + 1):
        if gen_level == 0:
            label = "🎯 Subject"
            color = '#48bb78'
        elif gen_level == 1:
            label = "👨‍👩 Parents"
            color = '#667eea'
        elif gen_level == 2:
            label = "👴👵 Grandparents"
            color = '#f093fb'
        elif gen_level == 3:
            label = "🌳 Great-Grandparents"
            color = '#feca57'
        else:
            label = f"Gen -{gen_level}"
            color = '#a0aec0'

        # Background badge for generation label
        label_bg = FancyBboxPatch(
            (gen_level - 0.35, -1.15),
            0.7, 0.25,
            boxstyle="round,pad=0.02",
            facecolor=color,
            edgecolor='white',
            linewidth=2,
            alpha=0.9,
            zorder=4
        )
        ax.add_patch(label_bg)

        ax.text(gen_level, -1.02, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color='white',
                fontfamily='sans-serif', zorder=5)

    # Add modern title with styling
    title_text = f"🐴 Family Tree: {selected_horse.name}"
    plt.text(depth/2, max(positions.values(), key=lambda p: p[1])[1] + 0.8,
             title_text,
             ha='center', va='center',
             fontsize=18, fontweight='bold',
             color='#2d3748',
             fontfamily='sans-serif',
             bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='white',
                      edgecolor='#667eea',
                      linewidth=3))

    # Save to buffer with high quality
    buf = io.BytesIO()
    plt.tight_layout(pad=1.5)
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                facecolor='#f8f9fa', edgecolor='none')
    plt.close(fig)
    buf.seek(0)

    return buf

def export_horses_to_csv(horses_list):
    """
    Export horses to CSV format.

    Args:
        horses_list: List of horse items from session state

    Returns:
        CSV string
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = ['Name', 'Phenotype', 'Extension', 'Agouti', 'Cream', 'Dun', 'Silver',
              'Champagne', 'Flaxen', 'Sooty', 'Gray', 'Has_Parents', 'Generated_At']
    writer.writerow(header)

    # Write horse data
    for item in horses_list:
        horse = item['horse']
        name = item['name']
        generated_at = item.get('generated_at', '')
        has_parents = 'Yes' if 'parents' in item else 'No'

        row = [
            name,
            horse.phenotype,
            '/'.join(horse.genotype.get('Extension', [''])),
            '/'.join(horse.genotype.get('Agouti', [''])),
            '/'.join(horse.genotype.get('Cream', [''])),
            '/'.join(horse.genotype.get('Dun', [''])),
            '/'.join(horse.genotype.get('Silver', [''])),
            '/'.join(horse.genotype.get('Champagne', [''])),
            '/'.join(horse.genotype.get('Flaxen', [''])),
            '/'.join(horse.genotype.get('Sooty', [''])),
            '/'.join(horse.genotype.get('Gray', [''])),
            has_parents,
            generated_at
        ]
        writer.writerow(row)

    return output.getvalue()

def import_horses_from_csv(csv_content):
    """
    Import horses from CSV format.

    Args:
        csv_content: CSV file content as string

    Returns:
        List of horse items for session state
    """
    registry = get_default_registry()
    calculator = PhenotypeCalculator(registry)

    horses_list = []
    reader = csv.DictReader(io.StringIO(csv_content.decode('utf-8')))

    for row in reader:
        # Build genotype dict from CSV columns
        genotype = {
            'Extension': row['Extension'].split('/') if row['Extension'] else ['E', 'E'],
            'Agouti': row['Agouti'].split('/') if row['Agouti'] else ['A', 'A'],
            'Cream': row['Cream'].split('/') if row['Cream'] else ['N', 'N'],
            'Dun': row['Dun'].split('/') if row['Dun'] else ['nd1', 'nd1'],
            'Silver': row['Silver'].split('/') if row['Silver'] else ['n', 'n'],
            'Champagne': row['Champagne'].split('/') if row['Champagne'] else ['n', 'n'],
            'Flaxen': row['Flaxen'].split('/') if row['Flaxen'] else ['F', 'F'],
            'Sooty': row['Sooty'].split('/') if row['Sooty'] else ['sty', 'sty'],
            'Gray': row['Gray'].split('/') if row['Gray'] else ['g', 'g']
        }

        # Calculate phenotype
        phenotype = calculator.calculate_phenotype(genotype)

        # Create horse
        horse = Horse(genotype, phenotype)

        # Create item
        item = {
            'horse': horse,
            'name': row['Name'],
            'generated_at': row.get('Generated_At', datetime.now().isoformat())
        }

        horses_list.append(item)

    return horses_list

# Page configuration
st.set_page_config(
    page_title="Horse Genetics Simulator",
    page_icon="🐴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .horse-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    .pedigree-box {
        padding: 1rem;
        border-radius: 8px;
        background: #f8f9fa;
        border: 2px solid #667eea;
        margin: 0.5rem 0;
    }
    .ancestor-box {
        padding: 0.8rem;
        border-radius: 6px;
        background: #e9ecef;
        margin: 0.3rem 0;
        border-left: 3px solid #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'horses' not in st.session_state:
    st.session_state.horses = []
if 'pedigree' not in st.session_state:
    st.session_state.pedigree = PedigreeTree()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

# Get current language
lang = st.session_state.lang

# Sidebar
with st.sidebar:
    st.markdown(f"# 🐴 {t('sidebar.title', lang)}")
    st.markdown(f"### {t('sidebar.version', lang)}")
    st.markdown("---")

    # Language selector
    def format_language(lang_code):
        trans = load_translations(lang_code)
        return f"{trans['language_flag']} {trans['language_name']}"

    selected_lang = st.selectbox(
        t('sidebar.language', lang),
        options=["en", "fi"],
        index=["en", "fi"].index(st.session_state.lang),
        format_func=format_language,
        key="language_selector"
    )

    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "**📍 Navigation**",
        [t('nav.generator', lang), t('nav.breeding', lang), t('nav.probability', lang),
         t('nav.stable', lang), t('nav.pedigree', lang), t('nav.compare', lang),
         t('nav.statistics', lang), t('nav.about', lang)],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Quick stats
    if st.session_state.horses:
        st.markdown(f"### 📊 {t('sidebar.quick_stats', lang)}")
        st.metric(t('sidebar.total_horses', lang), len(st.session_state.horses))
        st.metric(t('sidebar.in_pedigree', lang), len(st.session_state.pedigree.horses))

    st.markdown("---")
    st.caption(f"🔬 {t('sidebar.scientifically_accurate', lang)}")
    st.caption(f"⚡ {t('sidebar.performance', lang)}")
    st.caption("[💻 GitHub](https://github.com/Metroseksuaali/Horsegenetics)")

# Main content
if page == t('nav.generator', lang):
    st.markdown(f'<p class="main-header">🎲 {t("generator.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("generator.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('generator.how_to_use', lang)}", expanded=False):
        st.markdown(t('generator.instructions', lang))

    st.markdown("---")

    # Controls in a nice box
    with st.container():
        col1, col2 = st.columns([2, 2])

        with col1:
            num_horses = st.slider(f"🔢 {t('generator.how_many', lang)}", 1, 10, 1)

        with col2:
            auto_name = st.checkbox(t('generator.auto_generate_names', lang), value=True)

        if st.button(t('generator.generate_button', lang), type="primary", use_container_width=True):
            with st.spinner(f"🔮 {t('generator.generating', lang)}"):
                generated = []
                for i in range(num_horses):
                    horse = Horse.random()
                    generated.append(horse)

                    # Generate name based on auto_name setting
                    if auto_name:
                        horse_name = generate_random_horse_name()
                    else:
                        horse_name = f"Horse {len(st.session_state.horses) + 1}"

                    st.session_state.horses.append({
                        'horse': horse,
                        'name': horse_name,
                        'generated_at': datetime.now().isoformat()
                    })

                st.success(f"🎉 {t('generator.success', lang, count=num_horses)}")

                # Display generated horses in a nice grid
                st.markdown(f"### 🐴 {t('generator.your_new_horses', lang)}")

                for i, horse in enumerate(generated):
                    with st.expander(f"✨ {horse.phenotype}", expanded=True):
                        col_a, col_b = st.columns([2, 1])

                        with col_a:
                            st.markdown(f"**🎨 {t('generator.color', lang)}:** {horse.phenotype}")
                            st.code(horse.genotype_string, language="text")

                        with col_b:
                            st.markdown(f"**📊 {t('generator.genetics', lang)}**")
                            for gene_name, alleles in list(horse.genotype.items())[:3]:
                                st.caption(f"{gene_name}: {'/'.join(alleles)}")

    st.markdown("---")

    # Show recent horses in a beautiful grid
    if st.session_state.horses:
        st.markdown(f"### 📋 {t('generator.recent_horses', lang)}")
        recent = st.session_state.horses[-6:][::-1]

        cols = st.columns(3)
        for idx, item in enumerate(recent):
            with cols[idx % 3]:
                horse = item['horse']
                name = item['name']
                gradient, text_color = get_phenotype_color(horse.phenotype)

                st.markdown(f"""
                <div class="horse-card" style="background: {gradient}; color: {text_color};">
                    <h3>🐴 {name}</h3>
                    <p style="font-size: 1.1rem; margin: 0;">{horse.phenotype}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"👋 {t('generator.welcome', lang)}")

elif page == t('nav.breeding', lang):
    st.markdown(f'<p class="main-header">🧬 {t("breeding.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("breeding.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('breeding.how_to_use', lang)}", expanded=False):
        st.markdown(t('breeding.instructions', lang))

    st.markdown("---")

    if len(st.session_state.horses) < 2:
        st.warning(f"⚠️ {t('breeding.need_horses', lang)}")
        if st.button(f"🎲 {t('breeding.go_to_generator', lang)}"):
            st.rerun()
    else:
        horse_names = [f"{item['name']} - {item['horse'].phenotype}"
                       for item in st.session_state.horses]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 👨 {t('breeding.sire', lang)}")
            parent1_idx = st.selectbox(t('breeding.choose_sire', lang), range(len(horse_names)),
                                       format_func=lambda x: horse_names[x], key="p1",
                                       label_visibility="collapsed")
            parent1 = st.session_state.horses[parent1_idx]['horse']

            with st.expander(f"🔬 {t('breeding.view_genotype', lang)}"):
                st.code(parent1.genotype_string, language="text")

        with col2:
            st.markdown(f"### 👩 {t('breeding.dam', lang)}")
            parent2_idx = st.selectbox(t('breeding.choose_dam', lang), range(len(horse_names)),
                                       format_func=lambda x: horse_names[x], key="p2",
                                       label_visibility="collapsed")
            parent2 = st.session_state.horses[parent2_idx]['horse']

            with st.expander(f"🔬 {t('breeding.view_genotype', lang)}"):
                st.code(parent2.genotype_string, language="text")

        st.markdown("<br>", unsafe_allow_html=True)

        # Check for breeding risks
        risk_check = check_breeding_risks(parent1, parent2)
        if risk_check['has_risk']:
            st.error("🚨 **WARNING: Lethal Gene Combination Detected!**")
            for risk in risk_check['risks']:
                st.warning(risk['message'])
            st.info(f"💡 **Recommendation**: Avoid this breeding pair. Choose a parent without the {risk_check['risks'][0]['type']} gene to ensure 100% viable foals.")
            st.markdown("---")

        # Foal naming section
        st.markdown(f"### 🏷️ {t('generator.naming_title', lang)}")
        col_name1, col_name2 = st.columns([3, 1])

        with col_name1:
            foal_name = st.text_input(
                t('breeding.foal_name', lang),
                value="",
                placeholder=t('breeding.foal_name_placeholder', lang),
                key="foal_name_input"
            )

        with col_name2:
            if st.button(t('generator.random_name', lang), use_container_width=True):
                st.session_state.suggested_foal_name = generate_random_horse_name()
                st.rerun()

        # Use suggested name if available
        if 'suggested_foal_name' in st.session_state and not foal_name:
            foal_name = st.session_state.suggested_foal_name
            st.info(f"💡 Suggested: **{foal_name}**")

        st.markdown("<br>", unsafe_allow_html=True)

        # Center the breed button
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(t('breeding.breed_button', lang), type="primary", use_container_width=True):
                with st.spinner(f"🔬 {t('breeding.breeding', lang)}"):
                    offspring = Horse.breed(parent1, parent2)

                    # Check if offspring is NONVIABLE
                    is_nonviable = 'NONVIABLE' in offspring.phenotype

                    if is_nonviable:
                        # Show sad message for lethal foal
                        st.error("💔 **Breeding Resulted in Non-Viable Foal**")

                        st.markdown("### ⚠️ What Happened?")
                        col_res1, col_res2, col_res3 = st.columns(3)

                        with col_res1:
                            st.markdown(f"**👨 {t('breeding.sire', lang)}**")
                            st.info(parent1.phenotype)

                        with col_res2:
                            st.markdown(f"**❌ {t('breeding.offspring', lang)}**")
                            st.error(f"**{offspring.phenotype}**")

                        with col_res3:
                            st.markdown(f"**👩 {t('breeding.dam', lang)}**")
                            st.info(parent2.phenotype)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Explain the genetics
                        st.warning("""
                        **🧬 Genetic Explanation:**

                        This foal inherited a lethal gene combination from both parents. In real horse breeding:
                        - **LWOS (Lethal White Overo Syndrome)**: O/O foals are born all white but lack nerve cells in their intestines. They die within 2-3 days.
                        - **Dominant White homozygous**: Most W/W combinations (except W20/W20) result in embryonic death.

                        **This foal was NOT added to your stable.**
                        """)

                        st.info("""
                        💡 **Breeding Recommendation:**

                        To avoid lethal foals:
                        - ❌ **DON'T breed** Frame Overo (O/n) × Frame Overo (O/n)
                        - ❌ **DON'T breed** two horses with the same lethal Dominant White allele
                        - ✅ **DO breed** Frame Overo (O/n) × Solid (n/n) - 100% viable!
                        - ✅ **DO breed** Dominant White (W/n) × Solid (n/n) - 100% viable!
                        """)

                        with st.expander(f"🧬 {t('breeding.offspring_genotype', lang)}", expanded=False):
                            st.code(offspring.genotype_string, language="text")

                    else:
                        # Healthy foal - add to stable
                        # Use provided name or generate default
                        if not foal_name:
                            foal_name = generate_random_horse_name()

                        st.session_state.horses.append({
                            'horse': offspring,
                            'name': foal_name,
                            'generated_at': datetime.now().isoformat(),
                            'parents': (parent1_idx, parent2_idx)
                        })

                        # Add to pedigree
                        st.session_state.pedigree.add_breeding(
                            parent1, parent2, offspring,
                            sire_name=st.session_state.horses[parent1_idx]['name'],
                            dam_name=st.session_state.horses[parent2_idx]['name'],
                            foal_name=foal_name
                        )

                        # Clear suggested name after breeding
                        if 'suggested_foal_name' in st.session_state:
                            del st.session_state.suggested_foal_name

                        st.success(f"🎊 {t('breeding.congratulations', lang)}")

                        # Display offspring beautifully
                        st.markdown(f"### 🐴 {t('breeding.meet_foal', lang)}")

                        col_res1, col_res2, col_res3 = st.columns(3)

                        with col_res1:
                            st.markdown(f"**👨 {t('breeding.sire', lang)}**")
                            st.info(parent1.phenotype)

                        with col_res2:
                            st.markdown(f"**🐴 {t('breeding.offspring', lang)}**")
                            st.success(f"**{offspring.phenotype}**")

                        with col_res3:
                            st.markdown(f"**👩 {t('breeding.dam', lang)}**")
                            st.info(parent2.phenotype)

                        st.markdown("<br>", unsafe_allow_html=True)

                        with st.expander(f"🧬 {t('breeding.offspring_genotype', lang)}", expanded=True):
                            st.code(offspring.genotype_string, language="text")

elif page == t('nav.probability', lang):
    st.markdown(f'<p class="main-header">📊 {t("probability.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("probability.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('probability.how_to_use', lang)}", expanded=False):
        st.markdown(t('probability.instructions', lang))

    st.markdown("---")

    if len(st.session_state.horses) < 2:
        st.warning(f"⚠️ {t('probability.need_horses', lang)}")
    else:
        horse_names = [f"{item['name']} - {item['horse'].phenotype}"
                       for item in st.session_state.horses]

        col1, col2 = st.columns(2)

        with col1:
            parent1_idx = st.selectbox(f"👨 {t('probability.select_parent1', lang)}", range(len(horse_names)),
                                      format_func=lambda x: horse_names[x])
            parent1 = st.session_state.horses[parent1_idx]['horse']

        with col2:
            parent2_idx = st.selectbox(f"👩 {t('probability.select_parent2', lang)}", range(len(horse_names)),
                                      format_func=lambda x: horse_names[x])
            parent2 = st.session_state.horses[parent2_idx]['horse']

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(t('probability.calculate_button', lang), type="primary", use_container_width=True):
            with st.spinner(f"🧮 {t('probability.calculating', lang)}"):
                probs = calculate_offspring_probabilities(
                    parent1.genotype_string,
                    parent2.genotype_string
                )

                st.success(f"✅ {t('probability.complete', lang)}")

                st.markdown(f"### 📈 {t('probability.distribution', lang)}")

                # Show top results
                top_results = list(probs.items())[:10]

                for phenotype, prob in top_results:
                    col_name, col_bar = st.columns([1, 3])

                    with col_name:
                        st.markdown(f"**{phenotype}**")

                    with col_bar:
                        st.progress(prob, text=f"{prob*100:.1f}%")

                st.markdown("<br>", unsafe_allow_html=True)

                # Detailed table
                with st.expander(f"📋 {t('probability.view_all', lang)}"):
                    import pandas as pd
                    df = pd.DataFrame({
                        t('probability.phenotype', lang): list(probs.keys()),
                        t('probability.probability_label', lang): [f"{v*100:.2f}%" for v in probs.values()]
                    })
                    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == t('nav.stable', lang):
    st.markdown(f'<p class="main-header">📚 {t("stable.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("stable.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('stable.how_to_use', lang)}", expanded=False):
        st.markdown(t('stable.instructions', lang))

    st.markdown("---")

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"🐴 {t('stable.total_horses', lang)}", len(st.session_state.horses))
    with col2:
        bred = sum(1 for h in st.session_state.horses if 'parents' in h)
        st.metric(f"🧬 {t('stable.bred_horses', lang)}", bred)
    with col3:
        foundation = len(st.session_state.horses) - bred
        st.metric(f"✨ {t('stable.foundation', lang)}", foundation)
    with col4:
        st.metric(f"🌳 {t('sidebar.in_pedigree', lang)}", len(st.session_state.pedigree.horses))

    st.markdown("---")

    # Search and Filter section
    st.markdown(f"### 🔍 {t('stable.search_filter_title', lang)}")

    col_search, col_pheno, col_type = st.columns(3)

    with col_search:
        search_term = st.text_input(
            t('stable.search_name', lang),
            key="horse_search",
            placeholder=t('stable.search_name', lang)
        )

    with col_pheno:
        # Get unique phenotypes from horses
        phenotypes = set()
        for item in st.session_state.horses:
            phenotypes.add(item['horse'].phenotype)
        phenotype_options = [t('stable.filter_all', lang)] + sorted(list(phenotypes))

        selected_phenotype = st.selectbox(
            t('stable.filter_phenotype', lang),
            phenotype_options,
            key="phenotype_filter"
        )

    with col_type:
        type_options = [
            t('stable.filter_all', lang),
            t('stable.filter_foundation', lang),
            t('stable.filter_bred', lang)
        ]
        selected_type = st.selectbox(
            t('stable.filter_type', lang),
            type_options,
            key="type_filter"
        )

    # Apply filters
    filtered_horses = []
    for idx, item in enumerate(st.session_state.horses):
        horse = item['horse']
        name = item['name']

        # Name filter (case-insensitive)
        if search_term and search_term.lower() not in name.lower():
            continue

        # Phenotype filter
        if selected_phenotype != t('stable.filter_all', lang) and horse.phenotype != selected_phenotype:
            continue

        # Type filter
        if selected_type == t('stable.filter_foundation', lang) and 'parents' in item:
            continue
        elif selected_type == t('stable.filter_bred', lang) and 'parents' not in item:
            continue

        filtered_horses.append((idx, item))

    # Show count
    st.caption(t('stable.showing_count', lang, filtered=len(filtered_horses), total=len(st.session_state.horses)))

    st.markdown("---")

    # Action buttons - Row 1: JSON and CSV Export
    col_act1, col_act2 = st.columns(2)

    with col_act1:
        if st.session_state.horses:
            horses_data = [item['horse'].to_dict() for item in st.session_state.horses]
            json_str = json.dumps(horses_data, indent=2)
            st.download_button(
                t('stable.save_button', lang),
                json_str,
                file_name=f"stable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    with col_act2:
        if st.session_state.horses:
            csv_str = export_horses_to_csv(st.session_state.horses)
            st.download_button(
                t('stable.save_csv_button', lang),
                csv_str,
                file_name=f"stable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Action buttons - Row 2: JSON and CSV Import, Clear
    col_act3, col_act4, col_act5 = st.columns(3)

    with col_act3:
        uploaded_json = st.file_uploader(t('stable.load_button', lang), type=['json'], label_visibility="collapsed", key="json_upload")
        if uploaded_json is not None:
            try:
                horses_data = json.load(uploaded_json)
                registry = get_default_registry()
                calculator = PhenotypeCalculator(registry)

                for data in horses_data:
                    horse = Horse.from_dict(data, registry, calculator)
                    st.session_state.horses.append({
                        'horse': horse,
                        'name': f"Imported {len(st.session_state.horses) + 1}",
                        'generated_at': datetime.now().isoformat()
                    })

                st.success(f"✅ {t('stable.loaded', lang, count=len(horses_data))}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {t('stable.error_loading', lang, error=str(e))}")

    with col_act4:
        uploaded_csv = st.file_uploader(t('stable.load_csv_button', lang), type=['csv'], label_visibility="collapsed", key="csv_upload")
        if uploaded_csv is not None:
            try:
                csv_content = uploaded_csv.read()
                imported_horses = import_horses_from_csv(csv_content)

                for item in imported_horses:
                    st.session_state.horses.append(item)

                st.success(f"✅ {t('stable.loaded', lang, count=len(imported_horses))}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {t('stable.error_loading', lang, error=str(e))}")

    with col_act5:
        if st.button(t('stable.clear_button', lang), use_container_width=True):
            st.session_state.horses = []
            st.session_state.pedigree = PedigreeTree()
            st.rerun()

    st.markdown("---")

    # Display horses in grid
    if st.session_state.horses:
        st.markdown(f"### 🐴 {t('stable.all_horses', lang)}")

        if filtered_horses:
            for idx, item in filtered_horses:
                horse = item['horse']
                name = item['name']

                with st.expander(f"🐴 {name} - {horse.phenotype}"):
                    col_info1, col_info2 = st.columns([2, 1])

                    with col_info1:
                        st.markdown(f"**🎨 {t('stable.phenotype_label', lang)}:** {horse.phenotype}")
                        st.code(horse.genotype_string, language="text")

                    with col_info2:
                        if 'parents' in item:
                            p1_name = st.session_state.horses[item['parents'][0]]['name']
                            p2_name = st.session_state.horses[item['parents'][1]]['name']
                            st.markdown(f"**👪 {t('stable.parents_label', lang)}:**")
                            st.caption(f"👨 {p1_name}")
                            st.caption(f"👩 {p2_name}")
                        else:
                            st.info(f"✨ {t('stable.foundation_horse', lang)}")

                    # Rename option
                    col_rename1, col_rename2 = st.columns([3, 1])

                    with col_rename1:
                        new_name = st.text_input(
                            f"✏️ {t('stable.rename', lang)}",
                            value=name,
                            key=f"rename_{idx}"
                        )

                    with col_rename2:
                        st.markdown("<br>", unsafe_allow_html=True)  # Align button with text input
                        if st.button(t('stable.generate_random_name', lang), key=f"gen_name_{idx}"):
                            st.session_state.horses[idx]['name'] = generate_random_horse_name()
                            st.rerun()

                    if new_name != name:
                        st.session_state.horses[idx]['name'] = new_name
                        st.rerun()
        else:
            st.info(f"🔍 {t('stable.no_results', lang)}")
    else:
        st.info(f"👋 {t('stable.empty_stable', lang)}")

elif page == t('nav.pedigree', lang):
    st.markdown(f'<p class="main-header">🌳 {t("pedigree.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("pedigree.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('pedigree.how_to_use', lang)}", expanded=False):
        st.markdown(t('pedigree.instructions', lang))

    st.markdown("---")

    if len(st.session_state.pedigree.horses) == 0:
        st.warning(f"⚠️ {t('pedigree.no_data', lang)}")
        st.info(f"💡 {t('pedigree.how_to_build', lang)}")
    else:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"🐴 {t('pedigree.total', lang)}", len(st.session_state.pedigree.horses))
        with col2:
            st.metric(f"🧬 {t('pedigree.breedings', lang)}", len(st.session_state.pedigree.breedings))
        with col3:
            max_gen = max(h.generation for h in st.session_state.pedigree.horses.values())
            st.metric(f"📊 {t('pedigree.generations', lang)}", max_gen + 1)
        with col4:
            foundation = sum(1 for h in st.session_state.pedigree.horses.values()
                           if h.sire_id is None and h.dam_id is None)
            st.metric(f"✨ {t('stable.foundation', lang)}", foundation)

        st.markdown("---")

        # Simplified pedigree view
        st.markdown(f"### 🐴 {t('pedigree.select_horse', lang)}")

        horse_options = {h.name: h.horse_id for h in st.session_state.pedigree.horses.values()}
        horse_list = list(horse_options.keys())

        col_select, col_depth = st.columns([3, 1])

        with col_select:
            selected_name = st.selectbox(t('pedigree.choose_horse', lang), horse_list, label_visibility="collapsed")

        with col_depth:
            depth = st.selectbox(t('pedigree.generations_label', lang), [1, 2, 3, 4, 5], index=2)

        if selected_name:
            selected_id = horse_options[selected_name]
            selected_horse = st.session_state.pedigree.horses[selected_id]

            st.markdown("---")

            # Display selected horse
            st.markdown(f"""
            <div class="pedigree-box">
                <h2>🐴 {selected_name}</h2>
                <p style="font-size: 1.3rem; margin: 0.5rem 0;">🎨 {selected_horse.phenotype}</p>
                <p style="color: #6c757d; margin: 0;">📊 {t('pedigree.generation', lang)} {selected_horse.generation}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Get ancestors
            ancestors = st.session_state.pedigree.get_ancestors(selected_id, depth)

            if ancestors:
                st.markdown(f"### 🌳 {t('pedigree.family_tree', lang)} ({len(ancestors)} {t('pedigree.ancestors', lang)})")

                # Organize ancestors by generation distance
                by_distance = {}
                for ancestor in ancestors:
                    gen_dist = selected_horse.generation - ancestor.generation
                    if gen_dist not in by_distance:
                        by_distance[gen_dist] = []
                    by_distance[gen_dist].append(ancestor)

                # Display each generation
                for dist in sorted(by_distance.keys()):
                    if dist == 1:
                        st.markdown(f"### 👥 {t('pedigree.parents', lang)}")
                        icon = "👤"
                    elif dist == 2:
                        st.markdown(f"### 👴👵 {t('pedigree.grandparents', lang)}")
                        icon = "👴"
                    elif dist == 3:
                        st.markdown(f"### 🧓 {t('pedigree.great_grandparents', lang)}")
                        icon = "🧓"
                    else:
                        st.markdown(f"### 🧬 {t('pedigree.generation', lang)} -{dist}")
                        icon = "🧬"

                    # Display in columns
                    cols = st.columns(min(len(by_distance[dist]), 4))
                    for idx, ancestor in enumerate(by_distance[dist]):
                        with cols[idx % len(cols)]:
                            st.markdown(f"""
                            <div class="ancestor-box">
                                <p style="font-size: 1.1rem; font-weight: bold; margin: 0;">{icon} {ancestor.name}</p>
                                <p style="color: #495057; margin: 0.3rem 0 0 0;">{ancestor.phenotype}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                # Inbreeding check
                st.markdown(f"### 🔍 {t('pedigree.inbreeding_analysis', lang)}")
                inbreeding = st.session_state.pedigree.detect_inbreeding(selected_id, depth)
                if inbreeding:
                    st.warning(f"⚠️ {t('pedigree.inbreeding_detected', lang, count=len(inbreeding))}")
                    with st.expander(t('pedigree.view_repeated', lang)):
                        for anc_id in inbreeding:
                            anc = st.session_state.pedigree.horses[anc_id]
                            st.caption(f"• {anc.name} ({anc.phenotype})")
                else:
                    st.success(f"✅ {t('pedigree.no_inbreeding', lang)}")

            else:
                st.info(f"🌱 {t('pedigree.foundation_horse', lang)}")

            # Visual pedigree tree
            if ancestors:
                st.markdown("---")
                st.markdown(f"### 🎨 {t('pedigree.visual_tree_title', lang)}")

                with st.spinner(f"🔮 {t('pedigree.generating_tree', lang)}"):
                    try:
                        tree_image = generate_pedigree_tree_image(
                            st.session_state.pedigree,
                            selected_id,
                            depth
                        )

                        # Display the image
                        st.image(tree_image, use_container_width=True)

                        # Download button
                        st.download_button(
                            label=t('pedigree.download_tree', lang),
                            data=tree_image,
                            file_name=f"pedigree_{selected_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating tree visualization: {str(e)}")

            # Show genotype details
            st.markdown("---")
            with st.expander(f"🧬 {t('pedigree.view_genotype', lang)}"):
                st.code(selected_horse.genotype_string, language="text")

elif page == t('nav.compare', lang):
    st.markdown(f'<p class="main-header">⚖️ {t("compare.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("compare.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('compare.how_to_use', lang)}", expanded=False):
        st.markdown(t('compare.instructions', lang))

    st.markdown("---")

    if len(st.session_state.horses) < 2:
        st.warning(f"⚠️ {t('compare.need_horses', lang)}")
    else:
        horse_names = [f"{item['name']} - {item['horse'].phenotype}"
                       for item in st.session_state.horses]

        # Horse selection
        col1, col2 = st.columns(2)

        with col1:
            horse1_idx = st.selectbox(
                f"🐴 {t('compare.select_horse1', lang)}",
                range(len(horse_names)),
                format_func=lambda x: horse_names[x],
                key="compare_horse1"
            )
            horse1_item = st.session_state.horses[horse1_idx]
            horse1 = horse1_item['horse']

        with col2:
            horse2_idx = st.selectbox(
                f"🐴 {t('compare.select_horse2', lang)}",
                range(len(horse_names)),
                format_func=lambda x: horse_names[x],
                key="compare_horse2"
            )
            horse2_item = st.session_state.horses[horse2_idx]
            horse2 = horse2_item['horse']

        st.markdown("---")

        # Display horses side-by-side
        col_h1, col_h2 = st.columns(2)

        with col_h1:
            st.markdown(f"### {t('compare.horse1_details', lang)}")
            gradient1, text_color1 = get_phenotype_color(horse1.phenotype)
            st.markdown(f"""
            <div class="horse-card" style="background: {gradient1}; color: {text_color1};">
                <h2>🐴 {horse1_item['name']}</h2>
                <p style="font-size: 1.3rem; margin: 0.5rem 0;">{horse1.phenotype}</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🧬 {t('compare.full_genotype', lang)}"):
                st.code(horse1.genotype_string, language="text")

        with col_h2:
            st.markdown(f"### {t('compare.horse2_details', lang)}")
            gradient2, text_color2 = get_phenotype_color(horse2.phenotype)
            st.markdown(f"""
            <div class="horse-card" style="background: {gradient2}; color: {text_color2};">
                <h2>🐴 {horse2_item['name']}</h2>
                <p style="font-size: 1.3rem; margin: 0.5rem 0;">{horse2.phenotype}</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🧬 {t('compare.full_genotype', lang)}"):
                st.code(horse2.genotype_string, language="text")

        st.markdown("---")

        # Gene-by-gene comparison
        st.markdown(f"### 🔬 {t('compare.gene_comparison', lang)}")

        # Calculate similarity
        genes1 = horse1.genotype
        genes2 = horse2.genotype

        matching_genes = []
        different_genes = []

        for gene_name in genes1.keys():
            alleles1 = set(genes1[gene_name])
            alleles2 = set(genes2[gene_name])

            if alleles1 == alleles2:
                matching_genes.append(gene_name)
            else:
                different_genes.append(gene_name)

        # Similarity score
        total_genes = len(genes1)
        matching_count = len(matching_genes)
        similarity_percent = int((matching_count / total_genes) * 100)

        col_sim1, col_sim2, col_sim3 = st.columns(3)

        with col_sim1:
            st.metric(f"✅ {t('compare.matching', lang)}", f"{matching_count}/{total_genes}")

        with col_sim2:
            st.metric(f"🔬 {t('compare.compatibility_score', lang)}", f"{similarity_percent}%")

        with col_sim3:
            st.metric(f"❌ {t('compare.different', lang)}", f"{len(different_genes)}/{total_genes}")

        # Show compatibility message
        if similarity_percent == 100:
            st.success(f"🎉 {t('compare.identical_genotype', lang)}")
        elif similarity_percent >= 70:
            st.info(f"📊 {t('compare.compatibility_high', lang, percent=similarity_percent)}")
        elif similarity_percent >= 40:
            st.info(f"📊 {t('compare.compatibility_medium', lang, percent=similarity_percent)}")
        else:
            st.info(f"📊 {t('compare.compatibility_low', lang, percent=similarity_percent)}")

        st.markdown("---")

        # Detailed gene comparison table
        st.markdown(f"### 📋 {t('compare.gene_comparison', lang)}")

        for gene_name in genes1.keys():
            alleles1_str = "/".join(genes1[gene_name])
            alleles2_str = "/".join(genes2[gene_name])

            is_match = gene_name in matching_genes

            col_gene, col_a1, col_a2, col_status = st.columns([2, 2, 2, 1])

            with col_gene:
                st.markdown(f"**{gene_name}**")

            with col_a1:
                if is_match:
                    st.success(alleles1_str)
                else:
                    st.warning(alleles1_str)

            with col_a2:
                if is_match:
                    st.success(alleles2_str)
                else:
                    st.warning(alleles2_str)

            with col_status:
                if is_match:
                    st.markdown("✅")
                else:
                    st.markdown("❌")

elif page == t('nav.statistics', lang):
    st.markdown(f'<p class="main-header">📈 {t("statistics.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("statistics.subtitle", lang)}</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander(f"ℹ️ {t('statistics.how_to_use', lang)}", expanded=False):
        st.markdown(t('statistics.instructions', lang))

    st.markdown("---")

    if len(st.session_state.horses) == 0:
        st.warning(f"⚠️ {t('statistics.need_horses', lang)}")
    else:
        # Overview statistics
        st.markdown(f"### 📊 {t('statistics.overview_title', lang)}")

        total_horses = len(st.session_state.horses)
        bred_horses = sum(1 for h in st.session_state.horses if 'parents' in h)
        foundation_horses = total_horses - bred_horses

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(f"🐴 {t('statistics.total_horses', lang)}", total_horses)

        with col2:
            st.metric(f"✨ {t('statistics.foundation_count', lang)}", foundation_horses)

        with col3:
            st.metric(f"🧬 {t('statistics.bred_count', lang)}", bred_horses)

        with col4:
            phenotypes = set(item['horse'].phenotype for item in st.session_state.horses)
            st.metric(f"🎨 {t('statistics.unique_phenotypes', lang)}", len(phenotypes))

        st.markdown("---")

        # Phenotype distribution
        st.markdown(f"### 🎨 {t('statistics.phenotype_title', lang)}")

        phenotype_counts = {}
        for item in st.session_state.horses:
            pheno = item['horse'].phenotype
            phenotype_counts[pheno] = phenotype_counts.get(pheno, 0) + 1

        # Sort by count (descending)
        sorted_phenotypes = sorted(phenotype_counts.items(), key=lambda x: x[1], reverse=True)

        # Display top 10
        for phenotype, count in sorted_phenotypes[:10]:
            percentage = (count / total_horses) * 100

            col_name, col_bar = st.columns([1, 3])

            with col_name:
                st.markdown(f"**{phenotype}**")

            with col_bar:
                st.progress(count / total_horses, text=f"{count} ({percentage:.1f}%)")

        st.markdown("---")

        # Gene frequency analysis
        st.markdown(f"### 🧬 {t('statistics.gene_title', lang)}")

        # Collect all alleles for each gene
        gene_alleles = {}
        all_genes = list(st.session_state.horses[0]['horse'].genotype.keys())

        for gene_name in all_genes:
            gene_alleles[gene_name] = {}

        for item in st.session_state.horses:
            for gene_name, alleles in item['horse'].genotype.items():
                for allele in alleles:
                    gene_alleles[gene_name][allele] = gene_alleles[gene_name].get(allele, 0) + 1

        # Display gene frequency for each gene
        for gene_name in all_genes:
            with st.expander(f"📊 {t('statistics.gene_diversity', lang, gene=gene_name)}"):
                allele_counts = gene_alleles[gene_name]
                total_alleles = sum(allele_counts.values())

                # Sort by frequency
                sorted_alleles = sorted(allele_counts.items(), key=lambda x: x[1], reverse=True)

                for allele, count in sorted_alleles:
                    frequency = (count / total_alleles) * 100

                    col_allele, col_freq = st.columns([1, 3])

                    with col_allele:
                        st.markdown(f"**{allele}**")

                    with col_freq:
                        st.progress(count / total_alleles, text=f"{count} ({frequency:.1f}%)")

        st.markdown("---")

        # Diversity score
        st.markdown(f"### 🌈 {t('statistics.diversity_title', lang)}")

        # Calculate diversity score based on phenotype variety
        phenotype_diversity = len(phenotypes) / total_horses
        unique_ratio = phenotype_diversity

        # Calculate genetic diversity based on allele distribution
        total_gene_diversity = 0
        for gene_name in all_genes:
            unique_alleles = len(gene_alleles[gene_name])
            total_gene_diversity += unique_alleles

        avg_gene_diversity = total_gene_diversity / len(all_genes)

        # Overall diversity score (0-100)
        diversity_score = int(((phenotype_diversity + (avg_gene_diversity / 10)) / 2) * 100)

        col_div1, col_div2 = st.columns([1, 2])

        with col_div1:
            st.metric(f"🌟 {t('statistics.diversity_score', lang)}", f"{diversity_score}%")

        with col_div2:
            if diversity_score >= 70:
                st.success(f"✅ {t('statistics.diversity_high', lang)}")
            elif diversity_score >= 40:
                st.info(f"📊 {t('statistics.diversity_medium', lang)}")
            else:
                st.warning(f"⚠️ {t('statistics.diversity_low', lang)}")

else:  # About
    st.markdown(f'<p class="main-header">📖 {t("about.title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{t("about.subtitle", lang)}</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([t('about.tab_genetics', lang), t('about.tab_colors', lang), t('about.tab_tech', lang)])

    with tab1:
        st.markdown(f"""
        ### 🔬 {t('about.genetics_title', lang)}

        {t('about.genetics_description', lang)}

        1. {t('about.genetics_1', lang)}
        2. {t('about.genetics_2', lang)}
        3. {t('about.genetics_3', lang)}
        4. {t('about.genetics_4', lang)}
        5. {t('about.genetics_5', lang)}
        6. {t('about.genetics_6', lang)}
        7. {t('about.genetics_7', lang)}
        8. {t('about.genetics_8', lang)}
        9. {t('about.genetics_9', lang)}

        ### 🧮 {t('about.mendelian', lang)}

        {t('about.mendelian_description', lang)}
        """)

    with tab2:
        st.markdown(f"""
        ### 🎨 {t('about.colors_title', lang)}

        {t('about.colors_base', lang)}

        {t('about.colors_cream', lang)}

        {t('about.colors_pearl', lang)}

        {t('about.colors_special', lang)}
        """)

    with tab3:
        col_tech1, col_tech2 = st.columns(2)

        with col_tech1:
            st.markdown(f"""
            ### 💻 {t('about.tech_stack', lang)}

            - {t('about.tech_backend', lang)}
            - {t('about.tech_web', lang)}
            - {t('about.tech_api', lang)}
            - {t('about.tech_license', lang)}
            """)

        with col_tech2:
            st.markdown(f"""
            ### 📊 {t('about.performance_title', lang)}

            - {t('about.performance_generation', lang)}
            - {t('about.performance_breeding', lang)}
            - {t('about.performance_tests', lang)}
            - {t('about.performance_memory', lang)}
            """)

    st.markdown("---")

    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.metric(t('about.total_genes', lang), "9")
    with col_metric2:
        st.metric(t('about.phenotypes', lang), "50+")
    with col_metric3:
        st.metric(t('about.tests', lang), "65/65 ✅")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6c757d;">
    <p>🐴 {t('footer.made_with', lang)}</p>
    <p><a href="https://github.com/Metroseksuaali/Horsegenetics" target="_blank">{t('footer.github', lang)}</a></p>
</div>
""", unsafe_allow_html=True)
