from rest_framework import serializers
from .models import (
    User, Project, Station, TaskTemplate, Task,
    TaskFlowRecord, PreparationRecord, ReceptionRecord,
    ClosingRecord, ExceptionHandling
)


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'role_display', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ProjectSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.username', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'manager', 'manager_name', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class StationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Station
        fields = ['id', 'name', 'code', 'project', 'project_name', 'description', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class TaskTemplateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TaskTemplate
        fields = ['id', 'name', 'project', 'project_name', 'preparation_content', 
                  'reception_content', 'closing_content', 'description', 
                  'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class TaskFlowRecordSerializer(serializers.ModelSerializer):
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = TaskFlowRecord
        fields = ['id', 'old_status', 'old_status_display', 'new_status', 
                  'new_status_display', 'operator', 'operator_name', 'remark', 'created_at']


class PreparationRecordSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = PreparationRecord
        fields = ['id', 'task', 'content', 'operator', 'operator_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'operator']


class ReceptionRecordSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = ReceptionRecord
        fields = ['id', 'task', 'content', 'operator', 'operator_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'operator']


class ClosingRecordSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = ClosingRecord
        fields = ['id', 'task', 'content', 'has_exception', 'exception_description', 
                  'operator', 'operator_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'operator']


class ExceptionHandlingSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = ExceptionHandling
        fields = ['id', 'task', 'handling_content', 'reviewer', 'reviewer_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'reviewer']


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    can_hard_delete = serializers.BooleanField(read_only=True)
    flow_records = TaskFlowRecordSerializer(many=True, read_only=True)
    preparation = PreparationRecordSerializer(read_only=True)
    reception = ReceptionRecordSerializer(read_only=True)
    closing = ClosingRecordSerializer(read_only=True)
    exception_handlings = ExceptionHandlingSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'project', 'project_name', 'station', 'station_name',
                  'template', 'template_name', 'executor', 'executor_name',
                  'reviewer', 'reviewer_name', 'status', 'status_display',
                  'scheduled_time', 'can_hard_delete', 'flow_records',
                  'preparation', 'reception', 'closing', 'exception_handlings',
                  'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'is_deleted', 'can_hard_delete']


class TaskTransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    remark = serializers.CharField(required=False, allow_blank=True)
