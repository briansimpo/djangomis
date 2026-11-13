from simple_menu import Menu, MenuItem
from djangospice.utils import safe_action
from .apps import namespace


home = MenuItem(
    title="Home", 
    url=safe_action(namespace, "home"), 
    icon="fas fa-home",
)

create_org_unit = MenuItem(
    title="Create Org Unit", 
    url=safe_action(namespace, "create_org_unit"), 
    icon="fas fa-plus",
)


view_org_unit = MenuItem(
    title="Org Units", 
    url=safe_action(namespace, "org_unit_list"), 
    icon="fas fa-list",
)


org_unit_structure = MenuItem(
    title="Org Structure", 
    url=safe_action(namespace, "org_unit_structure"), 
    icon="fas fa-sitemap",
)


Menu.add_item(namespace, home)
Menu.add_item(namespace, create_org_unit)
Menu.add_item(namespace, view_org_unit)
Menu.add_item(namespace, org_unit_structure)




