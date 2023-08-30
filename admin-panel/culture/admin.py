from django.contrib import admin
from django.contrib.auth.models import Group
from django.db import models
from tinymce.widgets import TinyMCE

from .models import Route, RouteStage, Stage, StageStep, Step


class RouteStageInline(admin.TabularInline):
    verbose_name = 'Этап'
    verbose_name_plural = 'Этапы'
    model = RouteStage
    extra = 3


class StageStepInline(admin.TabularInline):
    verbose_name = 'Шаг'
    verbose_name_plural = 'Шаги'
    model = StageStep
    extra = 3


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
    list_display = ('name', 'address', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    inlines = [RouteStageInline]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
    list_display = ('name', 'address')
    search_fields = ('name', 'address')
    inlines = [StageStepInline]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
    list_display = ('type', 'content', 'photo', 'delay_after_display')
    list_filter = ('type',)
    search_fields = ('content',)


admin.site.unregister(Group)
