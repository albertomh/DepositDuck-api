"""
(c) 2024 Alberto Morón Hernández
"""

from starlette.routing import Mount

from depositduck.main import get_webapp, webapp


def test_get_webapp_mounts_static_dir():
    """
    Test that get_webapp returns an app with static files mounted at '/static'.
    """
    app = get_webapp()
    static_found = False

    for route in app.routes:
        if isinstance(route, Mount) and route.path == "/static":
            static_found = True
            break

    assert static_found, "static files are not mounted under '/static'."


def test_apiapp_mounted_on_webapp():
    """
    Test that apiapp is mounted on the webapp at '/api'.
    """
    api_mount_found = False

    for route in webapp.routes:
        if isinstance(route, Mount) and route.path == "/api":
            api_mount_found = True
            break

    assert api_mount_found, "apiapp is not mounted under '/api'."
