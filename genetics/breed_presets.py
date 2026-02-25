"""
Breed Presets - Predefined gene configurations for different horse breeds

This module provides realistic gene frequency presets for various horse breeds
and fantasy breeds, making it easy to generate breed-specific horses.
"""

from typing import Dict, Set, Optional


class BreedPreset:
    """Represents a breed with specific gene configurations."""

    def __init__(
        self,
        name: str,
        description: str,
        excluded_genes: Optional[Set[str]] = None,
        custom_probabilities: Optional[Dict[str, float]] = None,
        base_color_weights: Optional[Dict[str, float]] = None
    ):
        """
        Create a breed preset.

        Args:
            name: Breed name (e.g., "Arabian")
            description: Short description of the breed
            excluded_genes: Genes to exclude completely
            custom_probabilities: Custom gene frequencies
            base_color_weights: Base color preferences (future use)
        """
        self.name = name
        self.description = description
        self.excluded_genes = excluded_genes or set()
        self.custom_probabilities = custom_probabilities or {}
        self.base_color_weights = base_color_weights or {}


# ============================================================================
# REALISTIC BREED PRESETS
# ============================================================================

REALISTIC_BREEDS = {
    'arabian': BreedPreset(
        name="Arabian",
        description="Ancient desert breed - grays common, no heavy patterns",
        excluded_genes={'kit', 'frame', 'splash', 'leopard'},
        custom_probabilities={
            'gray': 0.5,      # 75% gray (very common in Arabians)
        }
    ),

    'thoroughbred': BreedPreset(
        name="Thoroughbred",
        description="Racing breed - solid colors, minimal white",
        excluded_genes={'kit', 'frame', 'splash', 'leopard', 'champagne'},
        custom_probabilities={
            'gray': 0.92,     # Uncommon but exists
        }
    ),

    'friesian': BreedPreset(
        name="Friesian",
        description="Dutch breed - only black, no white patterns",
        excluded_genes={'gray', 'kit', 'frame', 'splash', 'leopard', 'champagne'},
        custom_probabilities={}
    ),

    'paint': BreedPreset(
        name="Paint Horse",
        description="American breed - tobiano and overo patterns common",
        excluded_genes={'leopard', 'champagne'},
        custom_probabilities={
            'frame': 0.9,     # 19% frame (common in Paint)
            'splash': 0.9,    # Some splash
            'gray': 0.95,     # Less common
        }
    ),

    'appaloosa': BreedPreset(
        name="Appaloosa",
        description="American spotted breed - leopard patterns",
        excluded_genes={'frame'},
        custom_probabilities={
            'leopard': 0.3,   # 91% leopard (breed defining)
            'gray': 0.95,     # Uncommon
        }
    ),

    'quarter_horse': BreedPreset(
        name="Quarter Horse",
        description="American stock horse - solid colors, some roan",
        excluded_genes={'frame', 'splash', 'leopard', 'champagne'},
        custom_probabilities={
            'gray': 0.95,     # Uncommon
        }
    ),

    'icelandic': BreedPreset(
        name="Icelandic Horse",
        description="Nordic breed - all colors, minimal tobiano",
        excluded_genes={'frame', 'leopard'},
        custom_probabilities={
            'champagne': 0.98, # Very rare
            'gray': 0.8,       # Common
        }
    ),
}


# ============================================================================
# FANTASY BREED PRESETS
# ============================================================================

FANTASY_BREEDS = {
    'unicorn': BreedPreset(
        name="Unicorn",
        description="Magical - mostly white and gray, ethereal colors",
        excluded_genes={'leopard'},
        custom_probabilities={
            'gray': 0.6,            # 64% gray (ethereal)
            'splash': 0.8,          # Some splash
            'champagne': 0.9,       # Diluted colors
        }
    ),

    'shadow_steed': BreedPreset(
        name="Shadow Steed",
        description="Dark fantasy - blacks, grays, minimal white",
        excluded_genes={'kit', 'frame', 'splash', 'leopard', 'champagne'},
        custom_probabilities={
            'gray': 0.7,  # 51% gray (mysterious)
        }
    ),

    'wildfire': BreedPreset(
        name="Wildfire",
        description="Fiery colors - chestnuts, palominos, no grays/whites",
        excluded_genes={'gray', 'kit', 'frame', 'splash', 'leopard', 'champagne'},
        custom_probabilities={}
    ),

    'leopard_spirit': BreedPreset(
        name="Leopard Spirit",
        description="Spotted fantasy breed - all leopard patterns",
        excluded_genes={'frame', 'gray'},
        custom_probabilities={
            'leopard': 0.1,   # 99% leopard (breed defining)
            'champagne': 0.85, # Some dilution
        }
    ),

    'paint_splash': BreedPreset(
        name="Paint Splash",
        description="Maximum pinto - all white patterns combined",
        excluded_genes={'leopard'},
        custom_probabilities={
            'frame': 0.8,     # 36% frame
            'splash': 0.7,    # 51% splash
            'gray': 0.9,      # Some gray
        }
    ),
}


# ============================================================================
# PRESET MANAGER
# ============================================================================

class BreedPresetManager:
    """Manages breed presets and provides easy access."""

    def __init__(self):
        self.realistic = REALISTIC_BREEDS
        self.fantasy = FANTASY_BREEDS
        self.all_presets = {**REALISTIC_BREEDS, **FANTASY_BREEDS}

    def get_preset(self, breed_key: str) -> Optional[BreedPreset]:
        """Get a preset by key."""
        return self.all_presets.get(breed_key.lower())

    def get_realistic_breeds(self) -> Dict[str, BreedPreset]:
        """Get all realistic breed presets."""
        return self.realistic

    def get_fantasy_breeds(self) -> Dict[str, BreedPreset]:
        """Get all fantasy breed presets."""
        return self.fantasy

    def list_breeds(self, category: str = 'all') -> list:
        """
        List available breeds.

        Args:
            category: 'realistic', 'fantasy', or 'all'

        Returns:
            List of (key, BreedPreset) tuples
        """
        if category == 'realistic':
            return list(self.realistic.items())
        elif category == 'fantasy':
            return list(self.fantasy.items())
        else:
            return list(self.all_presets.items())


# Singleton instance
_preset_manager = None

def get_preset_manager() -> BreedPresetManager:
    """Get the global preset manager instance."""
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = BreedPresetManager()
    return _preset_manager
