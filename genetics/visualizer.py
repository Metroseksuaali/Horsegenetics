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

    def generate_svg(self, phenotype: str, genotype: Optional[Dict] = None) -> str:
        """
        Generate SVG image of horse based on phenotype.

        Args:
            phenotype: Phenotype string (e.g., "Bay Tobiano")
            genotype: Optional genotype dict for more detailed rendering

        Returns:
            SVG string
        """
        base_color = self._get_base_color_from_phenotype(phenotype)
        base_hex = self._rgb_to_hex(base_color)

        # Simplified horse silhouette SVG
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{base_hex};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{self._rgb_to_hex(tuple(max(0, c-30) for c in base_color))};stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Horse body -->
  <ellipse cx="200" cy="180" rx="120" ry="80" fill="url(#bodyGradient)" stroke="black" stroke-width="2"/>

  <!-- Horse neck -->
  <ellipse cx="130" cy="120" rx="40" ry="70" fill="url(#bodyGradient)" stroke="black" stroke-width="2"/>

  <!-- Horse head -->
  <ellipse cx="100" cy="70" rx="30" ry="35" fill="url(#bodyGradient)" stroke="black" stroke-width="2"/>

  <!-- Legs (front) -->
  <rect x="160" y="240" width="15" height="55" fill="{base_hex}" stroke="black" stroke-width="2"/>
  <rect x="190" y="240" width="15" height="55" fill="{base_hex}" stroke="black" stroke-width="2"/>

  <!-- Legs (back) -->
  <rect x="270" y="240" width="15" height="55" fill="{base_hex}" stroke="black" stroke-width="2"/>
  <rect x="300" y="240" width="15" height="55" fill="{base_hex}" stroke="black" stroke-width="2"/>

  <!-- Mane -->
  <path d="M 130 60 Q 120 80 115 100 Q 120 90 125 105 Q 120 95 120 110"
        fill="{self._rgb_to_hex((0, 0, 0))}" stroke="black" stroke-width="1"/>

  <!-- Tail -->
  <path d="M 310 170 Q 340 180 350 200 Q 345 185 355 210 Q 350 195 360 220"
        fill="{self._rgb_to_hex((0, 0, 0))}" stroke="black" stroke-width="1"/>
'''

        # Add white patterns if present
        if self._has_white_pattern(phenotype):
            # Tobiano-style white patches
            svg += '''
  <!-- White patches (Tobiano/Pinto pattern) -->
  <ellipse cx="200" cy="140" rx="60" ry="40" fill="white" opacity="0.9"/>
  <ellipse cx="170" cy="180" rx="40" ry="30" fill="white" opacity="0.9"/>
  <rect x="270" y="155" width="50" height="50" fill="white" opacity="0.9" rx="10"/>
'''

        # Add leopard spots if present
        if self._has_leopard(phenotype):
            svg += '''
  <!-- Leopard/Appaloosa spots -->
  <circle cx="180" cy="160" r="8" fill="''' + base_hex + '''" opacity="0.8"/>
  <circle cx="210" cy="170" r="7" fill="''' + base_hex + '''" opacity="0.8"/>
  <circle cx="190" cy="190" r="6" fill="''' + base_hex + '''" opacity="0.8"/>
  <circle cx="230" cy="180" r="8" fill="''' + base_hex + '''" opacity="0.8"/>
  <circle cx="250" cy="170" r="7" fill="''' + base_hex + '''" opacity="0.8"/>
  <circle cx="270" cy="190" r="6" fill="''' + base_hex + '''" opacity="0.8"/>
'''

        # Add roan effect (scattered white hairs)
        if self._is_roan(phenotype) and not self._has_white_pattern(phenotype):
            import random
            random.seed(hash(phenotype))  # Consistent pattern for same phenotype
            roan_dots = ""
            for _ in range(50):
                x = random.randint(150, 320)
                y = random.randint(120, 240)
                roan_dots += f'  <circle cx="{x}" cy="{y}" r="1" fill="white" opacity="0.6"/>\n'
            svg += roan_dots

        # Phenotype label
        svg += f'''
  <!-- Phenotype label -->
  <text x="200" y="290" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">
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
