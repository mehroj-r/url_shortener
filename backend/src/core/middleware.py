from django.conf import settings
from whitenoise.middleware import WhiteNoiseMiddleware


class StaticFilesMiddleware(WhiteNoiseMiddleware):
    """
    WhiteNoise for Django's static files plus the built web app's files under /app/.

    The app's page itself (index.html) is returned by `core.views.web_app`, so that
    every route under /app/ gets it with no-cache and the app's Content-Security-Policy.
    """

    APP_PREFIX = '/app/'

    def __init__(self, get_response=None, settings=settings):
        super().__init__(get_response, settings)
        if settings.FRONTEND_DIR.is_dir():
            self.add_files(settings.FRONTEND_DIR, prefix=self.APP_PREFIX)

    def immutable_file_test(self, path, url):
        # Vite puts a content hash in every file name under assets/
        return url.startswith(f'{self.APP_PREFIX}assets/') or super().immutable_file_test(path, url)
