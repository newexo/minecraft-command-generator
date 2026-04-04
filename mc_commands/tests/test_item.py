"""Tests for Item model."""

import json
import os

import pytest
from pydantic import ValidationError

from mc_commands.item import Item


def load_minecraft_items(version="1.19.2"):
    """Load items from minecraft-data for a specific version.

    Args:
        version: Minecraft version (e.g., '1.19.2')

    Returns:
        Dictionary of items loaded from minecraft-data
    """
    import minecraft_data

    package_dir = os.path.dirname(minecraft_data.__file__)
    pc_dir = os.path.join(package_dir, "data", "data", "pc")

    items_file = os.path.join(pc_dir, version, "items.json")
    with open(items_file) as f:
        items = json.load(f)

    return {item["name"]: item for item in items}


@pytest.fixture
def minecraft_items():
    """Fixture providing minecraft-data items."""
    return load_minecraft_items()


class TestItem:
    """Tests for the Item model."""

    def test_create_item_with_snake_case_fields(self):
        """Create an item using snake_case field names."""
        item = Item(id=264, name="diamond", display_name="Diamond", stack_size=64)

        assert item.id == 264
        assert item.name == "diamond"
        assert item.display_name == "Diamond"
        assert item.stack_size == 64

    def test_create_item_with_minecraft_data_aliases(self):
        """Create an item from minecraft-data using camelCase aliases."""
        data = {
            "id": 264,
            "name": "diamond",
            "displayName": "Diamond",
            "stackSize": 64,
        }
        item = Item(**data)

        assert item.id == 264
        assert item.name == "diamond"
        assert item.display_name == "Diamond"
        assert item.stack_size == 64

    def test_stick_from_real_data(self, minecraft_items):
        """Load stick item from real minecraft-data."""
        stick_data = minecraft_items["stick"]
        item = Item(**stick_data)

        assert item.name == "stick"
        assert item.stack_size == 64
        assert item.display_name == "Stick"

    def test_egg_from_real_data(self, minecraft_items):
        """Load egg item from real minecraft-data."""
        egg_data = minecraft_items["egg"]
        item = Item(**egg_data)

        assert item.name == "egg"
        assert item.stack_size == 16
        assert item.display_name == "Egg"

    def test_leather_boots_from_real_data(self, minecraft_items):
        """Load leather boots from real minecraft-data."""
        boots_data = minecraft_items["leather_boots"]
        item = Item(**boots_data)

        assert item.name == "leather_boots"
        assert item.stack_size == 1
        assert item.display_name == "Leather Boots"

    def test_stack_size_below_min(self):
        """Stack size of 0 raises ValidationError."""
        with pytest.raises(ValidationError):
            Item(id=1, name="test", display_name="Test", stack_size=0)

    def test_stack_size_above_max(self):
        """Stack size of 65 raises ValidationError."""
        with pytest.raises(ValidationError):
            Item(id=1, name="test", display_name="Test", stack_size=65)

    def test_missing_required_field(self):
        """Missing required field raises ValidationError."""
        with pytest.raises(ValidationError):
            Item(id=1, name="test", display_name="Test")
