from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from volta_api.core.api_response import error_response
from volta_api.core.database import database
from volta_api.users.router import router as users_router
from volta_api.auth.router import legacy_router as auth_legacy_router
from volta_api.auth.router import router as auth_router
from volta_api.vehicles.router import router as vehicles_router
from ws.ws import router as vehicles_ws_router
from volta_api.nodes.router import router as nodes_router
from volta_api.routes.router import router as routes_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(auth_legacy_router)
app.include_router(vehicles_router)
app.include_router(vehicles_ws_router)
app.include_router(nodes_router)
app.include_router(routes_router)


def _extract_error_message(detail: object) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict):
        message = detail.get("message")
        if isinstance(message, str):
            return message
    return "Request failed"


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):  # noqa: ARG001
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(_extract_error_message(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):  # noqa: ARG001
    errors = []
    missing_fields = []
    for err in exc.errors():
        loc = [str(part) for part in err.get("loc", []) if part != "body"]
        field = ".".join(loc) if loc else "body"
        message = err.get("msg", "Invalid value")
        error_type = err.get("type")
        errors.append(
            {
                "field": field,
                "message": message,
                "type": error_type,
            }
        )
        if error_type == "missing":
            missing_fields.append(field)

    if missing_fields:
        message = f"Missing required fields: {', '.join(missing_fields)}"
    else:
        message = "Validation error"

    return JSONResponse(
        status_code=422,
        content=error_response(
            message,
            data={
                "errors": errors,
                "missing_fields": missing_fields,
            },
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):  # noqa: ARG001
    return JSONResponse(
        status_code=500,
        content=error_response("Internal server error"),
    )


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
