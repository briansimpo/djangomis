from simple_menu import Menu, MenuItem
from djangospice.utils import safe_action
from .apps import namespace


home = MenuItem(
    title="Home", 
    url=safe_action(namespace, "home"), 
    icon="fas fa-home",
)


create_unit = MenuItem(
    title="Create Unit", 
    url=safe_action(namespace, "create_unit"), 
    icon="fas fa-plus",
)



Menu.add_item(namespace, home)
Menu.add_item(namespace, create_unit)




