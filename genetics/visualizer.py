"""
Horse Color Visualizer

Generates SVG images of horses based on their genotype.
Colors and patterns are rendered according to the horse's genetic makeup.
"""

from typing import Dict, Tuple, Optional
import re
import os
import xml.etree.ElementTree as ET


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

        # Template path
        self.template_path = os.path.join(os.path.dirname(__file__), 'horse_template.svg')

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

    def _darken_color(self, rgb: Tuple[int, int, int], amount: int = 40) -> Tuple[int, int, int]:
        """Darken an RGB color by the specified amount."""
        return tuple(max(0, c - amount) for c in rgb)

    def _lighten_color(self, rgb: Tuple[int, int, int], amount: int = 40) -> Tuple[int, int, int]:
        """Lighten an RGB color by the specified amount."""
        return tuple(min(255, c + amount) for c in rgb)

    def _load_and_color_template(self, phenotype: str) -> str:
        """
        Load the horse template SVG and apply colors based on phenotype.

        Args:
            phenotype: Phenotype string (e.g., "Bay Tobiano")

        Returns:
            Colored SVG string
        """
        # Check if template exists
        if not os.path.exists(self.template_path):
            # Fall back to pixel art if template is missing
            return None

        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Parse SVG
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        root = ET.fromstring(svg_content)

        # Get colors for this phenotype
        base_color = self._get_base_color_from_phenotype(phenotype)
        base_hex = self._rgb_to_hex(base_color)

        # Determine if this is a bay (black points)
        is_bay = 'bay' in phenotype.lower() and 'dun' not in phenotype.lower()

        # Mane/tail color
        if is_bay:
            mane_color = self._rgb_to_hex(self.bay_points)
        elif 'palomino' in phenotype.lower():
            mane_color = self._rgb_to_hex(self.palomino_mane)
        else:
            mane_color = self._rgb_to_hex(self._darken_color(base_color, 60))

        # Leg color
        if is_bay:
            leg_color = self._rgb_to_hex(self.bay_points)
        else:
            leg_color = base_hex

        # Apply colors to template
        ns = {'svg': 'http://www.w3.org/2000/svg'}

        # Color body parts
        for elem in root.findall('.//*[@id="body"]//*//', ns):
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = base_hex
        for elem in root.findall('.//*[@id="body"]//*', ns):
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = base_hex
        body_group = root.find('.//*[@id="body"]', ns)
        if body_group is not None:
            for elem in body_group:
                if 'fill' in elem.attrib:
                    elem.attrib['fill'] = base_hex

        # Color head
        for elem in root.findall('.//*[@id="head"]//*', ns):
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = base_hex
        head_group = root.find('.//*[@id="head"]', ns)
        if head_group is not None:
            for elem in head_group:
                if 'fill' in elem.attrib:
                    elem.attrib['fill'] = base_hex

        # Color ears
        for elem in root.findall('.//*[@id="ears"]//*', ns):
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = base_hex
        ears_group = root.find('.//*[@id="ears"]', ns)
        if ears_group is not None:
            for elem in ears_group:
                if 'fill' in elem.attrib:
                    elem.attrib['fill'] = base_hex

        # Color mane
        for elem in root.findall('.//*[@id="mane"]//*', ns):
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = mane_color
        mane_group = root.find('.//*[@id="mane"]', ns)
        if mane_group is not None:
            for elem in mane_group:
                if 'fill' in elem.attrib:
                    elem.attrib['fill'] = mane_color

        # Color tail
        for elem in root.findall('.//*[@id="tail"]//*', ns):
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = mane_color
        tail_group = root.find('.//*[@id="tail"]', ns)
        if tail_group is not None:
            for elem in tail_group:
                if 'fill' in elem.attrib:
                    elem.attrib['fill'] = mane_color

        # Color legs
        for leg_id in ['leg-front-left', 'leg-front-right', 'leg-back-left', 'leg-back-right']:
            for elem in root.findall(f'.//*[@id="{leg_id}"]//*', ns):
                if 'fill' in elem.attrib and elem.attrib['fill'] != '#2C1810':  # Don't recolor hooves
                    elem.attrib['fill'] = leg_color
            leg_group = root.find(f'.//*[@id="{leg_id}"]', ns)
            if leg_group is not None:
                for elem in leg_group:
                    if 'fill' in elem.attrib and elem.attrib['fill'] != '#2C1810':  # Don't recolor hooves
                        elem.attrib['fill'] = leg_color

        # Add white patterns if present
        if self._has_white_pattern(phenotype):
            self._add_white_patterns(root, phenotype, ns)

        # Add leopard spots if present
        if self._has_leopard(phenotype):
            self._add_leopard_spots(root, phenotype, ns)

        # Add roan effect if present
        if self._is_roan(phenotype):
            self._add_roan_effect(root, phenotype, ns)

        # Convert back to string
        svg_string = ET.tostring(root, encoding='unicode')

        # Add phenotype label
        svg_string = svg_string.replace('</svg>', f'''
  <text x="200" y="290" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333">
    {phenotype}
  </text>
</svg>''')

        # Add XML declaration at the beginning
        svg_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_string

        return svg_string

    def _add_white_patterns(self, root, phenotype: str, ns: dict):
        """Add white pattern overlays to the horse."""
        import random
        random.seed(hash(phenotype))

        # Create pattern group
        pattern_group = ET.Element('g', {'id': 'white-patterns'})

        phenotype_lower = phenotype.lower()

        if 'tobiano' in phenotype_lower:
            # Tobiano: large patches on back and sides
            patches = [
                ('M 180 160 Q 220 155 260 160 Q 270 170 275 185 Q 270 200 260 205 Q 220 210 180 205 Q 170 190 175 175 Z', 0.95),
                ('M 140 175 Q 160 170 180 175 Q 185 185 180 195 Q 160 200 140 195 Q 135 185 140 175 Z', 0.9),
                ('M 250 200 Q 270 195 285 200 Q 290 215 285 230 Q 270 235 250 230 Q 245 215 250 200 Z', 0.95),
            ]
            for path_d, opacity in patches:
                if random.random() < 0.85:
                    path = ET.Element('path', {'d': path_d, 'fill': 'white', 'opacity': str(opacity)})
                    pattern_group.append(path)

        elif 'frame' in phenotype_lower or 'overo' in phenotype_lower:
            # Overo/Frame: scattered patches, avoiding legs and back
            patches = [
                ('M 160 180 Q 180 175 195 180 Q 200 190 195 200 Q 180 205 160 200 Q 155 190 160 180 Z', 0.9),
                ('M 210 185 Q 230 180 245 185 Q 250 195 245 205 Q 230 210 210 205 Q 205 195 210 185 Z', 0.88),
                ('M 120 70 Q 130 65 138 70 Q 140 80 135 88 Q 125 92 115 87 Q 112 77 120 70 Z', 0.92),  # Face
            ]
            for path_d, opacity in patches:
                if random.random() < 0.7:
                    path = ET.Element('path', {'d': path_d, 'fill': 'white', 'opacity': str(opacity)})
                    pattern_group.append(path)

        elif 'sabino' in phenotype_lower:
            # Sabino: white on legs and belly
            patches = [
                ('M 150 220 Q 180 225 210 220 Q 215 230 210 240 Q 180 245 150 240 Q 145 230 150 220 Z', 0.85),  # Belly
                ('M 155 240 L 173 240 L 173 290 L 155 290 Z', 0.9),  # Front leg white
                ('M 248 245 L 265 245 L 265 290 L 248 290 Z', 0.9),  # Back leg white
            ]
            for path_d, opacity in patches:
                path = ET.Element('path', {'d': path_d, 'fill': 'white', 'opacity': str(opacity)})
                pattern_group.append(path)

        if len(pattern_group) > 0:
            root.insert(0, pattern_group)

    def _add_leopard_spots(self, root, phenotype: str, ns: dict):
        """Add leopard/appaloosa spots to the horse."""
        import random
        random.seed(hash(phenotype) + 1)

        # Create spots group
        spots_group = ET.Element('g', {'id': 'leopard-spots'})

        # Add random spots on body
        for _ in range(30):
            x = random.randint(150, 280)
            y = random.randint(170, 220)
            rx = random.randint(4, 10)
            ry = random.randint(4, 10)
            opacity = random.uniform(0.6, 0.9)

            spot = ET.Element('ellipse', {
                'cx': str(x),
                'cy': str(y),
                'rx': str(rx),
                'ry': str(ry),
                'fill': '#2C1810',
                'opacity': str(opacity)
            })
            spots_group.append(spot)

        root.insert(0, spots_group)

    def _add_roan_effect(self, root, phenotype: str, ns: dict):
        """Add roan effect (white hairs mixed in) to the horse."""
        import random
        random.seed(hash(phenotype) + 2)

        # Create roan group
        roan_group = ET.Element('g', {'id': 'roan-effect'})

        # Add small white circles scattered over body
        for _ in range(150):
            x = random.randint(140, 290)
            y = random.randint(160, 230)
            r = random.uniform(1, 2.5)
            opacity = random.uniform(0.3, 0.6)

            dot = ET.Element('circle', {
                'cx': str(x),
                'cy': str(y),
                'r': str(r),
                'fill': 'white',
                'opacity': str(opacity)
            })
            roan_group.append(dot)

        root.insert(0, roan_group)

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
        Generate SVG image of horse based on phenotype.

        Uses high-quality template-based rendering if available,
        falls back to pixel art if template is missing.

        Args:
            phenotype: Phenotype string (e.g., "Bay Tobiano")
            genotype: Optional genotype dict for more detailed rendering

        Returns:
            SVG string
        """
        # Try template-based rendering first
        template_svg = self._load_and_color_template(phenotype)
        if template_svg is not None:
            return template_svg

        # Fall back to pixel art
        return self._generate_pixel_art_svg(phenotype, genotype)

    def _generate_pixel_art_svg(self, phenotype: str, genotype: Optional[Dict] = None) -> str:
        """
        Generate pixel art SVG image of horse based on phenotype.

        Legacy method kept as fallback.

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
