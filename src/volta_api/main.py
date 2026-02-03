from fastapi import FastAPI
from volta_api.core.database import database
from volta_api.users.router import router as users_router
from volta_api.auth.router import legacy_router as auth_legacy_router
from volta_api.auth.router import router as auth_router
from volta_api.vehicles.router import router as vehicles_router
from volta_api.vehicles.ws import router as vehicles_ws_router
from volta_api.nodes.router import router as nodes_router
from volta_api.routes.router import router as routes_router


app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(auth_legacy_router)
app.include_router(vehicles_router)
app.include_router(vehicles_ws_router)
app.include_router(nodes_router)
app.include_router(routes_router)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
