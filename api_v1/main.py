from fastapi import FastAPI

from menu.router import router as menu_router
from submenu.router import router as submenu_router
from dish.router import router as dish_router

app = FastAPI(
    title="Restaurant Menu"
)

app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)
