"""Give command generation and validation."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from mc_commands.item import Item


class GiveTargets(BaseModel):
    """Validated entity selector for give command targets."""

    selector: str = Field(
        ...,
        description="Entity selector (e.g., @s, @a, @p, PlayerName, @a[distance=..10])",
    )

    @field_validator("selector")
    @classmethod
    def validate_selector(cls, v: str) -> str:
        """Validate entity selector format.

        Valid selectors:
        - Named player: PlayerName
        - Selector variables: @s, @a, @p, @r, @e
        - With modifiers: @a[distance=..10]
        """
        v = v.strip()

        # Check for named player (alphanumeric, underscores, hyphens)
        if v and not v.startswith("@"):
            if all(c.isalnum() or c in "_-" for c in v):
                return v
            raise ValueError(f"Invalid player name format: {v}")

        # Check for @ selector
        if v.startswith("@"):
            if len(v) < 2:
                raise ValueError("Selector must be @s, @a, @p, @r, or @e")

            selector_type = v[1]
            if selector_type not in "sapre":
                raise ValueError(
                    f"Invalid selector type @{selector_type}. "
                    "Must be @s, @a, @p, @r, or @e"
                )

            # If there are brackets, basic validation
            if "[" in v:
                if not v.endswith("]"):
                    raise ValueError("Selector brackets must be closed")

            return v

        raise ValueError(f"Invalid selector: {v}. Must be player name or @selector")


class GiveItem(BaseModel):
    """Validated item for give command.

    Can be a simple item name or item with NBT data.
    """

    item: Item = Field(..., description="Item to give")
    nbt: Optional[str] = Field(
        None,
        description="Optional NBT data (e.g., {Enchantments:[...]})",
    )

    @field_validator("nbt")
    @classmethod
    def validate_nbt(cls, v: Optional[str]) -> Optional[str]:
        """Basic NBT validation - must start with { and end with }."""
        if v is None:
            return None

        v = v.strip()
        if not v.startswith("{") or not v.endswith("}"):
            raise ValueError("NBT data must be enclosed in braces: {...}")

        return v


class GiveCount(BaseModel):
    """Validated count for give command."""

    count: int = Field(1, ge=1, description="Number of items to give (minimum 1)")


class GiveCommand(BaseModel):
    """Complete give command with all validated components."""

    targets: GiveTargets = Field(..., description="Entity selector(s)")
    item: GiveItem = Field(..., description="Item to give")
    count: GiveCount = Field(default_factory=GiveCount, description="Optional quantity")

    def to_command(self) -> str:
        """Generate the give command string.

        Returns:
            Valid /give command syntax (without leading /)
        """
        command = f"give {self.targets.selector} {self.item.item.name}"

        if self.item.nbt:
            command += self.item.nbt

        if self.count.count > 1:
            command += f" {self.count.count}"

        return command

    def __str__(self) -> str:
        """Return command with leading slash."""
        return f"/{self.to_command()}"
