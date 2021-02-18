from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse

from users.models import CustomUser


# Upload location for images
def upload_location(instance, filename):
    file_path = 'posts/images/{author_name}/{title}-{filename}'.format(
        author_name=str(instance.author.username), title=str(instance.title), filename=filename
    )
    return file_path

def upload_location_video(instance, filename):
    file_path = 'posts/videos/{author_name}/{title}-{filename}'.format(
        author_name=str(instance.author.username), title=str(instance.title), filename=filename
    )
    return file_path

class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return 'title: {} - id:{}'.format(self.title, self.pk)


class Post(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to=upload_location, blank=True, null=True, verbose_name="Image", width_field='image_width', height_field='image_height')
    image_width = models.IntegerField(default=0)
    image_height = models.IntegerField(default=0)
    video = models.FileField(upload_to=upload_location_video, blank=True, null=True, verbose_name="Video")
    title = models.TextField(max_length=90, null=False, blank=False, unique=True, default="title", verbose_name="Title")
    slug = models.SlugField(unique=True, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, null=False, blank=False, verbose_name="Category", related_name="category")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug':self.slug})

    # def is_rated_by(self, user=None):
    #     if user and hasattr(user, 'id'):
    #         return self.rates.filter(is_active=True, user=rater.id).exists()
    #     return False

    @property
    def comment_count(self):
        return self.comments.all().count()

    @property
    def rate_count(self):
        return self.rates.filter(is_active=True).count()

    @property
    def avg_rate(self):
        rateSum = 0
        rates = self.rates.filter(is_active=True)
        for rate in rates:
            rateSum += rate.rate
        if rates.count() == 0:
            return 0
        return '{:0.2f}'.format(rateSum / self.rates.filter(is_active=True).count())


class Rate(models.Model):
    rater = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='rater', null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='rates', null=False)
    rate = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.date_updated = timezone.now()
        return super(Rate, self).save(*args, **kwargs)

    def __str__(self):
        return 'user: {} - rated: {} - post: {}'.format(self.rater.username, self.rate, self.post.slug)

    @property
    def rater_ids(self):
        if rater:
            return rater.id
        return null

# When post is deleted image stays on db so we need a function to delete the image
@receiver(post_delete, sender=Post)
def submission_delete(sender, instance,**kwargs):
    instance.image.delete(False)
    # instance.slug.delete(True)

# To create a unique slug for each post
def pre_save_post_receiver(sender, instance,*args,**kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
pre_save.connect(pre_save_post_receiver, sender=Post)



class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports', null=False)
    reporter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='reporter', null=False)
    report = models.CharField(max_length=100, verbose_name='Report Reason')
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
    
    def __str__(self):
        return 'user: {} - reported: {} - post: {}'.format(self.reporter.username, self.report, self.post.slug)
