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

import streamlit as st
from genetics.horse import Horse
from genetics.breeding_stats import calculate_offspring_probabilities
from genetics.gene_registry import get_default_registry
from genetics.gene_interaction import PhenotypeCalculator
from genetics.pedigree import PedigreeTree
from genetics.io import save_horses_to_json, load_horses_from_json
import json
from datetime import datetime

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

# Sidebar
with st.sidebar:
    st.markdown("# 🐴 Horse Genetics")
    st.markdown("### Simulator v2.1")
    st.markdown("---")

    page = st.radio(
        "**📍 Navigation**",
        ["🎲 Generator", "🧬 Breeding", "📊 Probability",
         "📚 My Stable", "🌳 Pedigree", "📖 About"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Quick stats
    if st.session_state.horses:
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Horses", len(st.session_state.horses))
        st.metric("In Pedigree", len(st.session_state.pedigree.horses))

    st.markdown("---")
    st.caption("🔬 Scientifically Accurate")
    st.caption("⚡ 50k+ horses/sec")
    st.caption("[💻 GitHub](https://github.com/Metroseksuaali/Horsegenetics)")

# Main content
if page == "🎲 Generator":
    st.markdown('<p class="main-header">🎲 Random Horse Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Generate horses with scientifically accurate genetics</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        **Instructions:**
        1. Choose how many horses you want to generate (1-10)
        2. Click **Generate Horses** button
        3. View your new horses below
        4. All generated horses are automatically saved to **My Stable**

        **Tip:** Generate multiple horses at once to quickly build your breeding stock!
        """)

    st.markdown("---")

    # Controls in a nice box
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            num_horses = st.slider("🔢 How many horses?", 1, 10, 1, help="Generate up to 10 horses at once")

        with col2:
            if st.button("✨ Generate Horses", type="primary", use_container_width=True):
                with st.spinner("🔮 Creating horses..."):
                    generated = []
                    for i in range(num_horses):
                        horse = Horse.random()
                        generated.append(horse)
                        st.session_state.horses.append({
                            'horse': horse,
                            'name': f"Horse {len(st.session_state.horses) + 1}",
                            'generated_at': datetime.now().isoformat()
                        })

                    st.success(f"🎉 Successfully generated {num_horses} horse(s)!")

                    # Display generated horses in a nice grid
                    st.markdown("### 🐴 Your New Horses")

                    for i, horse in enumerate(generated):
                        with st.expander(f"✨ {horse.phenotype}", expanded=True):
                            col_a, col_b = st.columns([2, 1])

                            with col_a:
                                st.markdown(f"**🎨 Color:** {horse.phenotype}")
                                st.code(horse.genotype_string, language="text")

                            with col_b:
                                st.markdown("**📊 Genetics**")
                                for gene_name, alleles in list(horse.genotype.items())[:3]:
                                    st.caption(f"{gene_name}: {'/'.join(alleles)}")

        with col3:
            st.info("💡 Tip: Generate multiple horses to build your stable!")

    st.markdown("---")

    # Show recent horses in a beautiful grid
    if st.session_state.horses:
        st.markdown("### 📋 Recent Horses")
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
        st.info("👋 Welcome! Generate your first horse to get started.")

elif page == "🧬 Breeding":
    st.markdown('<p class="main-header">🧬 Breeding Simulator</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Breed two horses and discover their offspring</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        **Instructions:**
        1. Select a **Sire** (father) from the left dropdown
        2. Select a **Dam** (mother) from the right dropdown
        3. Click **Breed Horses** to create offspring
        4. The foal will be added to **My Stable** and **Pedigree Tree**

        **Genetics:** Each parent contributes one random allele from each gene to the offspring.
        Results follow real Mendelian inheritance patterns!
        """)

    st.markdown("---")

    if len(st.session_state.horses) < 2:
        st.warning("⚠️ You need at least 2 horses to breed. Visit the **Generator** page first!")
        if st.button("🎲 Go to Generator"):
            st.rerun()
    else:
        horse_names = [f"{item['name']} - {item['horse'].phenotype}"
                       for item in st.session_state.horses]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👨 Sire (Father)")
            parent1_idx = st.selectbox("Choose sire", range(len(horse_names)),
                                       format_func=lambda x: horse_names[x], key="p1",
                                       label_visibility="collapsed")
            parent1 = st.session_state.horses[parent1_idx]['horse']

            with st.expander("🔬 View Genotype"):
                st.code(parent1.genotype_string, language="text")

        with col2:
            st.markdown("### 👩 Dam (Mother)")
            parent2_idx = st.selectbox("Choose dam", range(len(horse_names)),
                                       format_func=lambda x: horse_names[x], key="p2",
                                       label_visibility="collapsed")
            parent2 = st.session_state.horses[parent2_idx]['horse']

            with st.expander("🔬 View Genotype"):
                st.code(parent2.genotype_string, language="text")

        st.markdown("<br>", unsafe_allow_html=True)

        # Center the breed button
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("💫 Breed Horses", type="primary", use_container_width=True):
                with st.spinner("🔬 Breeding in progress..."):
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

                    st.success("🎊 Congratulations! A new foal has been born!")

                    # Display offspring beautifully
                    st.markdown("### 🐴 Meet Your New Foal!")

                    col_res1, col_res2, col_res3 = st.columns(3)

                    with col_res1:
                        st.markdown("**👨 Sire**")
                        st.info(parent1.phenotype)

                    with col_res2:
                        st.markdown("**🐴 Offspring**")
                        st.success(f"**{offspring.phenotype}**")

                    with col_res3:
                        st.markdown("**👩 Dam**")
                        st.info(parent2.phenotype)

                    st.markdown("<br>", unsafe_allow_html=True)

                    with st.expander("🧬 Offspring Genotype", expanded=True):
                        st.code(offspring.genotype_string, language="text")

elif page == "📊 Probability":
    st.markdown('<p class="main-header">📊 Probability Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Calculate breeding outcome chances before you breed</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        **Instructions:**
        1. Select two horses from the dropdowns
        2. Click **Calculate Probabilities**
        3. View the probability distribution of all possible offspring colors

        **What does this show?** This calculates ALL possible genetic combinations from breeding
        these two horses and shows you the exact probability of each color outcome.

        **Tip:** Use this before breeding to see what colors are possible!
        """)

    st.markdown("---")

    if len(st.session_state.horses) < 2:
        st.warning("⚠️ You need at least 2 horses. Visit the **Generator** page first!")
    else:
        horse_names = [f"{item['name']} - {item['horse'].phenotype}"
                       for item in st.session_state.horses]

        col1, col2 = st.columns(2)

        with col1:
            parent1_idx = st.selectbox("👨 Select Parent 1", range(len(horse_names)),
                                      format_func=lambda x: horse_names[x])
            parent1 = st.session_state.horses[parent1_idx]['horse']

        with col2:
            parent2_idx = st.selectbox("👩 Select Parent 2", range(len(horse_names)),
                                      format_func=lambda x: horse_names[x])
            parent2 = st.session_state.horses[parent2_idx]['horse']

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🎯 Calculate Probabilities", type="primary", use_container_width=True):
            with st.spinner("🧮 Calculating all possible outcomes..."):
                probs = calculate_offspring_probabilities(
                    parent1.genotype_string,
                    parent2.genotype_string
                )

                st.success("✅ Calculation complete!")

                st.markdown("### 📈 Probability Distribution")

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
                with st.expander("📋 View All Outcomes"):
                    import pandas as pd
                    df = pd.DataFrame({
                        'Phenotype': list(probs.keys()),
                        'Probability': [f"{v*100:.2f}%" for v in probs.values()]
                    })
                    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "📚 My Stable":
    st.markdown('<p class="main-header">📚 My Stable</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Manage your horse collection</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        **Instructions:**
        - **Save Stable:** Download all horses as a JSON file
        - **Load Stable:** Upload a previously saved JSON file
        - **Clear Stable:** Remove all horses (cannot be undone!)
        - **Rename Horses:** Click on any horse and edit its name at the bottom

        **Tip:** Regularly save your stable to keep backups of your breeding work!
        """)

    st.markdown("---")

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🐴 Total Horses", len(st.session_state.horses))
    with col2:
        bred = sum(1 for h in st.session_state.horses if 'parents' in h)
        st.metric("🧬 Bred Horses", bred)
    with col3:
        foundation = len(st.session_state.horses) - bred
        st.metric("✨ Foundation", foundation)
    with col4:
        st.metric("🌳 In Pedigree", len(st.session_state.pedigree.horses))

    st.markdown("---")

    # Action buttons
    col_act1, col_act2, col_act3 = st.columns(3)

    with col_act1:
        if st.session_state.horses:
            horses_data = [item['horse'].to_dict() for item in st.session_state.horses]
            json_str = json.dumps(horses_data, indent=2)
            st.download_button(
                "💾 Save Stable (JSON)",
                json_str,
                file_name=f"stable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    with col_act2:
        uploaded_file = st.file_uploader("📂 Load Stable", type=['json'], label_visibility="collapsed")
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

                st.success(f"✅ Loaded {len(horses_data)} horses!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")

    with col_act3:
        if st.button("🗑️ Clear Stable", use_container_width=True):
            st.session_state.horses = []
            st.session_state.pedigree = PedigreeTree()
            st.rerun()

    st.markdown("---")

    # Display horses in grid
    if st.session_state.horses:
        st.markdown("### 🐴 All Horses")

        for idx, item in enumerate(st.session_state.horses):
            horse = item['horse']
            name = item['name']

            with st.expander(f"🐴 {name} - {horse.phenotype}"):
                col_info1, col_info2 = st.columns([2, 1])

                with col_info1:
                    st.markdown(f"**🎨 Phenotype:** {horse.phenotype}")
                    st.code(horse.genotype_string, language="text")

                with col_info2:
                    if 'parents' in item:
                        p1_name = st.session_state.horses[item['parents'][0]]['name']
                        p2_name = st.session_state.horses[item['parents'][1]]['name']
                        st.markdown("**👪 Parents:**")
                        st.caption(f"👨 {p1_name}")
                        st.caption(f"👩 {p2_name}")
                    else:
                        st.info("✨ Foundation Horse")

                # Rename option
                new_name = st.text_input("✏️ Rename", value=name, key=f"rename_{idx}")
                if new_name != name:
                    st.session_state.horses[idx]['name'] = new_name
                    st.rerun()
    else:
        st.info("👋 Your stable is empty. Visit the **Generator** to create horses!")

elif page == "🌳 Pedigree":
    st.markdown('<p class="main-header">🌳 Pedigree Tree</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explore family relationships and breeding history</p>', unsafe_allow_html=True)

    # Help/Instructions
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        **Instructions:**
        1. Select a horse from the dropdown menu
        2. Choose how many generations back to display (1-5)
        3. View the visual family tree showing all ancestors

        **What you'll see:**
        - **Parents** (1 generation back)
        - **Grandparents** (2 generations back)
        - **Great-Grandparents** (3 generations back)
        - **Inbreeding warnings** if the same ancestor appears multiple times

        **Note:** Only horses bred using the Breeding page appear in the pedigree tree.
        Foundation horses (randomly generated) have no ancestors.
        """)

    st.markdown("---")

    if len(st.session_state.pedigree.horses) == 0:
        st.warning("⚠️ No pedigree data yet. Breed some horses first using the **Breeding** page!")
        st.info("""
        💡 **How to build a pedigree:**
        1. Go to **Generator** and create some foundation horses
        2. Go to **Breeding** and breed two horses together
        3. The offspring will appear here with full pedigree information
        """)
    else:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🐴 Total", len(st.session_state.pedigree.horses))
        with col2:
            st.metric("🧬 Breedings", len(st.session_state.pedigree.breedings))
        with col3:
            max_gen = max(h.generation for h in st.session_state.pedigree.horses.values())
            st.metric("📊 Generations", max_gen + 1)
        with col4:
            foundation = sum(1 for h in st.session_state.pedigree.horses.values()
                           if h.sire_id is None and h.dam_id is None)
            st.metric("✨ Foundation", foundation)

        st.markdown("---")

        # Simplified pedigree view
        st.markdown("### 🐴 Select a Horse")

        horse_options = {h.name: h.horse_id for h in st.session_state.pedigree.horses.values()}
        horse_list = list(horse_options.keys())

        col_select, col_depth = st.columns([3, 1])

        with col_select:
            selected_name = st.selectbox("Choose a horse to view its pedigree", horse_list, label_visibility="collapsed")

        with col_depth:
            depth = st.selectbox("Generations", [1, 2, 3, 4, 5], index=2)

        if selected_name:
            selected_id = horse_options[selected_name]
            selected_horse = st.session_state.pedigree.horses[selected_id]

            st.markdown("---")

            # Display selected horse
            st.markdown(f"""
            <div class="pedigree-box">
                <h2>🐴 {selected_name}</h2>
                <p style="font-size: 1.3rem; margin: 0.5rem 0;">🎨 {selected_horse.phenotype}</p>
                <p style="color: #6c757d; margin: 0;">📊 Generation {selected_horse.generation}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Get ancestors
            ancestors = st.session_state.pedigree.get_ancestors(selected_id, depth)

            if ancestors:
                st.markdown(f"### 🌳 Family Tree ({len(ancestors)} ancestor(s))")

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
                        st.markdown("### 👥 Parents")
                        icon = "👤"
                    elif dist == 2:
                        st.markdown("### 👴👵 Grandparents")
                        icon = "👴"
                    elif dist == 3:
                        st.markdown("### 🧓 Great-Grandparents")
                        icon = "🧓"
                    else:
                        st.markdown(f"### 🧬 Generation -{dist}")
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
                st.markdown("### 🔍 Inbreeding Analysis")
                inbreeding = st.session_state.pedigree.detect_inbreeding(selected_id, depth)
                if inbreeding:
                    st.warning(f"⚠️ **Inbreeding detected!** {len(inbreeding)} ancestor(s) appear multiple times in the pedigree.")
                    with st.expander("View repeated ancestors"):
                        for anc_id in inbreeding:
                            anc = st.session_state.pedigree.horses[anc_id]
                            st.caption(f"• {anc.name} ({anc.phenotype})")
                else:
                    st.success("✅ **No inbreeding detected** - This is a diverse pedigree!")

            else:
                st.info("🌱 **Foundation Horse** - This horse was randomly generated and has no ancestors in the pedigree.")

            # Show genotype details
            st.markdown("---")
            with st.expander("🧬 View Full Genotype"):
                st.code(selected_horse.genotype_string, language="text")

else:  # About
    st.markdown('<p class="main-header">📖 About</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Horse Genetics Simulator v2.1</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🧬 Genetics", "🎨 Colors", "💻 Tech"])

    with tab1:
        st.markdown("""
        ### 🔬 Scientifically Accurate Simulation

        This simulator models **9 genetic traits** based on peer-reviewed equine genetics research:

        1. **Extension (E/e)** - Black vs. red pigment production
        2. **Agouti (A/a)** - Distribution of black pigment
        3. **Dilution (N/Cr/Prl)** - Cream and Pearl dilutions
        4. **Dun (D/nd1/nd2)** - Dun dilution with primitive markings
        5. **Silver (Z/n)** - Lightens black pigment
        6. **Champagne (Ch/n)** - Dilutes both red and black pigment
        7. **Flaxen (F/f)** - Lightens mane/tail on chestnuts only
        8. **Sooty (STY/sty)** - Adds darker hairs
        9. **Gray (G/g)** - Progressive graying with age

        ### 🧮 Mendelian Inheritance

        Each parent contributes one random allele from each gene to the offspring.
        Complex gene interactions are modeled accurately based on scientific literature.
        """)

    with tab2:
        st.markdown("""
        ### 🎨 Over 50 Different Phenotypes

        **Base Colors:**
        - Bay, Black, Chestnut

        **Cream Dilutes:**
        - Palomino, Buckskin, Smoky Black
        - Cremello, Perlino, Smoky Cream

        **Pearl Colors:**
        - Apricot, Pearl Bay, Smoky Pearl

        **Special Combinations:**
        - Silver Dapple, Champagne variants
        - Dun colors, Flaxen variations
        - Gray and many more!
        """)

    with tab3:
        col_tech1, col_tech2 = st.columns(2)

        with col_tech1:
            st.markdown("""
            ### 💻 Technology Stack

            - **Backend:** Python
            - **Web UI:** Streamlit
            - **API:** FastAPI
            - **License:** MIT
            """)

        with col_tech2:
            st.markdown("""
            ### 📊 Performance

            - **Generation:** >50,000 ops/sec
            - **Breeding:** >40,000 ops/sec
            - **Tests:** 65/65 passing
            - **Memory:** ~184 bytes/horse
            """)

    st.markdown("---")

    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.metric("Total Genes", "9")
    with col_metric2:
        st.metric("Phenotypes", "50+")
    with col_metric3:
        st.metric("Tests", "65/65 ✅")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d;">
    <p>🐴 Horse Genetics Simulator v2.1 | Made with ❤️</p>
    <p><a href="https://github.com/Metroseksuaali/Horsegenetics" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
