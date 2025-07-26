from decouple import config

if config('DEBUG', default=False, cast=bool):
    from .development import *
else:
    from .production import *