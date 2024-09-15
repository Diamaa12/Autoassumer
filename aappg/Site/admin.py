from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AappgCustomUser, AappgArticlesPost


# Register your models here.

class MyCustomUserAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'email',
                    'telephone',
                    'city',
                    'poste')
admin.site.register(AappgCustomUser, MyCustomUserAdmin)
class MyBlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'image', 'video', 'created_at', 'updated_at')

admin.site.register(AappgArticlesPost, MyBlogPostAdmin)