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



class FormSkeleton(Skeleton):
    template_name = get_template_name(
        "skeletons/form.html",
        namespace,
    )

    def __init__(
        self,
        rows=6,
        columns=1,
        show_sections=False,
        show_actions=False,
        **kwargs,
    ):
        self.rows = rows
        self.columns = columns
        self.show_sections = show_sections
        self.show_actions = show_actions

        super().__init__(**kwargs)

    def get_fields(self):
        # Simulates realistic form fields.
        field_pattern = [
            {"type": "input", "width": "full"},
            {"type": "input", "width": "full"},
            {"type": "select", "width": "full"},
            {"type": "input", "width": "half"},
            {"type": "input", "width": "half"},
            {"type": "textarea", "width": "full"},
            {"type": "select", "width": "full"},
            {"type": "input", "width": "full"},
        ]

        fields = []

        for index in range(self.rows):
            pattern = field_pattern[index % len(field_pattern)]

            fields.append({
                "index": index,
                "type": pattern["type"],
                "width": pattern["width"],
                "is_textarea": pattern["type"] == "textarea",
                "has_label": True,
            })

        return fields

    def get_rows(self):
        fields = self.get_fields()

        if self.columns <= 1:
            return [
                {"fields": [field]}
                for field in fields
            ]

        rows = []

        for index in range(0, len(fields), self.columns):
            rows.append({
                "fields": fields[index:index + self.columns],
            })

        return rows

    def get_context(self):
        return {
            **super().get_context(),
            "rows": self.get_rows(),
            "columns": self.columns,
            "show_sections": self.show_sections,
            "show_actions": self.show_actions,
        }