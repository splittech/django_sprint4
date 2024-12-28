from django.contrib import admin  # type: ignore[import-untyped] # noqa: F401
from .models import Category, Location, Post


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
