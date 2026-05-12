"""Container item models for Minecraft commands."""

from pydantic import BaseModel, Field, field_validator


class ContainerItem(BaseModel):
    """A single item in a container."""

    slot: int = Field(
        ..., ge=0, le=26, description="Container slot (0-26 for shulker boxes)"
    )
    item_id: str = Field(..., description="Item ID (e.g., 'minecraft:dirt')")
    count: int = Field(1, ge=1, le=64, description="Item count (1-64)")

    @field_validator("item_id")
    @classmethod
    def validate_item_id(cls, v: str) -> str:
        """Validate item ID format."""
        v = v.strip()
        if not v or ":" not in v:
            raise ValueError(
                "Item ID must be in format 'namespace:name' (e.g., 'minecraft:dirt')"
            )
        return v


class Container(BaseModel):
    """Container component for holding items (shulker boxes, chests, etc.)."""

    items: list[ContainerItem] = Field(
        ..., description="List of items in the container"
    )

    def to_component(self) -> str:
        """Generate the container component string.

        Returns:
            Component string like: [container=[{slot:0,item:{id:"minecraft:dirt",count:64}}, ...]]
        """
        items_str = ",".join(
            f'{{slot:{item.slot},item:{{id:"{item.item_id}",count:{item.count}}}}}'
            for item in self.items
        )
        return f"[container=[{items_str}]]"
