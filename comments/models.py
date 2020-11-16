from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from posts.models import Post
from users.models import CustomUser

class GetParentComments(models.Manager):
    def get_query_set(self):
        return super(GetParentComments, self).get_query_set().filter(is_parent=False)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_active = models.BooleanField(default=True)
    star_rate = models.FloatField(default=0.0)
    objects = models.Manager()
    parent_comments = GetParentComments()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post}'

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

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

class CommentRate(models.Model):
    rater = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='commentRater', null=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='rates', null=False)
    rate = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.date_updated = timezone.now()
        return super(CommentRate, self).save(*args, **kwargs)

    def __str__(self):
        return 'user: {} - rated: {} - comment: {}'.format(self.rater.username, self.rate, self.comment.id)

    @property
    def rater_ids(self):
        if rater:
            return rater.id
        return null
