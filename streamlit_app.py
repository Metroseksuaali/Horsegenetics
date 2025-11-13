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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
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
         t('nav.stable', lang), t('nav.pedigree', lang), t('nav.about', lang)],
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
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            num_horses = st.slider(f"🔢 {t('generator.how_many', lang)}", 1, 10, 1)

        with col2:
            if st.button(t('generator.generate_button', lang), type="primary", use_container_width=True):
                with st.spinner(f"🔮 {t('generator.generating', lang)}"):
                    generated = []
                    for i in range(num_horses):
                        horse = Horse.random()
                        generated.append(horse)
                        st.session_state.horses.append({
                            'horse': horse,
                            'name': f"Horse {len(st.session_state.horses) + 1}",
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

        with col3:
            st.info(f"💡 {t('generator.tip', lang)}")

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

                st.markdown(f"""
                <div class="horse-card">
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

        # Center the breed button
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(t('breeding.breed_button', lang), type="primary", use_container_width=True):
                with st.spinner(f"🔬 {t('breeding.breeding', lang)}"):
                    offspring = Horse.breed(parent1, parent2)

                    st.session_state.horses.append({
                        'horse': offspring,
                        'name': f"Foal {len(st.session_state.horses) + 1}",
                        'generated_at': datetime.now().isoformat(),
                        'parents': (parent1_idx, parent2_idx)
                    })

                    # Add to pedigree
                    st.session_state.pedigree.add_breeding(
                        parent1, parent2, offspring,
                        sire_name=st.session_state.horses[parent1_idx]['name'],
                        dam_name=st.session_state.horses[parent2_idx]['name'],
                        foal_name=f"Foal {len(st.session_state.horses)}"
                    )

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

    # Action buttons
    col_act1, col_act2, col_act3 = st.columns(3)

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
        uploaded_file = st.file_uploader(t('stable.load_button', lang), type=['json'], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                horses_data = json.load(uploaded_file)
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

    with col_act3:
        if st.button(t('stable.clear_button', lang), use_container_width=True):
            st.session_state.horses = []
            st.session_state.pedigree = PedigreeTree()
            st.rerun()

    st.markdown("---")

    # Display horses in grid
    if st.session_state.horses:
        st.markdown(f"### 🐴 {t('stable.all_horses', lang)}")

        for idx, item in enumerate(st.session_state.horses):
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
                new_name = st.text_input(f"✏️ {t('stable.rename', lang)}", value=name, key=f"rename_{idx}")
                if new_name != name:
                    st.session_state.horses[idx]['name'] = new_name
                    st.rerun()
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

            # Show genotype details
            st.markdown("---")
            with st.expander(f"🧬 {t('pedigree.view_genotype', lang)}"):
                st.code(selected_horse.genotype_string, language="text")

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
