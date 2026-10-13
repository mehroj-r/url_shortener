import os

from decouple import config

# `config.settings` picks development or production from DEBUG.
# Other modules (e.g. `config.settings.test`) are selected directly and skip this.
if os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings') == 'config.settings':
    if config('DEBUG', default=False, cast=bool):
        from .development import *
    else:
        from .production import *
