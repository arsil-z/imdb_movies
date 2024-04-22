from app.files.views import FileProcessorView, JobsProcessorView, FileView

FILES_ROUTE_PREFIX = "/api/files/"


routes = [
    (FILES_ROUTE_PREFIX + "process", FileProcessorView),
    (FILES_ROUTE_PREFIX + "process/jobs", JobsProcessorView),
    (FILES_ROUTE_PREFIX, FileView)
]
