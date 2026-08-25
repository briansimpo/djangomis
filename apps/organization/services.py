from django.db.transaction import atomic
from django.db import models
from .models import OrgUnit, OrgUnitClosure


class OrgUnitClosureService:

    @atomic
    @classmethod
    def create_node(cls, unit: OrgUnit):
        """
        Creates closure rows when a new OrgUnit is created.
        """

        # 1. self relationship
        OrgUnitClosure.objects.create(
            ancestor=unit,
            descendant=unit,
            depth=0
        )

        # 2. inherit parent hierarchy
        if not unit.parent:
            return

        parent_closures = OrgUnitClosure.objects.filter(
            descendant=unit.parent
        )

        OrgUnitClosure.objects.bulk_create([
            OrgUnitClosure(
                ancestor=pc.ancestor,
                descendant=unit,
                depth=pc.depth + 1
            )
            for pc in parent_closures
        ]) 
        
        
    @atomic
    @classmethod
    def move_node(cls, unit: OrgUnit, new_parent: OrgUnit):
        """
        Moves a node in the hierarchy and safely rebuilds closure paths.
        """

        if unit == new_parent:
            raise ValueError("OrgUnit cannot be its own parent")

        # Step 1: detach old subtree closure entries
        cls._delete_subtree_closure(unit)

        # Step 2: update adjacency relationship
        unit.parent = new_parent
        unit.save()

        # Step 3: rebuild closure for subtree
        OrgUnitClosureService._rebuild_subtree(unit)
        
        
    @classmethod
    def _delete_subtree_closure(cls, unit: OrgUnit):
        """
        Deletes all closure entries related to a subtree.
        """

        descendants = OrgUnitClosure.objects.filter(
            ancestor=unit
        ).values_list("descendant_id", flat=True)

        OrgUnitClosure.objects.filter(
            models.Q(descendant_id__in=descendants) |
            models.Q(ancestor_id__in=descendants)
        ).delete()
        
        
    @classmethod
    def _rebuild_subtree(cls, unit: OrgUnit):
        """
        Rebuild closure entries starting from a subtree root.
        """

        # rebuild self + ancestors
        cls._create_self_and_ancestors(unit)

        # recursively rebuild children
        children = OrgUnit.objects.filter(parent=unit)

        for child in children:
            cls._rebuild_subtree(child)
            
            
    @classmethod
    def _create_self_and_ancestors(cls, unit: OrgUnit):
        """
        Rebuilds closure rows for a single node.
        """

        # self link
        OrgUnitClosure.objects.create(
            ancestor=unit,
            descendant=unit,
            depth=0
        )

        if not unit.parent:
            return

        parent_links = OrgUnitClosure.objects.filter(
            descendant=unit.parent
        )

        OrgUnitClosure.objects.bulk_create([
            OrgUnitClosure(
                ancestor=link.ancestor,
                descendant=unit,
                depth=link.depth + 1
            )
            for link in parent_links
        ])
        

class OrgUnitService:

    @classmethod
    def create_unit(cls, name, parent=None, unit_type=None):
        unit = OrgUnit.objects.create(
            name=name,
            parent=parent,
            unit_type=unit_type
        )

        OrgUnitClosureService.create_node(unit)
        return unit

    @classmethod
    def move_unit(cls, unit, new_parent):
        OrgUnitClosureService.move_node(unit, new_parent)
        return unit
    
