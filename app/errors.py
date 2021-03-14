import bugsnag
from aiohttp.client_exceptions import ClientPayloadError
from sanic.exceptions import MethodNotSupported, NotFound
from sanic.handlers import ErrorHandler

from . import settings

IGNORED_EXCEPTIONS = (NotFound, MethodNotSupported, ClientPayloadError)

bugsnag.configure(
    api_key=settings.BUGSNAG_API_KEY,
    project_root="/app",
    release_stage=settings.RELEASE_STAGE,
)


class BugsnagErrorHandler(ErrorHandler):
    def default(self, request, exception):
        if self._should_notify(exception):
            bugsnag.notify(exception, meta_data={"request": request.url})
        return super().default(request, exception)

    @staticmethod
    def _should_notify(exception) -> bool:
        if not settings.BUGSNAG_API_KEY:
            return False
        if isinstance(exception, IGNORED_EXCEPTIONS):
            return False
        return True
