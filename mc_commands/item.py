"""Item data models for Minecraft command generation."""

from pydantic import BaseModel, ConfigDict, Field


class Item(BaseModel):
    """Represents a Minecraft item.

    Attributes:
        id: Numeric item ID
        name: Canonical item name (e.g., 'diamond', 'oak_log')
        display_name: Human-readable item name (e.g., 'Diamond')
        stack_size: Maximum number of items in a stack (1-64)
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(..., description="Numeric item ID")
    name: str = Field(..., description="Canonical item name")
    display_name: str = Field(
        ..., alias="displayName", description="Human-readable item name"
    )
    stack_size: int = Field(
        ...,
        alias="stackSize",
        ge=1,
        le=64,
        description="Maximum stack size",
    )
