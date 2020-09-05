import bugsnag
from sanic.handlers import ErrorHandler

from . import settings

if settings.BUGSNAG_API_KEY:
    bugsnag.configure(
        api_key=settings.BUGSNAG_API_KEY,
        project_root="/app",
        release_state=settings.RELEASE_STAGE,
    )


class BugsnagErrorHandler(ErrorHandler):
    def default(self, request, exception):
        bugsnag.notify(exception, meta_data={"request": request.url})
        return super().default(request, exception)
