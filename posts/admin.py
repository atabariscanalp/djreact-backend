from django.contrib import admin

from .models import Post
from .models import Category
from .models import Rate

class ClientAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Post, ClientAdmin)
admin.site.register(Category)
admin.site.register(Rate)
