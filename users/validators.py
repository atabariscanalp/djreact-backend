from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
@deconstructible
class CustomUsernameValidator(validators.RegexValidator):
    regex = r'^(?!.*\.\.)(?!.*\.$)[^\W][\w.]{0,29}$'
    message = _(
        'Enter a valid username. This value may contain letters, '
        'numbers and underscores and dots.'
    )
    flags = 0
