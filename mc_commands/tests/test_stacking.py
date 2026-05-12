"""Tests for item stacking utilities."""

import pytest

from mc_commands.give import GiveCommand
from mc_commands.item import Item
from mc_commands.stacking import break_into_stacks, shulker_give
from mc_commands.target import Target, NEAREST_PLAYER, SELF


class TestBreakIntoStacks:
    """Tests for break_into_stacks function."""

    @pytest.fixture
    def dirt(self):
        """Item with stack_size=64."""
        return Item(id=3, name="dirt", display_name="Dirt", stack_size=64)

    @pytest.fixture
    def bucket(self):
        """Item with stack_size=16."""
        return Item(id=325, name="bucket", display_name="Bucket", stack_size=16)

    @pytest.fixture
    def potion(self):
        """Item with stack_size=1."""
        return Item(id=373, name="potion", display_name="Potion", stack_size=1)

    def test_single_full_stack(self, dirt):
        """Single item exactly fills one stack."""
        result = break_into_stacks([(dirt, 64)])
        assert result == [(dirt, 64)]

    def test_single_partial_stack(self, dirt):
        """Single item partially fills one stack."""
        result = break_into_stacks([(dirt, 32)])
        assert result == [(dirt, 32)]

    def test_multiple_full_stacks(self, dirt):
        """Multiple full stacks with no remainder."""
        result = break_into_stacks([(dirt, 128)])
        assert result == [(dirt, 64), (dirt, 64)]

    def test_full_stacks_with_remainder(self, dirt):
        """Multiple full stacks with remainder."""
        result = break_into_stacks([(dirt, 129)])
        assert result == [(dirt, 64), (dirt, 64), (dirt, 1)]

    def test_small_stack_size(self, bucket):
        """Item with small stack_size=16."""
        result = break_into_stacks([(bucket, 100)])
        expected = [
            (bucket, 16),
            (bucket, 16),
            (bucket, 16),
            (bucket, 16),
            (bucket, 16),
            (bucket, 16),
            (bucket, 4),
        ]
        assert result == expected

    def test_stack_size_one(self, potion):
        """Item with stack_size=1 (potions)."""
        result = break_into_stacks([(potion, 5)])
        assert result == [
            (potion, 1),
            (potion, 1),
            (potion, 1),
            (potion, 1),
            (potion, 1),
        ]

    def test_multiple_items(self, dirt, bucket):
        """Multiple different items in one call."""
        result = break_into_stacks([(dirt, 129), (bucket, 50)])
        expected = [
            (dirt, 64),
            (dirt, 64),
            (dirt, 1),
            (bucket, 16),
            (bucket, 16),
            (bucket, 16),
            (bucket, 2),
        ]
        assert result == expected

    def test_multiple_items_mixed_order(self, dirt, bucket, potion):
        """Multiple items with different stack sizes."""
        result = break_into_stacks([(potion, 3), (bucket, 32), (dirt, 65)])
        expected = [
            (potion, 1),
            (potion, 1),
            (potion, 1),
            (bucket, 16),
            (bucket, 16),
            (dirt, 64),
            (dirt, 1),
        ]
        assert result == expected

    def test_empty_list(self):
        """Empty input returns empty output."""
        result = break_into_stacks([])
        assert result == []

    def test_quantity_zero_raises_error(self, dirt):
        """Quantity of 0 raises ValueError."""
        with pytest.raises(ValueError, match="quantity must be > 0"):
            break_into_stacks([(dirt, 0)])

    def test_negative_quantity_raises_error(self, dirt):
        """Negative quantity raises ValueError."""
        with pytest.raises(ValueError, match="quantity must be > 0"):
            break_into_stacks([(dirt, -5)])

    def test_error_message_includes_item_name(self, dirt):
        """Error message includes the item name."""
        with pytest.raises(ValueError, match="dirt"):
            break_into_stacks([(dirt, -1)])

    def test_first_invalid_item_raises_error(self, dirt, bucket):
        """Error raised on first invalid item."""
        with pytest.raises(ValueError):
            break_into_stacks([(dirt, 50), (bucket, 0)])

    def test_quantity_one(self, dirt):
        """Quantity of 1 returns single item."""
        result = break_into_stacks([(dirt, 1)])
        assert result == [(dirt, 1)]

    def test_large_quantity(self, dirt):
        """Large quantity is broken correctly."""
        result = break_into_stacks([(dirt, 1000)])
        assert len(result) == 16  # 15 full stacks of 64 + 1 remainder of 40
        assert result[0] == (dirt, 64)
        assert result[-1] == (dirt, 40)
        assert sum(count for _, count in result) == 1000


class TestShulkerGive:
    """Tests for shulker_give function."""

    @pytest.fixture
    def dirt(self):
        """Item with stack_size=64."""
        return Item(id=3, name="dirt", display_name="Dirt", stack_size=64)

    @pytest.fixture
    def bucket(self):
        """Item with stack_size=16."""
        return Item(id=325, name="bucket", display_name="Bucket", stack_size=16)

    @pytest.fixture
    def shulker_box(self):
        """Shulker box item."""
        return Item(
            id=454, name="shulker_box", display_name="Shulker Box", stack_size=1
        )

    def test_simple_shulker_give(self, dirt, shulker_box):
        """Create shulker box with single item."""
        cmd = shulker_give([(dirt, 64)], shulker_box, target=NEAREST_PLAYER)
        assert isinstance(cmd, GiveCommand)
        assert cmd.targets.selector == "@p"
        assert cmd.item.item.name == "shulker_box"
        assert "container=" in cmd.item.components
        assert str(cmd).startswith("/give @p shulker_box")

    def test_multiple_items_in_shulker(self, dirt, bucket, shulker_box):
        """Create shulker box with multiple different items."""
        cmd = shulker_give([(dirt, 65), (bucket, 50)], shulker_box, target=SELF)
        assert cmd.targets.selector == "@s"
        # Should have: 2 stacks of dirt (64+1) + 4 stacks of bucket (16+16+16+2) = 6 stacks total
        assert "slot:0" in cmd.item.components
        assert "slot:5" in cmd.item.components
        assert "minecraft:dirt" in cmd.item.components
        assert "minecraft:bucket" in cmd.item.components

    def test_shulker_default_target(self, dirt, shulker_box):
        """Default target is @p."""
        cmd = shulker_give([(dirt, 32)], shulker_box)
        assert cmd.targets.selector == "@p"

    def test_shulker_named_player(self, dirt, shulker_box):
        """Target can be a player name."""
        cmd = shulker_give(
            [(dirt, 32)], shulker_box, target=Target(selector="PlayerName")
        )
        assert cmd.targets.selector == "PlayerName"

    def test_shulker_with_selector_modifiers(self, dirt, shulker_box):
        """Target can include selector modifiers."""
        cmd = shulker_give(
            [(dirt, 32)], shulker_box, target=Target(selector="@a[gamemode=survival]")
        )
        assert cmd.targets.selector == "@a[gamemode=survival]"

    def test_shulker_count_always_one(self, dirt, shulker_box):
        """Shulker box count is always 1 (can't stack shulker boxes)."""
        cmd = shulker_give([(dirt, 32)], shulker_box)
        assert cmd.count.count == 1

    def test_shulker_exceeds_capacity(self, dirt, shulker_box):
        """Raises error if items exceed 27 slot capacity."""
        # 28 stacks of single items would exceed capacity
        items = [(dirt, i) for i in range(1, 29)]  # 28 items
        with pytest.raises(ValueError, match="exceed shulker box capacity"):
            shulker_give(items, shulker_box)

    def test_shulker_at_capacity(self, dirt, bucket, shulker_box):
        """Items exactly filling 27 slots is OK."""
        # 20 stacks of dirt (64*20 = 1280) + 7 stacks of bucket (16*7 = 112) = 27 stacks
        cmd = shulker_give([(dirt, 1280), (bucket, 112)], shulker_box)
        assert isinstance(cmd, GiveCommand)
        # Verify slots go from 0 to 26
        assert "slot:0" in cmd.item.components
        assert "slot:26" in cmd.item.components
        assert "slot:27" not in cmd.item.components

    def test_shulker_invalid_quantity_raises_error(self, dirt, shulker_box):
        """Invalid item quantities raise error."""
        with pytest.raises(ValueError, match="quantity must be > 0"):
            shulker_give([(dirt, 0)], shulker_box)

    def test_shulker_empty_items_list(self, shulker_box):
        """Empty items list creates empty shulker box."""
        cmd = shulker_give([], shulker_box)
        assert isinstance(cmd, GiveCommand)
        assert "container=[]" in cmd.item.components
