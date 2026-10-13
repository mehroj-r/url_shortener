from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# First path segments the app routes itself; a short code can't take them over.
RESERVED_SHORT_CODES = ['admin', 'api', 'static', '__debug__', 'query-analyzer']

SHORT_CODE_PATTERN = r'[A-Za-z0-9_-]+'

validate_short_code_format = RegexValidator(
    regex=rf'^{SHORT_CODE_PATTERN}\Z',
    message=_("Short code may only contain letters, digits, '-' and '_'."),
)


def validate_short_code_not_reserved(value):
    if value.lower() in RESERVED_SHORT_CODES:
        raise ValidationError(_("'%(value)s' is reserved."), params={'value': value})
