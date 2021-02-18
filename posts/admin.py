from django.contrib import admin

from .models import Post, Category, Rate, Report


class ClientAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Post, ClientAdmin)
admin.site.register(Category)
admin.site.register(Rate)
admin.site.register(Report)
