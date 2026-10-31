
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from itsdangerous import TimestampSigner, BadSignature

from backend.repository import list_groups, get_group


class Login(BaseModel):
    name: str


def create_app(db, session_secret):
    app = FastAPI()

    def known_names():
        names = []

        for group in list_groups(db):
            details = get_group(db, group["id"])

            for name in details["members"]:
                if name not in names:
                    names.append(name)

        return names

    # Use the same signer as Starlette's SessionMiddleware.
    signer = TimestampSigner(str(session_secret))

    def session_cookie_is_valid(request: Request):
        cookie = request.cookies.get("session")

        if not cookie:
            return False

        try:
            # Verify the cookie's cryptographic signature.
            unsigned = signer.unsign(
                cookie,
                max_age=14 * 24 * 60 * 60,
            )

            # Reject any noncanonical cookie representation.
            # This includes appended text that might otherwise
            # be accepted by the signature decoder.
            return (
                signer.sign(unsigned).decode("utf-8") == cookie
            )

        except (BadSignature, ValueError, UnicodeError):
            return False

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

        # GET and DELETE /api/session handle sessions themselves.
        if path == "/api/session":
            requires_session = False

        if requires_session:
            # Reject missing, expired, or modified cookies.
            if not session_cookie_is_valid(request):
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Invalid or missing session"
                    },
                )

            name = request.session.get("name")

            if name not in known_names():
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Sign in required"
                    },
                )

        return await call_next(request)

    # Register SessionMiddleware last so that it runs first.
    # This initializes request.session before protect() uses it.
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        same_site="lax",
        https_only=False,
    )

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
