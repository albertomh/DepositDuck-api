"""
(c) 2024 Alberto Morón Hernández
"""

from starlette.routing import Mount

from depositduck.main import webapp


def test_app_mounts():
    """
    Test that mounts for static files, the api & llm apps are present on the webapp.
    """
    mounts = {
        "webapp static": {"path": "/static", "observed": False},
        "apiapp": {"path": "/api", "observed": False},
        "llmapp": {"path": "/llm", "observed": False},
    }

    for route in webapp.routes:
        for k, v in mounts.items():
            if isinstance(route, Mount) and route.path == v["path"]:
                mounts[k]["observed"] = True
                break

    for k, v in mounts.items():
        assert v["observed"], f"{k} not mounted under '{v["path"]}'."
