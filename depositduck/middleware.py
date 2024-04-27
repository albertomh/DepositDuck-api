"""
important! Strictly speaking these are FastAPI dependables, but they behave and are used
closer to how middleware behaves and is used. Hence they are referred to as 'middleware'.

(c) 2024 Alberto Morón Hernández
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from depositduck.auth.users import current_active_user
from depositduck.models.sql.auth import User

FRONTEND_MUST_BE_LOGGED_OUT_PATHS = [
    "/login/",
    "/signup/",
]

OPERATIONS_MUST_BE_LOGGED_OUT_PATHS = [
    "/auth/filterProspect/",
    "/auth/unsuitableProspectFunnel/",
    "/auth/request-verification/",
    "/auth/verify/",
    "/auth/authenticate/",
]

ONBOARDING_PATH = "/welcome/"


async def _get_path_from_request(request: Request) -> tuple[str, str | None]:
    """
    Returns:
        tuple[str, str | None]: the path and (optionally) query param for the request.
        eg. `("/login/", "next=/")
    """
    base = str(request.base_url).rstrip("/")
    url = str(request.url)
    path = url[len(base) :]
    path_parts = path.split("?")
    if len(path_parts) == 1:
        return (path_parts[0], None)
    else:
        return (path_parts[0], path_parts[1])


async def frontend_auth_middleware(
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
):
    """
    Protect routes based on the authentication status of the user associated
    with the request (if any). Define an allowlist of which routes may be
    accessed without auth. Assume all others require a logged-in user.
    """
    path, query = await _get_path_from_request(request)

    # anonymous requests trying to reach protected routes are redirected to /login/
    if user is None and path not in FRONTEND_MUST_BE_LOGGED_OUT_PATHS:
        redirect_path = f"/login/?next={path}"
        if query is not None:
            redirect_path += f"&{query}"
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": redirect_path},
        )

    if user is not None:
        # logged-in users trying to reach anonymous-only paths are redirected
        if path in FRONTEND_MUST_BE_LOGGED_OUT_PATHS:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/"},
            )
        if user.completed_onboarding_at is not None:
            # users who have been onboarded are redirected away from the onboarding screen
            if path == ONBOARDING_PATH:
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": "/"},
                )
        else:
            # users who are yet to be onboarded are redirected to the onboarding screen
            if path != ONBOARDING_PATH:
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": ONBOARDING_PATH},
                )


async def operations_auth_middleware(
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
):
    """
    Protect routes based on the authentication status of the user associated
    with the request (if any). Define an allowlist of which routes may be
    accessed without auth. Assume all others require a logged-in user.
    """
    path, query = await _get_path_from_request(request)

    if user is not None and path in OPERATIONS_MUST_BE_LOGGED_OUT_PATHS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if user is not None and path in OPERATIONS_MUST_BE_LOGGED_OUT_PATHS:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"}
        )
