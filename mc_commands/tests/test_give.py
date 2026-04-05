"""Tests for give command generation."""

import pytest
from pydantic import ValidationError

from mc_commands.give import GiveCommand, GiveCount, GiveItem, GiveTargets
from mc_commands.item import Item


class TestGiveTargets:
    """Tests for entity selector validation."""

    def test_selector_at_s(self):
        """@s (self) is valid."""
        targets = GiveTargets(selector="@s")
        assert targets.selector == "@s"

    def test_selector_at_a(self):
        """@a (all players) is valid."""
        targets = GiveTargets(selector="@a")
        assert targets.selector == "@a"

    def test_selector_at_p(self):
        """@p (nearest player) is valid."""
        targets = GiveTargets(selector="@p")
        assert targets.selector == "@p"

    def test_selector_at_r(self):
        """@r (random player) is valid."""
        targets = GiveTargets(selector="@r")
        assert targets.selector == "@r"

    def test_selector_at_e(self):
        """@e (all entities) is valid."""
        targets = GiveTargets(selector="@e")
        assert targets.selector == "@e"

    def test_selector_with_modifiers(self):
        """Selector with brackets is valid."""
        targets = GiveTargets(selector="@a[distance=..10]")
        assert targets.selector == "@a[distance=..10]"

    def test_player_name(self):
        """Player name is valid."""
        targets = GiveTargets(selector="PlayerName")
        assert targets.selector == "PlayerName"

    def test_player_name_with_underscore(self):
        """Player name with underscore is valid."""
        targets = GiveTargets(selector="Player_123")
        assert targets.selector == "Player_123"

    def test_player_name_with_hyphen(self):
        """Player name with hyphen is valid."""
        targets = GiveTargets(selector="Player-Name")
        assert targets.selector == "Player-Name"

    def test_invalid_selector_type(self):
        """Invalid @ selector raises error."""
        with pytest.raises(ValidationError):
            GiveTargets(selector="@x")

    def test_unclosed_brackets(self):
        """Unclosed brackets raise error."""
        with pytest.raises(ValidationError):
            GiveTargets(selector="@a[distance=..10")

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        targets = GiveTargets(selector="  @s  ")
        assert targets.selector == "@s"


class TestGiveItem:
    """Tests for item validation."""

    def test_simple_item(self):
        """Simple item name is valid."""
        item = GiveItem(
            item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
        )
        assert item.item.name == "diamond"
        assert item.nbt is None

    def test_item_with_nbt(self):
        """Item with NBT data is valid."""
        item = GiveItem(
            item=Item(
                id=268, name="wooden_sword", display_name="Wooden Sword", stack_size=1
            ),
            nbt='{Enchantments:[{id:"minecraft:sharpness",lvl:5}]}',
        )
        assert item.nbt is not None
        assert "Enchantments" in item.nbt

    def test_invalid_nbt_missing_braces(self):
        """NBT without braces raises error."""
        with pytest.raises(ValidationError):
            GiveItem(
                item=Item(
                    id=268,
                    name="wooden_sword",
                    display_name="Wooden Sword",
                    stack_size=1,
                ),
                nbt="Enchantments:[...]",
            )

    def test_invalid_nbt_unclosed_brace(self):
        """Unclosed brace raises error."""
        with pytest.raises(ValidationError):
            GiveItem(
                item=Item(
                    id=268,
                    name="wooden_sword",
                    display_name="Wooden Sword",
                    stack_size=1,
                ),
                nbt="{Enchantments:[...]",
            )


class TestGiveCount:
    """Tests for count validation."""

    def test_default_count(self):
        """Default count is 1."""
        count = GiveCount()
        assert count.count == 1

    def test_count_one(self):
        """Count of 1 is valid."""
        count = GiveCount(count=1)
        assert count.count == 1

    def test_count_multiple(self):
        """Count > 1 is valid."""
        count = GiveCount(count=64)
        assert count.count == 64

    def test_count_zero_invalid(self):
        """Count of 0 is invalid."""
        with pytest.raises(ValidationError):
            GiveCount(count=0)

    def test_count_negative_invalid(self):
        """Negative count is invalid."""
        with pytest.raises(ValidationError):
            GiveCount(count=-5)


class TestGiveCommand:
    """Tests for complete give command generation."""

    def test_simple_give_command(self):
        """Simple give command with minimal args."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@s"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=1),
        )
        assert str(cmd) == "/give @s diamond"

    def test_give_command_with_count(self):
        """Give command with explicit count."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@a"),
            item=GiveItem(
                item=Item(id=1, name="stone", display_name="Stone", stack_size=64)
            ),
            count=GiveCount(count=32),
        )
        assert str(cmd) == "/give @a stone 32"

    def test_give_command_with_nbt(self):
        """Give command with NBT data."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@s"),
            item=GiveItem(
                item=Item(
                    id=268,
                    name="wooden_sword",
                    display_name="Wooden Sword",
                    stack_size=1,
                ),
                nbt="{Enchantments:[]}",
            ),
            count=GiveCount(count=1),
        )
        assert str(cmd) == "/give @s wooden_sword{Enchantments:[]}"

    def test_give_command_to_command(self):
        """to_command returns without leading slash."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@s"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
        )
        assert cmd.to_command() == "give @s diamond"
        assert str(cmd) == "/give @s diamond"

    def test_give_command_player_name(self):
        """Give command to named player."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="PlayerName"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=5),
        )
        assert str(cmd) == "/give PlayerName diamond 5"

    def test_give_command_with_selector_modifiers(self):
        """Give command with selector modifiers."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@a[gamemode=survival]"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=10),
        )
        assert str(cmd) == "/give @a[gamemode=survival] diamond 10"

    def test_count_one_omitted(self):
        """Count of 1 is omitted from command."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@s"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=1),
        )
        # Count should not appear when it's 1
        assert " 1" not in str(cmd)
        assert str(cmd) == "/give @s diamond"

    def test_count_greater_than_one_included(self):
        """Count > 1 is included in command."""
        cmd = GiveCommand(
            targets=GiveTargets(selector="@s"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=2),
        )
        assert " 2" in str(cmd)
        assert str(cmd) == "/give @s diamond 2"
