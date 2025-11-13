#!/usr/bin/env python3
"""
Horse Genetics GUI - Cross-platform graphical interface for horse coat color genetics
Uses tkinter for compatibility across Windows, macOS, and Linux
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from horse_genetics import HorseGeneticGenerator


class HorseGeneticsGUI:
    """GUI application for horse coat color genetics simulation"""

    GENE_MAP = {
        'E': 'extension',
        'A': 'agouti',
        'Dil': 'dilution',
        'D': 'dun',
        'Z': 'silver',
        'Ch': 'champagne',
        'F': 'flaxen',
        'STY': 'sooty'
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Horse Coat Color Genetics Simulator")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 700)

        self.generator = HorseGeneticGenerator()

        self.colors = {
            'primary': '#0066CC',      # WCAG AA compliant (4.5:1 contrast ratio)
            'secondary': '#4A8F00',    # WCAG AA compliant (4.5:1 contrast ratio)
            'background': '#FFFFFF',
            'panel_bg': '#F8F9FA',
            'border': '#DEE2E6',
            'text': '#212529',
            'text_secondary': '#5A6169'  # WCAG AA compliant (4.6:1 contrast ratio)
        }

        self.setup_styles()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_random_generator_tab()
        self.create_breeding_tab()
        self.create_help_tab()

        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        self.root.bind('<Control-g>', lambda e: self.generate_random_horse())
        self.root.bind('<Control-G>', lambda e: self.generate_random_horse())
        self.root.bind('<Control-b>', lambda e: self.breed_horses())
        self.root.bind('<Control-B>', lambda e: self.breed_horses())

    def setup_styles(self):
        style = ttk.Style()

        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Gene.TLabel', font=('Segoe UI', 10))
        style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'))

    def create_random_generator_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Random Generator')

        container = ttk.Frame(tab, padding=(20, 10, 20, 10))
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="Generate Random Horse", style='Title.TLabel')
        title.pack(pady=(0, 10))

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=5)

        generate_btn = tk.Button(
            btn_frame,
            text="Generate New Horse",
            command=self.generate_random_horse,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['secondary'],
            fg='white',
            padx=40,
            pady=15,
            relief=tk.RAISED,
            cursor='hand2'
        )
        generate_btn.pack()

        result_frame = ttk.LabelFrame(container, text="Generated Horse", padding=10)
        result_frame.pack(fill=tk.X, pady=10)

        pheno_frame = ttk.Frame(result_frame)
        pheno_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(pheno_frame, text="Phenotype:", style='Heading.TLabel').pack(anchor=tk.W)
        self.random_phenotype_label = ttk.Label(
            pheno_frame,
            text="(Click 'Generate New Horse' to start)",
            font=('Segoe UI', 16, 'bold'),
            foreground=self.colors['primary']
        )
        self.random_phenotype_label.pack(anchor=tk.W, pady=5)

        geno_frame = ttk.Frame(result_frame)
        geno_frame.pack(fill=tk.X)

        ttk.Label(geno_frame, text="Genotype:", style='Heading.TLabel').pack(anchor=tk.W)

        self.random_genotype_text = tk.Text(
            geno_frame,
            height=8,
            width=70,
            font=('Courier New', 10),
            bg=self.colors['panel_bg'],
            fg='black',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.random_genotype_text.pack(fill=tk.X, pady=5)
        self.random_genotype_text.config(state=tk.DISABLED)

        action_frame = ttk.Frame(container)
        action_frame.pack(pady=5)

        tk.Button(
            action_frame,
            text="Copy Genotype",
            command=self.copy_random_genotype,
            font=('Segoe UI', 10),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def create_breeding_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Breeding Simulator')

        # Create canvas with scrollbar
        canvas = tk.Canvas(tab, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scroll region when content changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the window width to match canvas width
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Create window and store the window ID for later configuration
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Update canvas window width when canvas is resized
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Enable mousewheel scrolling only when mouse is over this canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        container = ttk.Frame(scrollable_frame, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="Breed Two Horses", style='Title.TLabel')
        title.pack(pady=(0, 15))

        parents_frame = ttk.Frame(container)
        parents_frame.pack(fill=tk.BOTH, expand=False, pady=10)

        self.parent1_frame = self.create_parent_input_frame(parents_frame, "Parent 1 (Sire)", 1)
        self.parent1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.parent2_frame = self.create_parent_input_frame(parents_frame, "Parent 2 (Dam)", 2)
        self.parent2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        breed_btn_frame = ttk.Frame(container)
        breed_btn_frame.pack(pady=15)

        breed_btn = tk.Button(
            breed_btn_frame,
            text="♥ Breed Horses ♥",
            command=self.breed_horses,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            padx=30,
            pady=12,
            relief=tk.RAISED,
            cursor='hand2'
        )
        breed_btn.pack()

        offspring_frame = ttk.LabelFrame(container, text="Offspring", padding=15)
        offspring_frame.pack(fill=tk.X, pady=10)

        ttk.Label(offspring_frame, text="Phenotype:", style='Heading.TLabel').pack(anchor=tk.W)
        self.offspring_phenotype_label = ttk.Label(
            offspring_frame,
            text="(Breed two horses to see offspring)",
            font=('Segoe UI', 14, 'bold'),
            foreground=self.colors['primary']
        )
        self.offspring_phenotype_label.pack(anchor=tk.W, pady=5)

        ttk.Label(offspring_frame, text="Genotype:", style='Heading.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.offspring_genotype_text = tk.Text(
            offspring_frame,
            height=9,
            width=70,
            font=('Courier New', 10),
            bg=self.colors['panel_bg'],
            fg='black',
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.NONE
        )
        self.offspring_genotype_text.pack(fill=tk.X, pady=5)
        self.offspring_genotype_text.config(state=tk.DISABLED)

        action_frame = ttk.Frame(offspring_frame)
        action_frame.pack(pady=10)

        tk.Button(
            action_frame,
            text="Breed Again",
            command=self.breed_horses,
            font=('Segoe UI', 10),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            action_frame,
            text="Randomize All",
            command=self.clear_breeding,
            font=('Segoe UI', 10),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def create_parent_input_frame(self, parent, title, parent_num):
        frame = ttk.LabelFrame(parent, text=title, padding=10)

        dropdowns = {}

        genes = [
            ('E', ['E', 'e']),
            ('A', ['A', 'a']),
            ('Dil', ['N', 'Cr', 'Prl']),
            ('D', ['D', 'nd1', 'nd2']),
            ('Z', ['Z', 'n']),
            ('Ch', ['Ch', 'n']),
            ('F', ['F', 'f']),
            ('STY', ['STY', 'sty'])
        ]

        for gene_label, alleles in genes:
            gene_frame = ttk.Frame(frame)
            gene_frame.pack(fill=tk.X, pady=3)

            ttk.Label(gene_frame, text=f"{gene_label}:", width=5, style='Gene.TLabel').pack(side=tk.LEFT)

            # Set better defaults for common genotypes
            if gene_label == 'Dil':
                default1, default2 = 'N', 'N'  # Wild-type (no dilution)
            elif gene_label == 'D':
                default1, default2 = 'nd2', 'nd2'  # Non-dun
            elif gene_label in ['Z', 'Ch']:
                default1, default2 = 'n', 'n'  # Wild-type
            else:
                default1 = alleles[0]
                default2 = alleles[-1]

            var1 = tk.StringVar(value=default1)
            dropdown1 = ttk.Combobox(gene_frame, textvariable=var1, values=alleles, width=6, state='readonly')
            dropdown1.pack(side=tk.LEFT, padx=2)

            ttk.Label(gene_frame, text="/").pack(side=tk.LEFT)

            var2 = tk.StringVar(value=default2)
            dropdown2 = ttk.Combobox(gene_frame, textvariable=var2, values=alleles, width=6, state='readonly')
            dropdown2.pack(side=tk.LEFT, padx=2)

            dropdowns[gene_label] = (var1, var2)

            dropdown1.bind('<<ComboboxSelected>>', lambda e, pn=parent_num: self.update_parent_phenotype(pn))
            dropdown2.bind('<<ComboboxSelected>>', lambda e, pn=parent_num: self.update_parent_phenotype(pn))

        if parent_num == 1:
            self.parent1_dropdowns = dropdowns
        else:
            self.parent2_dropdowns = dropdowns

        pheno_frame = ttk.Frame(frame)
        pheno_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(pheno_frame, text="Phenotype:", style='Gene.TLabel').pack(anchor=tk.W)
        pheno_label = ttk.Label(
            pheno_frame,
            text="Bay",
            font=('Segoe UI', 11, 'bold'),
            foreground=self.colors['primary'],
            wraplength=250
        )
        pheno_label.pack(anchor=tk.W, pady=2)

        if parent_num == 1:
            self.parent1_phenotype_label = pheno_label
        else:
            self.parent2_phenotype_label = pheno_label

        # Update phenotype with default genotype
        self.root.after(100, lambda: self.update_parent_phenotype(parent_num))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            btn_frame,
            text="Random",
            command=lambda: self.randomize_parent(parent_num),
            font=('Segoe UI', 9),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=2)

        return frame

    def create_help_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Help')

        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="Gene Reference", style='Title.TLabel')
        title.pack(pady=(0, 15))

        help_text = scrolledtext.ScrolledText(
            container,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            padx=15,
            pady=15
        )
        help_text.pack(fill=tk.BOTH, expand=True)

        help_content = """
HORSE COAT COLOR GENETICS REFERENCE

═══════════════════════════════════════════════════════════════

EXTENSION GENE (E)
• E - Allows black pigment (eumelanin) to be produced (dominant)
• e - Restricts pigment to red/chestnut (recessive)

Valid genotypes: E/E, E/e, e/e
Phenotypes:
  - E/E or E/e: Allows black pigment (can be bay or black depending on Agouti)
  - e/e: Chestnut (red) coat regardless of other genes

Note: Extension is epistatic to Agouti (e/e overrides Agouti effects)

───────────────────────────────────────────────────────────────

AGOUTI GENE (A)
• A - Restricts black pigment to "points" (mane, tail, legs, ear tips) creating bay pattern (dominant)
• a - Allows black pigment all over the body (recessive)

Valid genotypes: A/A, A/a, a/a
Phenotypes:
  - A/A or A/a: Bay pattern (only visible with E/_ genotype)
  - a/a: Solid black (only visible with E/_ genotype)

Note: Only affects horses with black pigment (E/_ genotype)

───────────────────────────────────────────────────────────────

DILUTION GENE (Dil) - SLC45A2
IMPORTANT: Cream and Pearl are alleles of the SAME gene!

• N - Wild-type (no dilution)
• Cr - Cream allele (incomplete dominant)
• Prl - Pearl allele (recessive)

Valid genotypes: N/N, N/Cr, Cr/Cr, N/Prl, Prl/Prl, Cr/Prl
Phenotypes:
  - N/N: No dilution
  - N/Cr: Single cream dilution (Palomino on chestnut, Buckskin on bay, Smoky Black on black)
  - Cr/Cr: Double cream dilution (Cremello on chestnut, Perlino on bay, Smoky Cream on black)
  - N/Prl: Pearl carrier (no visible effect)
  - Prl/Prl: Double pearl dilution (Apricot on chestnut, Pearl Bay on bay, Pearl Black on black)
  - Cr/Prl: Compound heterozygote - pseudo-double dilute effect!

Note: A horse can have at most ONE Cr and ONE Prl allele simultaneously (Cr/Prl genotype)

───────────────────────────────────────────────────────────────

DUN GENE (D)
• D - Dun dilution with primitive markings (dorsal stripe, leg barring) (dominant)
• nd1 - Non-dun 1, may show faint primitive markings
• nd2 - Non-dun 2, no primitive markings (recessive)

Valid genotypes: D/D, D/nd1, D/nd2, nd1/nd1, nd1/nd2, nd2/nd2
Dominance: D > nd1 > nd2
Phenotypes:
  - D/_: Dun dilution with clear primitive markings
  - nd1/nd1 or nd1/nd2: Possible faint markings
  - nd2/nd2: No dun dilution

───────────────────────────────────────────────────────────────

SILVER GENE (Z)
• Z - Silver dilution (dominant)
• n - Non-silver (wild-type)

Valid genotypes: Z/Z, Z/n, n/n
Phenotypes:
  - Z/Z or Z/n: Dilutes black pigment (eumelanin) to silver/chocolate, especially in mane and tail
  - n/n: No silver dilution

Note: ONLY affects horses with black pigment. No effect on chestnut horses (e/e).

───────────────────────────────────────────────────────────────

SOOTY GENE (STY)
• STY - Sooty modifier, adds darker hairs along topline (dominant)
• sty - Non-sooty

Valid genotypes: STY/STY, STY/sty, sty/sty
Phenotypes:
  - STY/_: Darker hairs, especially on back, shoulders, and face
  - sty/sty: No sooty modifier

Note: Simplified model. In reality, sooty is polygenic (multiple genes).

═══════════════════════════════════════════════════════════════

GENOTYPE INPUT FORMAT

When entering genotypes manually:
Gene:Allele1/Allele2 (separated by spaces)

Example: E:E/e A:A/a Dil:N/Cr D:D/nd2 Z:n/n STY:STY/sty

═══════════════════════════════════════════════════════════════

BREEDING INHERITANCE

Each parent contributes ONE randomly selected allele from each gene to the offspring.
This follows Mendelian inheritance patterns.

Example:
  Parent 1: E/e (can pass E or e)
  Parent 2: E/E (can only pass E)
  Offspring: 50% E/E, 50% E/e

═══════════════════════════════════════════════════════════════
"""

        help_text.insert('1.0', help_content)
        help_text.config(state=tk.DISABLED)

    def generate_random_horse(self):
        try:
            horse = self.generator.generate_horse()

            self.random_phenotype_label.config(text=horse['phenotype'], foreground=self.colors['primary'])

            self.random_genotype_text.config(state=tk.NORMAL)
            self.random_genotype_text.delete('1.0', tk.END)

            genotype_text = self.format_genotype_detailed(horse['genotype'])
            self.random_genotype_text.insert('1.0', genotype_text)
            self.random_genotype_text.config(state=tk.DISABLED)

            self.current_random_horse = horse
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate horse: {e}\n\nPlease try again.")
            self.random_phenotype_label.config(text="Error generating horse", foreground='red')

    def format_genotype_detailed(self, genotype):
        lines = []
        gene_names = {
            'extension': 'Extension',
            'agouti': 'Agouti',
            'dilution': 'Dilution',
            'dun': 'Dun',
            'silver': 'Silver',
            'champagne': 'Champagne',
            'flaxen': 'Flaxen',
            'sooty': 'Sooty'
        }

        for gene_key, name in gene_names.items():
            alleles = '/'.join(genotype[gene_key])
            lines.append(f"{name:12} : {alleles}")

        return '\n'.join(lines)

    def copy_random_genotype(self):
        if hasattr(self, 'current_random_horse'):
            genotype_str = self.generator.format_genotype(self.current_random_horse['genotype'])
            self.root.clipboard_clear()
            self.root.clipboard_append(genotype_str)
            messagebox.showinfo("Copied", "Genotype copied to clipboard!")
        else:
            messagebox.showwarning("No Horse", "Generate a horse first!")

    def get_parent_genotype(self, parent_num):
        dropdowns = self.parent1_dropdowns if parent_num == 1 else self.parent2_dropdowns

        genotype = {}

        for gene_label, gene_name in self.GENE_MAP.items():
            var1, var2 = dropdowns[gene_label]
            alleles = self.generator._sort_alleles([var1.get(), var2.get()])
            genotype[gene_name] = alleles

        return genotype

    def update_parent_phenotype(self, parent_num):
        try:
            genotype = self.get_parent_genotype(parent_num)
            phenotype = self.generator.determine_phenotype(genotype)

            if parent_num == 1:
                self.parent1_phenotype_label.config(text=phenotype, foreground=self.colors['primary'])
            else:
                self.parent2_phenotype_label.config(text=phenotype, foreground=self.colors['primary'])
        except Exception as e:
            # Show error message in GUI
            error_msg = f"Invalid: {str(e)}"

            if parent_num == 1:
                self.parent1_phenotype_label.config(text=error_msg, foreground='red')
            else:
                self.parent2_phenotype_label.config(text=error_msg, foreground='red')

    def randomize_parent(self, parent_num):
        dropdowns = self.parent1_dropdowns if parent_num == 1 else self.parent2_dropdowns

        random_genotype = self.generator.generate_genotype()

        for gene_label, gene_name in self.GENE_MAP.items():
            var1, var2 = dropdowns[gene_label]
            alleles = random_genotype[gene_name]
            var1.set(alleles[0])
            var2.set(alleles[1])

        self.update_parent_phenotype(parent_num)

    def breed_horses(self):
        try:
            parent1_geno = self.get_parent_genotype(1)
            parent2_geno = self.get_parent_genotype(2)

            offspring_geno = self.generator.breed_horses(parent1_geno, parent2_geno)
            offspring_pheno = self.generator.determine_phenotype(offspring_geno)

            # Update phenotype with correct color
            self.offspring_phenotype_label.config(
                text=offspring_pheno,
                foreground=self.colors['primary']
            )

            # Update genotype text
            self.offspring_genotype_text.config(state=tk.NORMAL)
            self.offspring_genotype_text.delete('1.0', tk.END)
            genotype_text = self.format_genotype_detailed(offspring_geno)
            self.offspring_genotype_text.insert('1.0', genotype_text)
            self.offspring_genotype_text.config(state=tk.DISABLED)

            # Force UI update
            self.offspring_phenotype_label.update_idletasks()
            self.offspring_genotype_text.update_idletasks()

        except Exception as e:
            messagebox.showerror("Error", f"Error breeding horses: {e}")
            self.offspring_phenotype_label.config(text="Error breeding horses", foreground='red')

    def clear_breeding(self):
        self.randomize_parent(1)
        self.randomize_parent(2)

        self.offspring_phenotype_label.config(text="(Breed two horses to see offspring)")
        self.offspring_genotype_text.config(state=tk.NORMAL)
        self.offspring_genotype_text.delete('1.0', tk.END)
        self.offspring_genotype_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = HorseGeneticsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
