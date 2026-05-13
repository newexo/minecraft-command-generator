"""Load Minecraft data from minecraft-data package."""

import json
import os

from mc_commands.item import Item


def load_items(version: str = "1.21.6") -> dict[str, Item]:
    """Load all items for a Minecraft version.

    Args:
        version: Minecraft version (e.g., '1.21.6')

    Returns:
        Dictionary mapping item names to Item objects

    Raises:
        ValueError: If version is not supported by minecraft-data
        FileNotFoundError: If items.json not available for version
    """
    from minecraft_data.data import get_data_path

    data_dir = get_data_path(version)
    items_file = os.path.join(data_dir, "pc", version, "items.json")

    if not os.path.isfile(items_file):
        raise FileNotFoundError(f"items.json not available for version {version}")

    with open(items_file) as f:
        items_data = json.load(f)

    return {item["name"]: Item(**item) for item in items_data}


def get_item(name: str, version: str = "1.21.6") -> Item:
    """Get a single item by name.

    Args:
        name: Item name (e.g., 'diamond', 'stick')
        version: Minecraft version

    Returns:
        Item object

    Raises:
        ValueError: If version is not supported by minecraft-data
        FileNotFoundError: If items.json not available for version
        KeyError: If item name not found in version data
    """
    items = load_items(version)
    return items[name]
