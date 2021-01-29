from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

from .validators import CustomUsernameValidator


class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    custom_username_validator = CustomUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=20,
        unique=True,
        help_text=_('Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[custom_username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'username':self.user})

# defines a path to upload photos
# def upload_path(instance, filename):
#     return '/'.join(['profilephotos', str(instance.title), filename])

def upload_path(instance, filename):
    file_path = 'profiles/{username}/{filename}'.format(
        username=str(instance.user.username), filename=filename
    )
    return file_path

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, related_name='profile', on_delete=models.CASCADE)
    location = models.CharField(max_length=140)
    profile_photo = models.ImageField(upload_to=upload_path, blank=True, null=True)
    language = models.CharField(max_length=10, default='en')

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username':self.user.username})


# This is a signal that updates/creates "Profile" when "User" instances updated/created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
