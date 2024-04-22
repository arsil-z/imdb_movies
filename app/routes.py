from app.user.routes import routes as user_routes
from app.shows.routes import routes as show_routes
from app.files.routes import routes as file_routes


imdb_movies_routes = user_routes + show_routes + file_routes


def register_routes(app):
    for route in imdb_movies_routes:
        app.add_url_rule(route[0], view_func=route[1].as_view(route[0]))
