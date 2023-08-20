from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Object, ObjectStep, Route, RouteObject, Step


class RouteObjectInline(admin.TabularInline):
    verbose_name = 'Этап'
    verbose_name_plural = 'Этапы'
    model = RouteObject
    extra = 3


class ObjectStepInline(admin.TabularInline):
    verbose_name = 'Шаг'
    verbose_name_plural = 'Шаги'
    model = ObjectStep
    extra = 3


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    inlines = [RouteObjectInline]


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'address')
    search_fields = ('name', 'author', 'address')
    inlines = [ObjectStepInline]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'content', 'delay_after_display')
    list_filter = ('type',)
    search_fields = ('content',)


admin.site.unregister(Group)
