import bugsnag
from sanic.exceptions import MethodNotSupported, NotFound
from sanic.handlers import ErrorHandler

from . import settings

bugsnag.configure(
    api_key=settings.BUGSNAG_API_KEY,
    project_root="/app",
    release_stage=settings.RELEASE_STAGE,
)


class BugsnagErrorHandler(ErrorHandler):
    def default(self, request, exception):
        if self._should_report(exception):
            bugsnag.notify(exception, meta_data={"request": request.url})
        return super().default(request, exception)

    def _should_report(self, exception) -> bool:
        if not settings.BUGSNAG_API_KEY:
            return False
        if isinstance(exception, (NotFound, MethodNotSupported)):
            return False
        return True
