"""Minecraft entity selectors (targets) for commands."""

from pydantic import BaseModel, Field, field_validator


class Target(BaseModel):
    """Validated Minecraft entity selector for command targets.

    Represents a target entity or player for commands like /give, /summon, etc.
    """

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

    def __str__(self) -> str:
        """Return selector string for use in commands."""
        return self.selector


# Common target constants
NEAREST_PLAYER = Target(selector="@p")
SELF = Target(selector="@s")
ALL_PLAYERS = Target(selector="@a")
RANDOM_PLAYER = Target(selector="@r")
ALL_ENTITIES = Target(selector="@e")
