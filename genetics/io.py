"""
I/O module - JSON export/import for game saves

This module provides utilities for saving and loading horses to/from JSON files.
Perfect for game projects that need to persist horse data between sessions.

Example usage:
    from genetics.horse import Horse
    from genetics.io import save_horses_to_json, load_horses_from_json

    # Create horses
    horses = [Horse.random() for _ in range(10)]

    # Save to file
    save_horses_to_json(horses, 'my_horses.json')

    # Load from file
    loaded_horses = load_horses_from_json('my_horses.json')
"""

import json
from typing import List, Dict, Any
from pathlib import Path


def save_horses_to_json(horses: List['Horse'], filename: str, pretty: bool = True) -> None:
    """
    Save horses to JSON file.

    Perfect for game save files - preserves all genetic information.

    Args:
        horses: List of Horse objects to save
        filename: Path to output JSON file
        pretty: If True, format JSON with indentation (default: True)

    Example:
        >>> from genetics.horse import Horse
        >>> from genetics.io import save_horses_to_json
        >>> horses = [Horse.random() for _ in range(5)]
        >>> save_horses_to_json(horses, 'stable.json')  # doctest: +SKIP
    """
    data = [horse.to_dict() for horse in horses]

    with open(filename, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)


def load_horses_from_json(filename: str) -> List['Horse']:
    """
    Load horses from JSON file.

    Reconstructs Horse objects with all genetic information intact.

    Args:
        filename: Path to JSON file containing horse data

    Returns:
        List of Horse objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON format is invalid

    Example:
        >>> from genetics.io import load_horses_from_json
        >>> horses = load_horses_from_json('stable.json')  # doctest: +SKIP
        >>> print(f"Loaded {len(horses)} horses")  # doctest: +SKIP
    """
    from genetics.horse import Horse

    with open(filename, 'r') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain a list of horses")

    horses = []
    for i, horse_data in enumerate(data):
        try:
            horse = Horse.from_dict(horse_data)
            horses.append(horse)
        except Exception as e:
            raise ValueError(f"Error loading horse at index {i}: {e}")

    return horses


def save_horse_to_json(horse: 'Horse', filename: str, pretty: bool = True) -> None:
    """
    Save a single horse to JSON file.

    Args:
        horse: Horse object to save
        filename: Path to output JSON file
        pretty: If True, format JSON with indentation (default: True)

    Example:
        >>> from genetics.horse import Horse
        >>> from genetics.io import save_horse_to_json
        >>> horse = Horse.random()
        >>> save_horse_to_json(horse, 'champion.json')  # doctest: +SKIP
    """
    save_horses_to_json([horse], filename, pretty)


def load_horse_from_json(filename: str) -> 'Horse':
    """
    Load a single horse from JSON file.

    Args:
        filename: Path to JSON file

    Returns:
        Horse object

    Raises:
        ValueError: If file contains multiple horses

    Example:
        >>> from genetics.io import load_horse_from_json
        >>> horse = load_horse_from_json('champion.json')  # doctest: +SKIP
    """
    horses = load_horses_from_json(filename)

    if len(horses) != 1:
        raise ValueError(
            f"Expected single horse in file, found {len(horses)}. "
            f"Use load_horses_from_json() for multiple horses."
        )

    return horses[0]


def export_breeding_records(
    records: List[Dict[str, Any]],
    filename: str,
    pretty: bool = True
) -> None:
    """
    Export breeding records to JSON.

    Useful for game projects that track breeding history.

    Args:
        records: List of breeding records, each with 'parent1', 'parent2', 'offspring'
        filename: Output JSON file
        pretty: Format with indentation

    Example:
        >>> from genetics.horse import Horse
        >>> from genetics.io import export_breeding_records
        >>>
        >>> mare = Horse.random()
        >>> stallion = Horse.random()
        >>> foal = Horse.breed(mare, stallion)
        >>>
        >>> records = [{
        ...     'parent1': mare.to_dict(),
        ...     'parent2': stallion.to_dict(),
        ...     'offspring': foal.to_dict(),
        ...     'date': '2024-01-15'
        ... }]
        >>> export_breeding_records(records, 'breedings.json')  # doctest: +SKIP
    """
    with open(filename, 'w') as f:
        if pretty:
            json.dump(records, f, indent=2)
        else:
            json.dump(records, f)


def import_breeding_records(filename: str) -> List[Dict[str, Any]]:
    """
    Import breeding records from JSON.

    Args:
        filename: JSON file with breeding records

    Returns:
        List of breeding record dictionaries

    Example:
        >>> from genetics.io import import_breeding_records
        >>> records = import_breeding_records('breedings.json')  # doctest: +SKIP
        >>> print(f"Found {len(records)} breeding records")  # doctest: +SKIP
    """
    with open(filename, 'r') as f:
        records = json.load(f)

    if not isinstance(records, list):
        raise ValueError("JSON file must contain a list of breeding records")

    return records


def horses_to_csv(horses: List['Horse'], filename: str, include_genotype: bool = True) -> None:
    """
    Export horses to CSV format.

    Useful for spreadsheet analysis or data visualization.

    Args:
        horses: List of Horse objects
        filename: Output CSV file
        include_genotype: If True, include full genotype string (default: True)

    Example:
        >>> from genetics.horse import Horse
        >>> from genetics.io import horses_to_csv
        >>> horses = [Horse.random() for _ in range(100)]
        >>> horses_to_csv(horses, 'horses.csv')  # doctest: +SKIP
    """
    import csv

    with open(filename, 'w', newline='') as f:
        fieldnames = ['phenotype']
        if include_genotype:
            fieldnames.append('genotype')

        # Add individual gene columns
        if horses:
            first_horse = horses[0]
            for gene_name in first_horse.genotype.keys():
                fieldnames.append(f'gene_{gene_name}')

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for horse in horses:
            row = {'phenotype': horse.phenotype}

            if include_genotype:
                row['genotype'] = horse.genotype_string

            # Add individual genes
            for gene_name, alleles in horse.genotype.items():
                row[f'gene_{gene_name}'] = '/'.join(alleles)

            writer.writerow(row)
