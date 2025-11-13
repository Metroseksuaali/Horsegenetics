#!/usr/bin/env python3
"""
Horse Genetics Simulator - Web Interface (Streamlit)

Modern web-based interface for the horse genetics simulator.
No installation required - just run and open in browser!

Run with:
    pip install streamlit
    streamlit run streamlit_app.py

Or with Docker:
    docker-compose up
    # Open http://localhost:8501
"""

import streamlit as st
from genetics.horse import Horse
from genetics.breeding_stats import calculate_offspring_probabilities, format_probability_report
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

# Initialize session state
if 'horses' not in st.session_state:
    st.session_state.horses = []
if 'pedigree' not in st.session_state:
    st.session_state.pedigree = PedigreeTree()
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar
with st.sidebar:
    st.title("🐴 Horse Genetics")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🎲 Random Generator", "🧬 Breeding", "📊 Probability Calculator",
         "📚 My Stable", "📖 About"]
    )

    st.markdown("---")
    st.caption("v2.1 - Production Ready")
    st.caption("[GitHub](https://github.com/Metroseksuaali/Horsegenetics)")

# Main content
if page == "🎲 Random Generator":
    st.title("🎲 Random Horse Generator")
    st.markdown("Generate random horses with scientifically accurate genetics!")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Generate")

        num_horses = st.slider("Number of horses", 1, 10, 1)

        if st.button("🎲 Generate Random Horse(s)", type="primary", use_container_width=True):
            with st.spinner("Generating horses..."):
                generated = []
                for i in range(num_horses):
                    horse = Horse.random()
                    generated.append(horse)
                    st.session_state.horses.append({
                        'horse': horse,
                        'name': f"Horse {len(st.session_state.horses) + 1}",
                        'generated_at': datetime.now().isoformat()
                    })

                st.success(f"✅ Generated {num_horses} horse(s)!")

                # Display generated horses
                for i, horse in enumerate(generated):
                    with st.expander(f"🐴 Horse {i+1}: **{horse.phenotype}**", expanded=True):
                        st.markdown(f"**Phenotype:** `{horse.phenotype}`")
                        st.code(horse.genotype_string, language="text")

                        # Detailed genotype
                        st.markdown("**Detailed Genotype:**")
                        for gene_name, alleles in horse.genotype.items():
                            st.text(f"  {gene_name}: {'/'.join(alleles)}")

    with col2:
        st.subheader("Recent Horses")

        if st.session_state.horses:
            # Show last 5 horses
            recent = st.session_state.horses[-5:][::-1]

            for idx, item in enumerate(recent):
                horse = item['horse']
                name = item['name']

                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{name}**")
                        st.markdown(f"🎨 *{horse.phenotype}*")
                    with col_b:
                        if st.button("📋", key=f"copy_{idx}"):
                            st.code(horse.genotype_string)

                    st.markdown("---")
        else:
            st.info("No horses generated yet. Generate some horses to get started!")

elif page == "🧬 Breeding":
    st.title("🧬 Breeding Simulator")
    st.markdown("Breed two horses and see the offspring!")

    if len(st.session_state.horses) < 2:
        st.warning("⚠️ You need at least 2 horses to breed. Generate some horses first!")
    else:
        col1, col2 = st.columns(2)

        horse_names = [f"{item['name']} ({item['horse'].phenotype})"
                       for item in st.session_state.horses]

        with col1:
            st.subheader("👨 Parent 1 (Sire)")
            parent1_idx = st.selectbox("Select sire", range(len(horse_names)),
                                       format_func=lambda x: horse_names[x], key="p1")
            parent1 = st.session_state.horses[parent1_idx]['horse']

            with st.expander("Show genotype"):
                st.code(parent1.genotype_string)

        with col2:
            st.subheader("👩 Parent 2 (Dam)")
            parent2_idx = st.selectbox("Select dam", range(len(horse_names)),
                                       format_func=lambda x: horse_names[x], key="p2")
            parent2 = st.session_state.horses[parent2_idx]['horse']

            with st.expander("Show genotype"):
                st.code(parent2.genotype_string)

        st.markdown("---")

        col_breed1, col_breed2, col_breed3 = st.columns([1, 1, 1])

        with col_breed2:
            if st.button("🐴 Breed Horses", type="primary", use_container_width=True):
                with st.spinner("Breeding..."):
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

                    st.success("🎉 Breeding successful!")

                    # Display offspring
                    st.markdown("### 🐴 Offspring")

                    col_result1, col_result2 = st.columns([1, 1])

                    with col_result1:
                        st.metric("Phenotype", offspring.phenotype)

                    with col_result2:
                        st.metric("Generation", "1")

                    st.code(offspring.genotype_string)

                    with st.expander("Detailed Genotype"):
                        for gene_name, alleles in offspring.genotype.items():
                            st.text(f"{gene_name}: {'/'.join(alleles)}")

elif page == "📊 Probability Calculator":
    st.title("📊 Breeding Probability Calculator")
    st.markdown("Calculate the chances of different offspring before breeding!")

    method = st.radio("Input method", ["Select from stable", "Enter genotype manually"])

    if method == "Select from stable":
        if len(st.session_state.horses) < 2:
            st.warning("⚠️ You need at least 2 horses. Generate some horses first!")
        else:
            horse_names = [f"{item['name']} ({item['horse'].phenotype})"
                          for item in st.session_state.horses]

            col1, col2 = st.columns(2)

            with col1:
                parent1_idx = st.selectbox("Parent 1", range(len(horse_names)),
                                          format_func=lambda x: horse_names[x])
                parent1 = st.session_state.horses[parent1_idx]['horse']

            with col2:
                parent2_idx = st.selectbox("Parent 2", range(len(horse_names)),
                                          format_func=lambda x: horse_names[x])
                parent2 = st.session_state.horses[parent2_idx]['horse']

            if st.button("Calculate Probabilities", type="primary"):
                with st.spinner("Calculating probabilities..."):
                    probs = calculate_offspring_probabilities(
                        parent1.genotype_string,
                        parent2.genotype_string
                    )

                    st.success("✅ Calculation complete!")

                    # Display as chart
                    st.subheader("Probability Distribution")

                    # Create bar chart data
                    phenotypes = list(probs.keys())[:10]  # Top 10
                    percentages = [probs[p] * 100 for p in phenotypes]

                    import pandas as pd
                    df = pd.DataFrame({
                        'Phenotype': phenotypes,
                        'Probability (%)': percentages
                    })

                    st.bar_chart(df.set_index('Phenotype'))

                    # Display table
                    st.subheader("Detailed Probabilities")
                    st.dataframe(df, use_container_width=True)

    else:  # Manual entry
        col1, col2 = st.columns(2)

        with col1:
            parent1_str = st.text_input("Parent 1 genotype",
                                       value="E:E/e A:A/a Dil:N/Cr D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g")

        with col2:
            parent2_str = st.text_input("Parent 2 genotype",
                                       value="E:e/e A:A/a Dil:N/N D:nd2/nd2 Z:n/n Ch:n/n F:F/f STY:sty/sty G:g/g")

        if st.button("Calculate Probabilities", type="primary"):
            try:
                with st.spinner("Calculating probabilities..."):
                    probs = calculate_offspring_probabilities(parent1_str, parent2_str)

                    st.success("✅ Calculation complete!")

                    # Display results
                    st.subheader("Top 10 Most Likely Outcomes")

                    for phenotype, prob in list(probs.items())[:10]:
                        col_name, col_prob = st.columns([3, 1])
                        with col_name:
                            st.markdown(f"**{phenotype}**")
                        with col_prob:
                            st.progress(prob, text=f"{prob*100:.1f}%")

            except ValueError as e:
                st.error(f"❌ Invalid genotype: {e}")

elif page == "📚 My Stable":
    st.title("📚 My Stable")
    st.markdown(f"You have **{len(st.session_state.horses)}** horse(s) in your stable")

    if st.session_state.horses:
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("💾 Save Stable", use_container_width=True):
                # Save to JSON
                horses_data = [item['horse'].to_dict() for item in st.session_state.horses]
                json_str = json.dumps(horses_data, indent=2)
                st.download_button(
                    "⬇️ Download JSON",
                    json_str,
                    file_name=f"stable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col2:
            uploaded_file = st.file_uploader("📂 Load Stable", type=['json'])
            if uploaded_file is not None:
                try:
                    horses_data = json.load(uploaded_file)
                    # Reconstruct horses
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

        with col3:
            if st.button("🗑️ Clear Stable", use_container_width=True):
                st.session_state.horses = []
                st.session_state.pedigree = PedigreeTree()
                st.rerun()

        st.markdown("---")

        # Display all horses
        for idx, item in enumerate(st.session_state.horses):
            horse = item['horse']
            name = item['name']

            with st.expander(f"🐴 {name} - {horse.phenotype}"):
                col_info1, col_info2 = st.columns([2, 1])

                with col_info1:
                    st.markdown(f"**Phenotype:** {horse.phenotype}")
                    st.code(horse.genotype_string, language="text")

                with col_info2:
                    if 'parents' in item:
                        p1_name = st.session_state.horses[item['parents'][0]]['name']
                        p2_name = st.session_state.horses[item['parents'][1]]['name']
                        st.markdown(f"**Parents:**")
                        st.markdown(f"- Sire: {p1_name}")
                        st.markdown(f"- Dam: {p2_name}")

                # Allow renaming
                new_name = st.text_input("Rename", value=name, key=f"rename_{idx}")
                if new_name != name:
                    st.session_state.horses[idx]['name'] = new_name
                    st.rerun()

    else:
        st.info("Your stable is empty. Generate some horses to get started!")

else:  # About
    st.title("📖 About Horse Genetics Simulator")

    st.markdown("""
    ## 🐴 Welcome!

    This is a scientifically accurate horse coat color genetics simulator based on
    peer-reviewed equine genetics research.

    ### 🧬 Genetics Modeled

    The simulator includes **9 genetic traits**:

    1. **Extension (E/e)** - Black vs. red pigment production
    2. **Agouti (A/a)** - Distribution of black pigment (bay vs. black)
    3. **Dilution (N/Cr/Prl)** - Cream and Pearl dilutions
    4. **Dun (D/nd1/nd2)** - Dun dilution with primitive markings
    5. **Silver (Z/n)** - Lightens black pigment, especially mane/tail
    6. **Champagne (Ch/n)** - Dilutes both red and black pigment
    7. **Flaxen (F/f)** - Lightens mane/tail on chestnuts only
    8. **Sooty (STY/sty)** - Adds darker hairs to the coat
    9. **Gray (G/g)** - Progressive graying with age

    ### 🎨 Colors Produced

    Over **50 different phenotypes** including:
    - Base colors: Bay, Black, Chestnut
    - Cream dilutes: Palomino, Buckskin, Cremello, Perlino, Smoky Cream
    - Pearl colors: Apricot, Pearl Bay, Smoky Pearl
    - Special: Silver Dapple, Champagne variants, Gray, and many combinations!

    ### 🔬 How It Works

    The simulator uses **Mendelian inheritance** - each parent contributes one random
    allele from each gene to the offspring. Complex gene interactions are modeled
    accurately based on scientific literature.

    ### 📊 Features

    - ✅ Random horse generation
    - ✅ Realistic breeding simulation
    - ✅ Probability calculator
    - ✅ Pedigree tracking
    - ✅ Save/load your stable
    - ✅ 65 unit tests ensuring accuracy
    - ✅ Performance optimized (>50k horses/sec)

    ### 💻 Technology

    - **Backend**: Python with modular architecture
    - **Web UI**: Streamlit
    - **API**: FastAPI REST API available
    - **License**: MIT (Open Source)

    ### 🚀 For Developers

    This simulator is perfect for:
    - Game developers needing horse breeding mechanics
    - Educational tools for genetics
    - Research and analysis

    Check out the [GitHub repository](https://github.com/Metroseksuaali/Horsegenetics)
    for API documentation and more!

    ### ❤️ Credits

    Made with love for horse enthusiasts and game developers.

    **Version 2.1** - Production Ready
    """)

    st.markdown("---")

    col_about1, col_about2, col_about3 = st.columns(3)

    with col_about1:
        st.metric("Total Genes", "9")
    with col_about2:
        st.metric("Phenotypes", "50+")
    with col_about3:
        st.metric("Tests Passing", "65/65")

# Footer
st.markdown("---")
st.caption("🐴 Horse Genetics Simulator v2.1 | Made with ❤️ by Metroseksuaali")
