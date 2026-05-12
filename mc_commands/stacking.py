"""Item stacking utilities for breaking quantities into stack-sized groups."""

from mc_commands.item import Item


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
