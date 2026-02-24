"""
Pedigree Tracking - Family tree management for horse breeding games

This module provides tools for tracking family relationships and visualizing
pedigrees. Perfect for breeding games that want to show lineage!

Example usage:
    from genetics.pedigree import PedigreeTree
    from genetics.horse import Horse

    # Create pedigree tracker
    tree = PedigreeTree()

    # Add horses to tree
    mare = Horse.random()
    stallion = Horse.random()
    foal = Horse.breed(mare, stallion)

    # Record breeding
    tree.add_breeding(stallion, mare, foal, generation=1)

    # Get ancestors
    ancestors = tree.get_ancestors(foal, depth=3)

    # Export to various formats
    tree.export_text("pedigree.txt")
    tree.export_json("pedigree.json")

    # Optional: visualize with matplotlib
    tree.export_graph("pedigree.png")
"""

from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import hashlib
import json


class PedigreeNode:
    """Represents a horse in the pedigree tree."""

    def __init__(
        self,
        horse_id: str,
        phenotype: str,
        genotype_string: str,
        generation: int = 0,
        name: Optional[str] = None,
        sire_id: Optional[str] = None,
        dam_id: Optional[str] = None,
        birth_date: Optional[str] = None
    ):
        """
        Initialize a pedigree node.

        Args:
            horse_id: Unique identifier for the horse
            phenotype: Coat color phenotype
            genotype_string: Complete genotype string
            generation: Generation number (0 = foundation, 1 = first bred, etc.)
            name: Optional horse name
            sire_id: ID of sire (father)
            dam_id: ID of dam (mother)
            birth_date: Optional birth date string
        """
        self.horse_id = horse_id
        self.phenotype = phenotype
        self.genotype_string = genotype_string
        self.generation = generation
        self.name = name or f"Horse_{horse_id[:8]}"
        self.sire_id = sire_id
        self.dam_id = dam_id
        self.birth_date = birth_date or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'horse_id': self.horse_id,
            'phenotype': self.phenotype,
            'genotype_string': self.genotype_string,
            'generation': self.generation,
            'name': self.name,
            'sire_id': self.sire_id,
            'dam_id': self.dam_id,
            'birth_date': self.birth_date
        }

    @staticmethod
    def from_dict(data: dict) -> 'PedigreeNode':
        """Create from dictionary."""
        return PedigreeNode(**data)


class PedigreeTree:
    """
    Manages a family tree of horses with breeding relationships.

    Supports:
    - Adding horses and breeding records
    - Querying ancestors and descendants
    - Detecting inbreeding
    - Exporting to text, JSON, and graph formats
    """

    def __init__(self):
        """Initialize an empty pedigree tree."""
        self.horses: Dict[str, PedigreeNode] = {}
        self.breedings: List[Tuple[str, str, str]] = []  # (sire_id, dam_id, foal_id)

    def add_horse(
        self,
        horse_id: str,
        phenotype: str,
        genotype_string: str,
        generation: int = 0,
        name: Optional[str] = None,
        sire_id: Optional[str] = None,
        dam_id: Optional[str] = None
    ) -> PedigreeNode:
        """
        Add a horse to the pedigree tree.

        Args:
            horse_id: Unique ID for this horse
            phenotype: Coat color
            genotype_string: Full genotype
            generation: Generation number
            name: Optional name
            sire_id: Father's ID (if known)
            dam_id: Mother's ID (if known)

        Returns:
            PedigreeNode object
        """
        node = PedigreeNode(
            horse_id=horse_id,
            phenotype=phenotype,
            genotype_string=genotype_string,
            generation=generation,
            name=name,
            sire_id=sire_id,
            dam_id=dam_id
        )

        self.horses[horse_id] = node
        return node

    def add_breeding(
        self,
        sire: 'Horse',
        dam: 'Horse',
        foal: 'Horse',
        generation: Optional[int] = None,
        sire_name: Optional[str] = None,
        dam_name: Optional[str] = None,
        foal_name: Optional[str] = None
    ) -> PedigreeNode:
        """
        Record a breeding and add foal to tree.

        Automatically adds parents if not already in tree.

        Args:
            sire: Sire (father) Horse object
            dam: Dam (mother) Horse object
            foal: Foal (offspring) Horse object
            generation: Optional generation number (auto-calculated if None)
            sire_name: Optional name for sire
            dam_name: Optional name for dam
            foal_name: Optional name for foal

        Returns:
            PedigreeNode for the foal
        """
        # Generate deterministic IDs from genotype strings
        sire_id = hashlib.md5(sire.genotype_string.encode()).hexdigest()[:16]
        dam_id = hashlib.md5(dam.genotype_string.encode()).hexdigest()[:16]
        foal_id = hashlib.md5(foal.genotype_string.encode()).hexdigest()[:16]

        # Add parents if not already in tree
        if sire_id not in self.horses:
            self.add_horse(
                horse_id=sire_id,
                phenotype=sire.phenotype,
                genotype_string=sire.genotype_string,
                generation=0,
                name=sire_name
            )

        if dam_id not in self.horses:
            self.add_horse(
                horse_id=dam_id,
                phenotype=dam.phenotype,
                genotype_string=dam.genotype_string,
                generation=0,
                name=dam_name
            )

        # Calculate generation if not provided
        if generation is None:
            sire_gen = self.horses[sire_id].generation
            dam_gen = self.horses[dam_id].generation
            generation = max(sire_gen, dam_gen) + 1

        # Add foal
        foal_node = self.add_horse(
            horse_id=foal_id,
            phenotype=foal.phenotype,
            genotype_string=foal.genotype_string,
            generation=generation,
            name=foal_name,
            sire_id=sire_id,
            dam_id=dam_id
        )

        # Record breeding
        self.breedings.append((sire_id, dam_id, foal_id))

        return foal_node

    def get_parents(self, horse_id: str) -> Tuple[Optional[PedigreeNode], Optional[PedigreeNode]]:
        """
        Get parents of a horse.

        Args:
            horse_id: Horse ID to look up

        Returns:
            tuple: (sire_node, dam_node) or (None, None) if not found
        """
        if horse_id not in self.horses:
            return None, None

        horse = self.horses[horse_id]

        sire = self.horses.get(horse.sire_id) if horse.sire_id else None
        dam = self.horses.get(horse.dam_id) if horse.dam_id else None

        return sire, dam

    def get_ancestors(self, horse_id: str, depth: int = 3) -> List[PedigreeNode]:
        """
        Get ancestors of a horse up to specified depth.

        Args:
            horse_id: Horse ID
            depth: How many generations to go back (1 = parents, 2 = grandparents, etc.)

        Returns:
            List of ancestor PedigreeNode objects
        """
        ancestors = []
        current_generation = [horse_id]

        for _ in range(depth):
            next_generation = []

            for current_id in current_generation:
                sire, dam = self.get_parents(current_id)

                if sire:
                    ancestors.append(sire)
                    next_generation.append(sire.horse_id)

                if dam:
                    ancestors.append(dam)
                    next_generation.append(dam.horse_id)

            current_generation = next_generation

            if not current_generation:
                break

        return ancestors

    def get_descendants(self, horse_id: str) -> List[PedigreeNode]:
        """
        Get all descendants of a horse.

        Args:
            horse_id: Horse ID

        Returns:
            List of descendant PedigreeNode objects
        """
        descendants = []

        for sire_id, dam_id, foal_id in self.breedings:
            if sire_id == horse_id or dam_id == horse_id:
                foal = self.horses[foal_id]
                descendants.append(foal)

                # Recursively get descendants of this foal
                descendants.extend(self.get_descendants(foal_id))

        return descendants

    def detect_inbreeding(self, horse_id: str, depth: int = 3) -> Dict[str, int]:
        """
        Detect inbreeding by finding duplicate ancestors.

        Args:
            horse_id: Horse ID to check
            depth: How many generations to check

        Returns:
            dict: {ancestor_id: number_of_occurrences} for ancestors appearing multiple times
        """
        ancestors = self.get_ancestors(horse_id, depth)
        ancestor_ids = [a.horse_id for a in ancestors]

        # Count occurrences
        from collections import Counter
        counts = Counter(ancestor_ids)

        # Return only duplicates
        inbreeding = {aid: count for aid, count in counts.items() if count > 1}

        return inbreeding

    def export_text(self, filename: str):
        """
        Export pedigree to text file.

        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("PEDIGREE TREE\n")
            f.write("=" * 80 + "\n\n")

            # Group by generation
            by_generation = {}
            for horse in self.horses.values():
                gen = horse.generation
                if gen not in by_generation:
                    by_generation[gen] = []
                by_generation[gen].append(horse)

            # Write each generation
            for gen in sorted(by_generation.keys()):
                f.write(f"\n--- Generation {gen} ---\n\n")

                for horse in by_generation[gen]:
                    f.write(f"{horse.name} - {horse.phenotype}\n")
                    f.write(f"  ID: {horse.horse_id}\n")
                    f.write(f"  Genotype: {horse.genotype_string}\n")

                    if horse.sire_id or horse.dam_id:
                        sire, dam = self.get_parents(horse.horse_id)
                        sire_name = sire.name if sire else "Unknown"
                        dam_name = dam.name if dam else "Unknown"
                        f.write(f"  Parents: {sire_name} × {dam_name}\n")

                    f.write("\n")

            # Write breeding records
            f.write("\n" + "=" * 80 + "\n")
            f.write("BREEDING RECORDS\n")
            f.write("=" * 80 + "\n\n")

            for sire_id, dam_id, foal_id in self.breedings:
                sire = self.horses[sire_id]
                dam = self.horses[dam_id]
                foal = self.horses[foal_id]

                f.write(f"{sire.name} ({sire.phenotype}) × {dam.name} ({dam.phenotype})\n")
                f.write(f"  → {foal.name} ({foal.phenotype})\n\n")

    def export_json(self, filename: str):
        """
        Export pedigree to JSON file.

        Args:
            filename: Output filename
        """
        data = {
            'horses': {hid: horse.to_dict() for hid, horse in self.horses.items()},
            'breedings': [
                {
                    'sire_id': sire_id,
                    'dam_id': dam_id,
                    'foal_id': foal_id
                }
                for sire_id, dam_id, foal_id in self.breedings
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def export_graph(self, filename: str):
        """
        Export pedigree as a visual graph (requires matplotlib).

        Args:
            filename: Output filename (e.g., 'pedigree.png')
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
        except ImportError:
            print("Error: matplotlib not installed")
            print("Install with: pip install matplotlib")
            return

        fig, ax = plt.subplots(figsize=(16, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Group horses by generation
        by_generation = {}
        for horse in self.horses.values():
            gen = horse.generation
            if gen not in by_generation:
                by_generation[gen] = []
            by_generation[gen].append(horse)

        # Calculate positions
        positions = {}
        max_gen = max(by_generation.keys()) or 1  # Avoid ZeroDivisionError

        for gen, horses in by_generation.items():
            y = 9 - (gen / max_gen) * 8  # Top to bottom
            num_horses = len(horses)

            for i, horse in enumerate(horses):
                x = (i + 1) * 10 / (num_horses + 1)
                positions[horse.horse_id] = (x, y)

        # Draw horses
        for horse_id, (x, y) in positions.items():
            horse = self.horses[horse_id]

            # Draw box
            rect = patches.FancyBboxPatch(
                (x - 0.4, y - 0.2), 0.8, 0.4,
                boxstyle="round,pad=0.05",
                edgecolor='black',
                facecolor='lightblue',
                linewidth=1.5
            )
            ax.add_patch(rect)

            # Add text
            ax.text(x, y + 0.05, horse.name, ha='center', va='center', fontsize=9, weight='bold')
            ax.text(x, y - 0.05, horse.phenotype, ha='center', va='center', fontsize=7)

        # Draw lines between parents and offspring
        for sire_id, dam_id, foal_id in self.breedings:
            if sire_id in positions and dam_id in positions and foal_id in positions:
                sire_x, sire_y = positions[sire_id]
                dam_x, dam_y = positions[dam_id]
                foal_x, foal_y = positions[foal_id]

                # Line from sire to foal
                ax.plot([sire_x, foal_x], [sire_y - 0.2, foal_y + 0.2],
                       'k-', linewidth=1, alpha=0.5)

                # Line from dam to foal
                ax.plot([dam_x, foal_x], [dam_y - 0.2, foal_y + 0.2],
                       'k-', linewidth=1, alpha=0.5)

        plt.title('Horse Pedigree Tree', fontsize=16, weight='bold')
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Pedigree graph saved to {filename}")

    @staticmethod
    def load_from_json(filename: str) -> 'PedigreeTree':
        """
        Load pedigree from JSON file.

        Args:
            filename: JSON file to load

        Returns:
            PedigreeTree object
        """
        with open(filename, 'r') as f:
            data = json.load(f)

        tree = PedigreeTree()

        # Load horses
        for horse_id, horse_data in data['horses'].items():
            tree.horses[horse_id] = PedigreeNode.from_dict(horse_data)

        # Load breedings
        tree.breedings = [
            (b['sire_id'], b['dam_id'], b['foal_id'])
            for b in data['breedings']
        ]

        return tree
