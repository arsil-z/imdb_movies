from app.db.client import mongo_conn


class ShowType:
    MOVIE = "movie"
    TV_SHOW = "tv_show"


class Shows:
    def __init__(self):
        pass

    def create_bulk(self, documents):
        mongo_conn.shows.insert_many(documents)
        return

    def get_paginated_shows_by_filters(self, page, page_size, sort_by, sort_order):
        skip = (page - 1) * page_size

        sort_options = {
            "date_added": [("date_added", sort_order)],
            "release_year": [("release_year", sort_order)],
            "duration": [("file_duration", sort_order)]
        }

        sorted_shows = []
        sort_option = sort_options.get(sort_by)
        if sort_by == "date_added":
            shows = mongo_conn.shows.aggregate([
                {"$addFields": {"date_added": {
                    "$dateFromString": {"dateString": "$date_added", "format": "%B %d, %Y"}}}},
                {"$sort": {"date_added": sort_order}},
                {"$skip": skip},
                {"$limit": page_size}
            ])
        else:
            shows = mongo_conn.shows.find().skip(skip).limit(page_size).sort(sort_option)

        for show in shows:
            show["_id"] = str(show["_id"])
            sorted_shows.append(show)

        return sorted_shows
