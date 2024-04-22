from app.shows.views import ShowsUploadFileView, ShowView

SHOW_ROUTES_PREFIX = "/api/shows/"


routes = [
    (SHOW_ROUTES_PREFIX + "upload", ShowsUploadFileView),
    (SHOW_ROUTES_PREFIX, ShowView)
]
