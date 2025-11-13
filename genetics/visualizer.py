"""
Horse Color Visualizer

Generates SVG images of horses based on their genotype.
Colors and patterns are rendered according to the horse's genetic makeup.
"""

from typing import Dict, Tuple, Optional
import re


class HorseVisualizer:
    """
    Generate visual representations of horses based on genotype.

    Creates SVG images with accurate colors and patterns.
    """

    def __init__(self):
        """Initialize the visualizer with color mappings."""
        # Base color RGB mappings (approximations)
        self.base_colors = {
            'Chestnut': (139, 69, 19),      # Saddle brown
            'Bay': (101, 67, 33),            # Dark brown body
            'Black': (20, 20, 20),           # Nearly black
            'Palomino': (218, 165, 32),      # Golden
            'Buckskin': (222, 184, 135),     # Burlywood
            'Cremello': (255, 250, 205),     # Lemon chiffon
            'Perlino': (250, 235, 215),      # Antique white
            'Smoky Black': (64, 64, 64),     # Dark gray
            'Smoky Cream': (245, 245, 220),  # Beige
            'Silver': (192, 192, 192),       # Silver
            'Champagne': (244, 164, 96),     # Sandy brown
            'Dun': (210, 180, 140),          # Tan
            'Grullo': (128, 128, 128),       # Gray
        }

        # Point colors (mane, tail, legs for bay)
        self.bay_points = (0, 0, 0)  # Black
        self.palomino_mane = (255, 255, 224)  # Light yellow

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color string."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _get_base_color_from_phenotype(self, phenotype: str) -> Tuple[int, int, int]:
        """
        Extract base color from phenotype string.

        Args:
            phenotype: Full phenotype string (e.g., "Bay Roan Tobiano")

        Returns:
            RGB tuple for base color
        """
        # Check for known color names in order of specificity
        phenotype_lower = phenotype.lower()

        # Check for Dominant White (overrides everything)
        if 'dominant white' in phenotype_lower:
            return (255, 255, 255)  # Pure white

        # Check for specific dilutions first
        if 'cremello' in phenotype_lower:
            return self.base_colors['Cremello']
        if 'perlino' in phenotype_lower:
            return self.base_colors['Perlino']
        if 'smoky cream' in phenotype_lower:
            return self.base_colors['Smoky Cream']
        if 'smoky black' in phenotype_lower:
            return self.base_colors['Smoky Black']

        # Check for diluted colors
        if 'palomino' in phenotype_lower or 'dunalino' in phenotype_lower:
            return self.base_colors['Palomino']
        if 'buckskin' in phenotype_lower or 'dunskin' in phenotype_lower:
            return self.base_colors['Buckskin']

        # Check for dun colors
        if 'grullo' in phenotype_lower or 'black dun' in phenotype_lower:
            return self.base_colors['Grullo']
        if 'dun' in phenotype_lower:
            return self.base_colors['Dun']

        # Check for champagne
        if 'champagne' in phenotype_lower:
            return self.base_colors['Champagne']

        # Check for silver
        if 'silver' in phenotype_lower:
            return self.base_colors['Silver']

        # Check base colors
        if 'chestnut' in phenotype_lower or 'red' in phenotype_lower:
            return self.base_colors['Chestnut']
        if 'bay' in phenotype_lower:
            return self.base_colors['Bay']
        if 'black' in phenotype_lower:
            return self.base_colors['Black']

        # Default to bay if unclear
        return self.base_colors['Bay']

    def _has_white_pattern(self, phenotype: str) -> bool:
        """Check if phenotype has white spotting patterns."""
        patterns = ['tobiano', 'overo', 'sabino', 'splash', 'tovero', 'frame']
        phenotype_lower = phenotype.lower()
        return any(pattern in phenotype_lower for pattern in patterns)

    def _has_leopard(self, phenotype: str) -> bool:
        """Check if phenotype has leopard/appaloosa pattern."""
        patterns = ['leopard', 'fewspot', 'blanket']
        phenotype_lower = phenotype.lower()
        return any(pattern in phenotype_lower for pattern in patterns)

    def _is_roan(self, phenotype: str) -> bool:
        """Check if phenotype is roan."""
        return 'roan' in phenotype.lower()

    def _get_horse_pixel_map(self) -> list:
        """
        Get pixel art representation of a horse (side view).

        Returns 2D array where:
        0 = transparent
        1 = body
        2 = mane/tail
        3 = leg
        4 = head
        5 = ear
        6 = eye
        """
        # 40 wide x 32 tall pixel art horse
        return [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,5,5,4,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,5,4,4,4,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,4,4,6,4,4,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,2,2,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,2,2,1,1,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,2,2,1,1,1,1,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,2,2,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,2,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,2,2,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,2,2,0],
            [0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,2,2,2,2,0],
            [0,0,0,3,3,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,2,2,2,2,2,0],
            [0,0,0,3,3,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,0],
            [0,0,0,3,3,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,0,0],
            [0,0,0,3,3,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,0,0,0],
            [0,0,0,3,3,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,0,0,0,0],
            [0,0,0,3,3,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,3,1,1,1,1,1,1,1,2,0,0,0,0,0],
            [0,0,0,3,3,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,3,3,1,1,1,1,1,1,1,0,0,0,0,0,0],
            [0,0,0,3,3,3,0,0,3,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,3,3,1,1,1,1,1,1,1,0,0,0,0,0,0],
            [0,0,0,3,3,3,0,0,3,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,3,3,1,1,1,1,1,1,0,0,0,0,0,0,0],
            [0,0,0,3,3,3,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,3,3,3,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,3,3,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,3,3,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ]

    def generate_svg(self, phenotype: str, genotype: Optional[Dict] = None) -> str:
        """
        Generate pixel art SVG image of horse based on phenotype.

        Args:
            phenotype: Phenotype string (e.g., "Bay Tobiano")
            genotype: Optional genotype dict for more detailed rendering

        Returns:
            SVG string
        """
        base_color = self._get_base_color_from_phenotype(phenotype)
        base_hex = self._rgb_to_hex(base_color)

        # Get darker shade for mane/tail (black points for bay)
        is_bay = 'bay' in phenotype.lower() and 'dun' not in phenotype.lower()
        mane_color = self._rgb_to_hex(self.bay_points if is_bay else tuple(max(0, c-40) for c in base_color))

        # Leg color (black for bay, otherwise base color)
        leg_color = self._rgb_to_hex(self.bay_points if is_bay else base_color)

        # Head color (same as body)
        head_color = base_hex

        # Ear color (slightly darker)
        ear_color = self._rgb_to_hex(tuple(max(0, c-20) for c in base_color))

        pixel_size = 8
        horse_map = self._get_horse_pixel_map()
        width = len(horse_map[0]) * pixel_size
        height = len(horse_map) * pixel_size

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width + 40}" height="{height + 60}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#f0f0f0"/>

  <!-- Pixel art horse -->
  <g transform="translate(20, 10)">
'''

        # Render base horse
        for y, row in enumerate(horse_map):
            for x, pixel in enumerate(row):
                if pixel == 0:
                    continue

                # Determine pixel color
                if pixel == 1:  # Body
                    color = base_hex
                elif pixel == 2:  # Mane/tail
                    color = mane_color
                elif pixel == 3:  # Leg
                    color = leg_color
                elif pixel == 4:  # Head
                    color = head_color
                elif pixel == 5:  # Ear
                    color = ear_color
                elif pixel == 6:  # Eye
                    color = "#000000"
                else:
                    color = base_hex

                svg += f'    <rect x="{x * pixel_size}" y="{y * pixel_size}" width="{pixel_size}" height="{pixel_size}" fill="{color}" stroke="#333" stroke-width="0.5"/>\n'

        # Add white patterns if present
        if self._has_white_pattern(phenotype):
            import random
            random.seed(hash(phenotype))
            # Add white patches on body
            for y, row in enumerate(horse_map):
                for x, pixel in enumerate(row):
                    if pixel == 1:  # Only on body
                        # Create patches based on pattern type
                        if 'tobiano' in phenotype.lower():
                            # Tobiano: large patches on back/sides
                            if (15 <= x <= 30 and 12 <= y <= 20) or (x > 25 and 18 <= y <= 24):
                                if random.random() < 0.7:
                                    svg += f'    <rect x="{x * pixel_size}" y="{y * pixel_size}" width="{pixel_size}" height="{pixel_size}" fill="white" stroke="#333" stroke-width="0.5"/>\n'
                        elif 'frame' in phenotype.lower() or 'overo' in phenotype.lower():
                            # Frame/Overo: scattered white on body
                            if 15 <= x <= 28 and 14 <= y <= 22:
                                if random.random() < 0.4:
                                    svg += f'    <rect x="{x * pixel_size}" y="{y * pixel_size}" width="{pixel_size}" height="{pixel_size}" fill="white" stroke="#333" stroke-width="0.5"/>\n'
                        elif 'sabino' in phenotype.lower():
                            # Sabino: white on legs and belly
                            if y >= 22 or (16 <= y <= 20 and random.random() < 0.3):
                                svg += f'    <rect x="{x * pixel_size}" y="{y * pixel_size}" width="{pixel_size}" height="{pixel_size}" fill="white" stroke="#333" stroke-width="0.5"/>\n'

        # Add leopard spots if present
        if self._has_leopard(phenotype):
            import random
            random.seed(hash(phenotype) + 1)
            for y, row in enumerate(horse_map):
                for x, pixel in enumerate(row):
                    if pixel == 1 and 12 <= y <= 24:  # Spots on body
                        if random.random() < 0.15:
                            spot_size = pixel_size * random.choice([1, 2])
                            svg += f'    <ellipse cx="{x * pixel_size + pixel_size/2}" cy="{y * pixel_size + pixel_size/2}" rx="{spot_size}" ry="{spot_size}" fill="{mane_color}" opacity="0.8"/>\n'

        # Add roan effect
        if self._is_roan(phenotype):
            import random
            random.seed(hash(phenotype) + 2)
            for y, row in enumerate(horse_map):
                for x, pixel in enumerate(row):
                    if pixel == 1:  # Only on body
                        if random.random() < 0.25:
                            svg += f'    <rect x="{x * pixel_size}" y="{y * pixel_size}" width="{pixel_size}" height="{pixel_size}" fill="white" opacity="0.4" stroke="none"/>\n'

        svg += '  </g>\n'

        # Phenotype label
        svg += f'''
  <text x="{(width + 40) / 2}" y="{height + 40}" text-anchor="middle" font-family="monospace" font-size="12" font-weight="bold" fill="#333">
    {phenotype}
  </text>

</svg>'''

        return svg

    def save_svg(self, phenotype: str, filename: str, genotype: Optional[Dict] = None):
        """
        Generate and save SVG image to file.

        Args:
            phenotype: Phenotype string
            filename: Output filename (should end with .svg)
            genotype: Optional genotype dict
        """
        svg_content = self.generate_svg(phenotype, genotype)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        print(f"✓ Horse image saved to: {filename}")


def visualize_horse(phenotype: str, output_file: str = "horse.svg", genotype: Optional[Dict] = None):
    """
    Convenience function to visualize a horse.

    Args:
        phenotype: Phenotype string (e.g., "Bay Tobiano")
        output_file: Output filename (default: horse.svg)
        genotype: Optional genotype dictionary

    Example:
        >>> visualize_horse("Grullo (Black Dun) Tobiano", "my_horse.svg")
        ✓ Horse image saved to: my_horse.svg
    """
    visualizer = HorseVisualizer()
    visualizer.save_svg(phenotype, output_file, genotype)


if __name__ == '__main__':
    # Demo: Generate example horses
    examples = [
        "Bay",
        "Chestnut Roan",
        "Bay Tobiano",
        "Palomino",
        "Grullo (Black Dun)",
        "Bay Leopard",
        "Dominant White (W20)",
    ]

    print("Generating example horse images...")
    for i, phenotype in enumerate(examples, 1):
        filename = f"example_horse_{i}.svg"
        visualize_horse(phenotype, filename)

    print(f"\n✓ Generated {len(examples)} example horse images!")
