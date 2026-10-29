from .api import route_upload


def register(app):
    app.add_route("/upload", route_upload)
