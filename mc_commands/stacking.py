"""Item stacking utilities for breaking quantities into stack-sized groups."""

from mc_commands.container import Container, ContainerItem
from mc_commands.give import GiveCommand, GiveCount, GiveItem
from mc_commands.item import Item
from mc_commands.target import NEAREST_PLAYER, Target


def break_into_stacks(items: list[tuple[Item, int]]) -> list[tuple[Item, int]]:
    """Break items into stacks respecting item stack sizes.

    Args:
        items: List of (Item, total_quantity) pairs where total_quantity is the
               desired total number of items.

    Returns:
        List of (Item, stack_count) pairs where each stack_count ≤ item.stack_size.
        The returned list contains one entry per stack, flattened across all input items.

    Raises:
        ValueError: If any quantity is ≤ 0.

    Example:
        >>> dirt = Item(id=3, name="dirt", display_name="Dirt", stack_size=64)
        >>> bucket = Item(id=325, name="bucket", display_name="Bucket", stack_size=16)
        >>> break_into_stacks([(dirt, 129), (bucket, 100)])
        [
            (dirt, 64), (dirt, 64), (dirt, 1),
            (bucket, 16), (bucket, 16), (bucket, 16),
            (bucket, 16), (bucket, 16), (bucket, 16),
            (bucket, 4)
        ]
    """
    result = []

    for item, quantity in items:
        if quantity <= 0:
            raise ValueError(
                f"Item quantity must be > 0, got {quantity} for {item.name}"
            )

        full_stacks, remainder = divmod(quantity, item.stack_size)

        for _ in range(full_stacks):
            result.append((item, item.stack_size))

        if remainder > 0:
            result.append((item, remainder))

    return result


def shulker_give(
    items: list[tuple[Item, int]], shulker_box: Item, target: Target = NEAREST_PLAYER
) -> GiveCommand:
    """Create a give command for a shulker box populated with items.

    Args:
        items: List of (Item, total_quantity) pairs to populate the shulker box.
               Quantities will be broken into stacks respecting item stack sizes.
        shulker_box: The shulker_box Item to give.
        target: Target selector for the give command (default: NEAREST_PLAYER/@p).

    Returns:
        GiveCommand that gives a shulker box with items inside.

    Raises:
        ValueError: If any item quantity is ≤ 0, target selector is invalid,
                    or items exceed shulker box capacity (27 slots).

    Example:
        >>> dirt = Item(id=3, name="dirt", display_name="Dirt", stack_size=64)
        >>> bucket = Item(id=325, name="bucket", display_name="Bucket", stack_size=16)
        >>> shulker_box = Item(id=454, name="shulker_box", display_name="Shulker Box", stack_size=1)
        >>> cmd = shulker_give([(dirt, 129), (bucket, 50)], shulker_box, target=NEAREST_PLAYER)
        >>> print(cmd)
        /give @p shulker_box[container=[...]]
    """
    # Break items into stacks
    stacked_items = break_into_stacks(items)

    # Validate that items fit in shulker box (27 slots)
    if len(stacked_items) > 27:
        raise ValueError(
            f"Items exceed shulker box capacity (27 slots): got {len(stacked_items)} stacks"
        )

    # Create ContainerItems with sequential slot assignment
    container_items = [
        ContainerItem(slot=slot, item_id=f"minecraft:{item.name}", count=count)
        for slot, (item, count) in enumerate(stacked_items)
    ]

    # Create Container and GiveCommand
    container = Container(items=container_items)
    give_item = GiveItem(item=shulker_box, components=container.to_component())
    give_command = GiveCommand(
        targets=target,
        item=give_item,
        count=GiveCount(count=1),
    )

    return give_command
