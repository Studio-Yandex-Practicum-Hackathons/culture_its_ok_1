from django.contrib import admin
from django.contrib.auth.models import Group

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
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    inlines = [RouteStageInline]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')
    inlines = [StageStepInline]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ('type', 'content', 'photo', 'delay_after_display')
    list_filter = ('type',)
    search_fields = ('content',)


admin.site.unregister(Group)
