from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Project, Station, TaskTemplate, Task,
    TaskFlowRecord, PreparationRecord, ReceptionRecord,
    ClosingRecord, ExceptionHandling, RectificationRecord, TaskReview
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'role', 'email', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('角色信息', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('角色信息', {'fields': ('role',)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['name']


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'project', 'is_deleted']
    list_filter = ['project', 'is_deleted']
    search_fields = ['name', 'code']


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_at', 'is_deleted']
    list_filter = ['project', 'is_deleted']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'station', 'executor', 'reviewer', 'status', 'scheduled_time', 'is_deleted']
    list_filter = ['status', 'project', 'station', 'is_deleted']
    search_fields = ['title']


@admin.register(TaskFlowRecord)
class TaskFlowRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'old_status', 'new_status', 'operator', 'created_at']
    list_filter = ['old_status', 'new_status']
    search_fields = ['task__title']


@admin.register(PreparationRecord)
class PreparationRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'operator', 'created_at']
    search_fields = ['task__title']


@admin.register(ReceptionRecord)
class ReceptionRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'operator', 'created_at']
    search_fields = ['task__title']


@admin.register(ClosingRecord)
class ClosingRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'has_exception', 'operator', 'created_at']
    list_filter = ['has_exception']
    search_fields = ['task__title']


@admin.register(ExceptionHandling)
class ExceptionHandlingAdmin(admin.ModelAdmin):
    list_display = ['task', 'reviewer', 'created_at']
    search_fields = ['task__title']


@admin.register(RectificationRecord)
class RectificationRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'stage', 'status', 'reviewer', 'executor', 'created_at']
    list_filter = ['stage', 'status']
    search_fields = ['task__title']


@admin.register(TaskReview)
class TaskReviewAdmin(admin.ModelAdmin):
    list_display = ['task', 'problem_type', 'responsibility_stage', 'followup_status', 'initiator', 'created_at']
    list_filter = ['problem_type', 'responsibility_stage', 'followup_status']
    search_fields = ['task__title', 'conclusion']
