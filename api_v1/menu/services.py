def count_dishes(menu):
    dishes = 0

    for submenu in menu.submenus:
        dishes += submenu.dishes_counter

    return dishes
