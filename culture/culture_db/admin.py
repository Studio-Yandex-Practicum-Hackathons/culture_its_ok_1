from django.contrib import admin

from .models import (Object, ObjectStep, Progress, Reflection, Route,
                     RouteObject, Step, User)


class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')


admin.site.register(Route, RouteAdmin)


class StepAdmin(admin.ModelAdmin):
    list_display = ('route', 'type', 'content', 'delay_after_display')
    list_filter = ('type',)
    search_fields = ('content',)


admin.site.register(Step, StepAdmin)


class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'address')
    search_fields = ('name', 'author', 'address')


admin.site.register(Object, ObjectAdmin)


class RouteObjectAdmin(admin.ModelAdmin):
    list_display = ('route', 'object', 'object_priority', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('route__name', 'object__name')


admin.site.register(RouteObject, RouteObjectAdmin)


class ObjectStepAdmin(admin.ModelAdmin):
    list_display = ('object', 'step', 'step_priority')
    list_filter = ('object',)
    search_fields = ('object__name', 'step__content')


admin.site.register(ObjectStep, ObjectStepAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'age')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)


class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'route', 'object', 'started_at', 'finished_at')
    list_filter = ('route', 'object')
    search_fields = ('user__name', 'route__name', 'object__name')


admin.site.register(Progress, ProgressAdmin)


class ReflectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'route', 'object', 'type', 'content')
    list_filter = ('type', 'route', 'object')
    search_fields = ('user__name', 'route__name', 'object__name', 'content')


admin.site.register(Reflection, ReflectionAdmin)
