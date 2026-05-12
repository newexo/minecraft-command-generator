"""Tests for give command generation."""

import pytest
from pydantic import ValidationError

from mc_commands.container import Container, ContainerItem
from mc_commands.give import GiveCommand, GiveCount, GiveItem
from mc_commands.item import Item
from mc_commands.target import Target, SELF, ALL_PLAYERS, NEAREST_PLAYER


class TestTargetValidation:
    """Tests for Target selector validation logic."""

    def test_selector_with_modifiers(self):
        """Selector with brackets is valid."""
        target = Target(selector="@a[distance=..10]")
        assert target.selector == "@a[distance=..10]"

    def test_player_name(self):
        """Player name is valid."""
        target = Target(selector="PlayerName")
        assert target.selector == "PlayerName"

    def test_player_name_with_underscore(self):
        """Player name with underscore is valid."""
        target = Target(selector="Player_123")
        assert target.selector == "Player_123"

    def test_player_name_with_hyphen(self):
        """Player name with hyphen is valid."""
        target = Target(selector="Player-Name")
        assert target.selector == "Player-Name"

    def test_invalid_selector_type(self):
        """Invalid @ selector raises error."""
        with pytest.raises(ValidationError):
            Target(selector="@x")

    def test_unclosed_brackets(self):
        """Unclosed brackets raise error."""
        with pytest.raises(ValidationError):
            Target(selector="@a[distance=..10")

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        target = Target(selector="  @s  ")
        assert target.selector == "@s"


class TestGiveItem:
    """Tests for item validation."""

    def test_simple_item(self):
        """Simple item name is valid."""
        item = GiveItem(
            item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
        )
        assert item.item.name == "diamond"
        assert item.components is None

    def test_item_with_components(self):
        """Item with data components is valid."""
        item = GiveItem(
            item=Item(
                id=268, name="wooden_sword", display_name="Wooden Sword", stack_size=1
            ),
            components='[enchantments={"minecraft:sharpness":5}]',
        )
        assert item.components is not None
        assert "enchantments" in item.components

    def test_invalid_components_missing_brackets(self):
        """Data components without brackets raises error."""
        with pytest.raises(ValidationError):
            GiveItem(
                item=Item(
                    id=268,
                    name="wooden_sword",
                    display_name="Wooden Sword",
                    stack_size=1,
                ),
                components="enchantments={...}",
            )

    def test_invalid_components_unclosed_bracket(self):
        """Unclosed bracket raises error."""
        with pytest.raises(ValidationError):
            GiveItem(
                item=Item(
                    id=268,
                    name="wooden_sword",
                    display_name="Wooden Sword",
                    stack_size=1,
                ),
                components="[enchantments={...}",
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
            targets=SELF,
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=1),
        )
        assert str(cmd) == "/give @s diamond"

    def test_give_command_with_count(self):
        """Give command with explicit count."""
        cmd = GiveCommand(
            targets=ALL_PLAYERS,
            item=GiveItem(
                item=Item(id=1, name="stone", display_name="Stone", stack_size=64)
            ),
            count=GiveCount(count=32),
        )
        assert str(cmd) == "/give @a stone 32"

    def test_give_command_with_components(self):
        """Give command with data components."""
        cmd = GiveCommand(
            targets=SELF,
            item=GiveItem(
                item=Item(
                    id=268,
                    name="wooden_sword",
                    display_name="Wooden Sword",
                    stack_size=1,
                ),
                components="[enchantments={}]",
            ),
            count=GiveCount(count=1),
        )
        assert str(cmd) == "/give @s wooden_sword[enchantments={}]"

    def test_give_command_to_command(self):
        """to_command returns without leading slash."""
        cmd = GiveCommand(
            targets=SELF,
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
        )
        assert cmd.to_command() == "give @s diamond"
        assert str(cmd) == "/give @s diamond"

    def test_give_command_player_name(self):
        """Give command to named player."""
        cmd = GiveCommand(
            targets=Target(selector="PlayerName"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=5),
        )
        assert str(cmd) == "/give PlayerName diamond 5"

    def test_give_command_with_selector_modifiers(self):
        """Give command with selector modifiers."""
        cmd = GiveCommand(
            targets=Target(selector="@a[gamemode=survival]"),
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=10),
        )
        assert str(cmd) == "/give @a[gamemode=survival] diamond 10"

    def test_count_one_omitted(self):
        """Count of 1 is omitted from command."""
        cmd = GiveCommand(
            targets=SELF,
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
            targets=SELF,
            item=GiveItem(
                item=Item(id=264, name="diamond", display_name="Diamond", stack_size=64)
            ),
            count=GiveCount(count=2),
        )
        assert " 2" in str(cmd)
        assert str(cmd) == "/give @s diamond 2"

    def test_shulker_box_with_dirt_and_glass(self):
        """Give shulker box containing dirt and glass."""
        container = Container(
            items=[
                ContainerItem(slot=0, item_id="minecraft:dirt", count=64),
                ContainerItem(slot=1, item_id="minecraft:glass", count=64),
            ]
        )
        cmd = GiveCommand(
            targets=NEAREST_PLAYER,
            item=GiveItem(
                item=Item(
                    id=454,
                    name="shulker_box",
                    display_name="Shulker Box",
                    stack_size=1,
                ),
                components=container.to_component(),
            ),
        )
        expected = '/give @p shulker_box[container=[{slot:0,item:{id:"minecraft:dirt",count:64}},{slot:1,item:{id:"minecraft:glass",count:64}}]]'
        assert str(cmd) == expected
