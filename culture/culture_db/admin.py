from django.contrib import admin
from .models import Object, ObjectStep, Route, RouteObject, Step


class ObjectStepInline(admin.TabularInline):
    model = ObjectStep
    extra = 3


class RouteObjectInline(admin.TabularInline):
    model = RouteObject
    extra = 3


class StepAdmin(admin.ModelAdmin):
    list_display = ('type', 'content', 'delay_after_display')
    list_filter = ('type',)
    search_fields = ('content',)


class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'address')
    search_fields = ('name', 'author', 'address')
    inlines = [ObjectStepInline]


class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    inlines = [RouteObjectInline]


admin.site.register(Step, StepAdmin)
admin.site.register(Object, ObjectAdmin)
admin.site.register(Route, RouteAdmin)
