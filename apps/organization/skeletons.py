from djangospice.html.skeleton import Skeleton
from djangospice.utils import get_template_name
from .apps import namespace


class OrgStructureSkeleton(Skeleton):
    template_name = get_template_name(
        "skeletons/org_structure.html",
        namespace,
    )

    def __init__(self, rows=8, max_depth=3, **kwargs):
        self.rows = rows
        self.max_depth = max_depth

        super().__init__(**kwargs)

    def get_nodes(self):
        # Simulates a realistic organizational tree.
        depth_pattern = [0, 1, 1, 2, 2, 1, 2, 0, 1, 1, 2]

        nodes = []

        for index in range(self.rows):
            depth = min(
                depth_pattern[index % len(depth_pattern)],
                self.max_depth - 1,
            )

            next_depth = (
                min(
                    depth_pattern[(index + 1) % len(depth_pattern)],
                    self.max_depth - 1,
                )
                if index < self.rows - 1
                else -1
            )

            nodes.append({
                "index": index,
                "depth": depth,
                "indent": depth * 36,
                "has_children": next_depth > depth,
                "is_last": next_depth < depth,
            })

        return nodes

    def get_context(self):
        return {
            **super().get_context(),
            "nodes": self.get_nodes(),
        }
