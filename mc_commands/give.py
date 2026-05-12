"""Give command generation and validation."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from mc_commands.item import Item
from mc_commands.target import Target


class GiveItem(BaseModel):
    """Validated item for give command.

    Can be a simple item name or item with data components.
    """

    item: Item = Field(..., description="Item to give")
    components: Optional[str] = Field(
        None,
        description="Optional data components (e.g., [enchantments={...}])",
    )

    @field_validator("components")
    @classmethod
    def validate_components(cls, v: Optional[str]) -> Optional[str]:
        """Validate data component syntax - must start with [ and end with ]."""
        if v is None:
            return None

        v = v.strip()
        if not v.startswith("[") or not v.endswith("]"):
            raise ValueError("Data components must be enclosed in brackets: [...]")

        return v


class GiveCount(BaseModel):
    """Validated count for give command."""

    count: int = Field(1, ge=1, description="Number of items to give (minimum 1)")


class GiveCommand(BaseModel):
    """Complete give command with all validated components."""

    targets: Target = Field(..., description="Entity selector")
    item: GiveItem = Field(..., description="Item to give")
    count: GiveCount = Field(default_factory=GiveCount, description="Optional quantity")

    def to_command(self) -> str:
        """Generate the give command string.

        Returns:
            Valid /give command syntax (without leading /)
        """
        command = f"give {self.targets} {self.item.item.name}"

        if self.item.components:
            command += self.item.components

        if self.count.count > 1:
            command += f" {self.count.count}"

        return command

    def __str__(self) -> str:
        """Return command with leading slash."""
        return f"/{self.to_command()}"
