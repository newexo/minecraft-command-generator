"""Tests for container models."""

import pytest
from pydantic import ValidationError

from mc_commands.container import Container, ContainerItem


class TestContainerItem:
    """Tests for container item validation."""

    def test_valid_container_item(self):
        """Valid container item."""
        item = ContainerItem(slot=0, item_id="minecraft:dirt", count=64)
        assert item.slot == 0
        assert item.item_id == "minecraft:dirt"
        assert item.count == 64

    def test_default_count(self):
        """Default count is 1."""
        item = ContainerItem(slot=5, item_id="minecraft:glass")
        assert item.count == 1

    def test_slot_range_valid(self):
        """Slot 0-26 is valid."""
        item_min = ContainerItem(slot=0, item_id="minecraft:dirt")
        item_max = ContainerItem(slot=26, item_id="minecraft:dirt")
        assert item_min.slot == 0
        assert item_max.slot == 26

    def test_slot_negative_invalid(self):
        """Negative slot is invalid."""
        with pytest.raises(ValidationError):
            ContainerItem(slot=-1, item_id="minecraft:dirt")

    def test_slot_too_high_invalid(self):
        """Slot > 26 is invalid."""
        with pytest.raises(ValidationError):
            ContainerItem(slot=27, item_id="minecraft:dirt")

    def test_count_range_valid(self):
        """Count 1-64 is valid."""
        item_min = ContainerItem(slot=0, item_id="minecraft:dirt", count=1)
        item_max = ContainerItem(slot=0, item_id="minecraft:dirt", count=64)
        assert item_min.count == 1
        assert item_max.count == 64

    def test_count_zero_invalid(self):
        """Count of 0 is invalid."""
        with pytest.raises(ValidationError):
            ContainerItem(slot=0, item_id="minecraft:dirt", count=0)

    def test_count_too_high_invalid(self):
        """Count > 64 is invalid."""
        with pytest.raises(ValidationError):
            ContainerItem(slot=0, item_id="minecraft:dirt", count=65)

    def test_item_id_format_required(self):
        """Item ID must have namespace:name format."""
        with pytest.raises(ValidationError):
            ContainerItem(slot=0, item_id="dirt")

    def test_item_id_whitespace_stripped(self):
        """Item ID whitespace is stripped."""
        item = ContainerItem(slot=0, item_id="  minecraft:dirt  ")
        assert item.item_id == "minecraft:dirt"


class TestContainer:
    """Tests for container component."""

    def test_single_item_container(self):
        """Container with single item."""
        container = Container(
            items=[ContainerItem(slot=0, item_id="minecraft:dirt", count=64)]
        )
        assert len(container.items) == 1
        assert (
            container.to_component()
            == '[container=[{slot:0,item:{id:"minecraft:dirt",count:64}}]]'
        )

    def test_multiple_items_container(self):
        """Container with multiple items."""
        container = Container(
            items=[
                ContainerItem(slot=0, item_id="minecraft:dirt", count=64),
                ContainerItem(slot=1, item_id="minecraft:glass", count=64),
            ]
        )
        assert len(container.items) == 2
        expected = '[container=[{slot:0,item:{id:"minecraft:dirt",count:64}},{slot:1,item:{id:"minecraft:glass",count:64}}]]'
        assert container.to_component() == expected

    def test_container_with_different_counts(self):
        """Container items can have different counts."""
        container = Container(
            items=[
                ContainerItem(slot=0, item_id="minecraft:dirt", count=32),
                ContainerItem(slot=1, item_id="minecraft:glass", count=1),
            ]
        )
        component = container.to_component()
        assert "count:32" in component
        assert "count:1" in component

    def test_shulker_box_example(self):
        """Shulker box with dirt and sand."""
        container = Container(
            items=[
                ContainerItem(slot=0, item_id="minecraft:dirt", count=64),
                ContainerItem(slot=1, item_id="minecraft:sand", count=64),
            ]
        )
        expected = '[container=[{slot:0,item:{id:"minecraft:dirt",count:64}},{slot:1,item:{id:"minecraft:sand",count:64}}]]'
        assert container.to_component() == expected

    def test_empty_container(self):
        """Empty container is valid."""
        container = Container(items=[])
        assert len(container.items) == 0
        assert container.to_component() == "[container=[]]"
