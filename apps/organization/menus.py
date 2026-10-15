from simple_menu import Menu, MenuItem
from djangospice.routing import safe_action
from .apps import namespace


home = MenuItem(
    title="Home", 
    url=safe_action(namespace, "home"), 
    icon="fas fa-home",
)


Menu.add_item(namespace, home)




