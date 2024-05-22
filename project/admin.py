from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Proj_Post, Proj_Category, Proj_Tag, Proj_Comment

admin.site.register(Proj_Post, MarkdownxModelAdmin)
admin.site.register(Proj_Comment)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Proj_Category, CategoryAdmin)
admin.site.register(Proj_Tag, TagAdmin)