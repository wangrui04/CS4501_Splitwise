
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from backend.repository import list_groups, get_group


class Login(BaseModel):
    name: str


def create_app(db, session_secret):
    app = FastAPI()

    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        same_site="lax",
        https_only=False,
    )

    def known_names():
        names = []

        for group in list_groups(db):
            details = get_group(db, group["id"])

            for name in details["members"]:
                if name not in names:
                    names.append(name)

        return names

    @app.middleware("http")
    async def protect(request: Request, call_next):
        path = request.url.path

        public_routes = {
            "/health",
            "/api/session/names",
            "/api/session",
        }

        requires_session = (
            path.startswith("/api/")
            and path not in public_routes
        )

        # GET /api/session and DELETE /api/session
        # are handled by their own endpoints.
        if path == "/api/session":
            requires_session = False

        if requires_session:
            name = request.session.get("name")

            if name not in known_names():
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Sign in required"},
                )

        return await call_next(request)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/session/names")
    def names():
        return known_names()

    @app.post("/api/session")
    def login(payload: Login, request: Request):
        if payload.name not in known_names():
            raise HTTPException(
                status_code=400,
                detail="Unknown name",
            )

        request.session.clear()
        request.session["name"] = payload.name

        return {"name": payload.name}

    @app.get("/api/session")
    def session(request: Request):
        name = request.session.get("name")

        if name not in known_names():
            raise HTTPException(
                status_code=401,
                detail="Not signed in",
            )

        return {"name": name}

    @app.delete("/api/session")
    def logout(request: Request):
        request.session.clear()
        return {"ok": True}

    @app.get("/api/groups")
    def groups():
        return [
            get_group(db, group["id"])
            for group in list_groups(db)
        ]

    @app.get("/api/groups/{group_id}")
    def group(group_id: int):
        result = get_group(db, group_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Group not found",
            )

        return result

    return app
