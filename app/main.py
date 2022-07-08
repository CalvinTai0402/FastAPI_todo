from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from . import models
from .routers import task, user, auth, tag

app = FastAPI()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(task.router)
app.include_router(tag.router)

