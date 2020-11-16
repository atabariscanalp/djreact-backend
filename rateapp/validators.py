from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not any(char.isalpha() for char in password):
          raise ValidationError(_('Password must contain at least 1 uppercase letter.'))

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )
