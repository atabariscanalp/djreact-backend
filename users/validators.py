from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class CustomUsernameValidator(validators.RegexValidator):
    regex = r'^[a-zA-Z][\w@-]{2,20}$' #2-20 characters long and may contain @ - _ characters. Only starts with letters.
    message = _(
        'Enter a valid username. This value may contain letters, '
        'numbers and underscores and dots.'
    )
    flags = 0
