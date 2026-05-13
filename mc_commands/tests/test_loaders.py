"""Tests for minecraft-data loaders."""

import pytest

from mc_commands.item import Item
from mc_commands.loaders import get_item, load_items


class TestLoadItems:
    """Tests for load_items function."""

    def test_load_items_returns_dict(self):
        """load_items returns a dictionary of Item objects."""
        items = load_items()
        assert isinstance(items, dict)
        assert len(items) > 0

    def test_load_items_values_are_items(self):
        """All values in returned dict are Item objects."""
        items = load_items()
        for name, item in items.items():
            assert isinstance(item, Item)
            assert item.name == name

    def test_load_items_contains_common_items(self):
        """Loaded items include common Minecraft items."""
        items = load_items()
        common_items = ["diamond", "stick", "dirt", "stone"]
        for item_name in common_items:
            assert item_name in items

    def test_load_items_diamond_properties(self):
        """Diamond item has expected properties."""
        items = load_items()
        diamond = items["diamond"]
        assert diamond.name == "diamond"
        assert diamond.stack_size == 64
        assert diamond.display_name == "Diamond"

    def test_load_items_stick_properties(self):
        """Stick item has expected properties."""
        items = load_items()
        stick = items["stick"]
        assert stick.name == "stick"
        assert stick.stack_size == 64

    def test_load_items_egg_properties(self):
        """Egg item has expected properties."""
        items = load_items()
        egg = items["egg"]
        assert egg.name == "egg"
        assert egg.stack_size == 16

    def test_load_items_unsupportable_version(self):
        """load_items raises ValueError for unsupported version."""
        with pytest.raises(ValueError):
            load_items(version="0.0.0")


class TestGetItem:
    """Tests for get_item function."""

    def test_get_item_returns_item(self):
        """get_item returns an Item object."""
        item = get_item("diamond")
        assert isinstance(item, Item)
        assert item.name == "diamond"

    def test_get_item_diamond(self):
        """Can retrieve diamond item."""
        diamond = get_item("diamond")
        assert diamond.name == "diamond"
        assert diamond.stack_size == 64
        assert diamond.display_name == "Diamond"

    def test_get_item_stick(self):
        """Can retrieve stick item."""
        stick = get_item("stick")
        assert stick.name == "stick"
        assert stick.stack_size == 64

    def test_get_item_egg(self):
        """Can retrieve egg item."""
        egg = get_item("egg")
        assert egg.name == "egg"
        assert egg.stack_size == 16

    def test_get_item_leather_boots(self):
        """Can retrieve leather_boots item (stack_size=1)."""
        boots = get_item("leather_boots")
        assert boots.name == "leather_boots"
        assert boots.stack_size == 1

    def test_get_item_nonexistent(self):
        """get_item raises KeyError for nonexistent item."""
        with pytest.raises(KeyError):
            get_item("nonexistent_item_xyz_123")

    def test_get_item_unsupported_version(self):
        """get_item raises ValueError for unsupported version."""
        with pytest.raises(ValueError):
            get_item("diamond", version="0.0.0")
