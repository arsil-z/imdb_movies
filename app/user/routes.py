from app.user.views import UserView, LoginView

USER_ROUTES_PREFIX = "/api/users/"

routes = [
    (USER_ROUTES_PREFIX, UserView),
    (USER_ROUTES_PREFIX + "login", LoginView)
]
