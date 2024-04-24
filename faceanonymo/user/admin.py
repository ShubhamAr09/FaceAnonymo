from django.contrib import admin
from .models import InstaUser, PostImage , Post_Video

# Register your models here.
admin.site.register(InstaUser)
admin.site.register(PostImage)
admin.site.register(Post_Video)
