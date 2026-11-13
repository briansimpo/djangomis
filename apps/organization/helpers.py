from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from .models import OrgUnit


def build_org_tree(queryset: QuerySet[OrgUnit] | None = None) -> list[OrgUnit]:
    """
    Build a hierarchical organization tree.

    Each OrgUnit receives a transient `tree_children` attribute.
    Returns only root organizational units.
    """

    queryset = queryset or OrgUnit.objects.all()

    units = list(
        queryset.select_related("type").order_by("level", "name")
    )

    nodes: dict[Any, OrgUnit] = {}

    for unit in units:
        unit.tree_children = []
        nodes[unit.pk] = unit

    roots: list[OrgUnit] = []

    for unit in units:
        parent = nodes.get(unit.parent_id)

        if parent is None:
            roots.append(unit)
        else:
            parent.tree_children.append(unit)

    return roots