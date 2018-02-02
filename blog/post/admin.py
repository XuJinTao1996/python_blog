from django.contrib import admin
from .models import Article, Comment, Realtion_Article_Tags

# Register your models here.
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Realtion_Article_Tags)