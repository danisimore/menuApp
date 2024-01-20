from fastapi import FastAPI

from menu.router import router as menu_router
from submenu.router import router

app = FastAPI(
    title="Restaurant Menu"
)

app.include_router(menu_router)
app.include_router(router)
