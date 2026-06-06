from rest_framework import serializers
from .models import (
    User, Project, Station, TaskTemplate, Task,
    TaskFlowRecord, PreparationRecord, ReceptionRecord,
    ClosingRecord, ExceptionHandling, RectificationRecord, 
    TaskReview, TaskReviewOperationLog
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


class RectificationRecordSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)

    class Meta:
        model = RectificationRecord
        fields = ['id', 'task', 'stage', 'stage_display', 'rectification_content', 
                  'rectification_note', 'reviewer', 'reviewer_name', 
                  'executor', 'executor_name', 'status', 'status_display',
                  'created_at', 'rectified_at']
        read_only_fields = ['id', 'created_at', 'rectified_at', 'reviewer', 'executor', 'status']


class InitiateRectificationSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=RectificationRecord.STAGE_CHOICES)
    rectification_content = serializers.CharField()


class SubmitRectificationSerializer(serializers.Serializer):
    rectification_id = serializers.IntegerField()
    rectification_note = serializers.CharField()


class TaskReviewOperationLogSerializer(serializers.ModelSerializer):
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    old_followup_status_display = serializers.SerializerMethodField(read_only=True)
    new_followup_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskReviewOperationLog
        fields = [
            'id', 'operation_type', 'operation_type_display',
            'operator', 'operator_name',
            'old_followup_status', 'old_followup_status_display',
            'new_followup_status', 'new_followup_status_display',
            'remark', 'created_at'
        ]

    def get_old_followup_status_display(self, obj):
        if obj.old_followup_status:
            return dict(TaskReview.FOLLOWUP_STATUS_CHOICES).get(obj.old_followup_status, obj.old_followup_status)
        return None

    def get_new_followup_status_display(self, obj):
        if obj.new_followup_status:
            return dict(TaskReview.FOLLOWUP_STATUS_CHOICES).get(obj.new_followup_status, obj.new_followup_status)
        return None


class TaskReviewSerializer(serializers.ModelSerializer):
    problem_type_display = serializers.CharField(source='get_problem_type_display', read_only=True)
    responsibility_stage_display = serializers.CharField(source='get_responsibility_stage_display', read_only=True)
    followup_status_display = serializers.CharField(source='get_followup_status_display', read_only=True)
    initiator_name = serializers.CharField(source='initiator.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_status = serializers.CharField(source='task.status', read_only=True)
    task_status_display = serializers.CharField(source='task.get_status_display', read_only=True)
    project_id = serializers.IntegerField(source='task.project.id', read_only=True)
    project_name = serializers.CharField(source='task.project.name', read_only=True)
    station_id = serializers.IntegerField(source='task.station.id', read_only=True)
    station_name = serializers.CharField(source='task.station.name', read_only=True)
    executor_name = serializers.CharField(source='task.executor.username', read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    can_submit_feedback = serializers.SerializerMethodField(read_only=True)
    operation_logs = TaskReviewOperationLogSerializer(many=True, read_only=True)

    class Meta:
        model = TaskReview
        fields = [
            'id', 'task', 'task_title', 'task_status', 'task_status_display',
            'project_id', 'project_name', 'station_id', 'station_name',
            'executor_name', 'conclusion', 'problem_type', 'problem_type_display',
            'responsibility_stage', 'responsibility_stage_display',
            'improvement_suggestion', 'followup_status', 'followup_status_display',
            'rectification_feedback', 'initiator', 'initiator_name',
            'created_at', 'updated_at', 'rectification_feedback_at',
            'can_edit', 'can_submit_feedback', 'operation_logs'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'rectification_feedback_at',
            'initiator', 'task_title', 'task_status', 'task_status_display',
            'project_id', 'project_name', 'station_id', 'station_name',
            'executor_name', 'initiator_name'
        ]

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_edit(request.user)
        return False

    def get_can_submit_feedback(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_submit_feedback(request.user)
        return False


class CreateTaskReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReview
        fields = [
            'task', 'conclusion', 'problem_type',
            'responsibility_stage', 'improvement_suggestion'
        ]


class UpdateTaskReviewStatusSerializer(serializers.Serializer):
    followup_status = serializers.ChoiceField(choices=TaskReview.FOLLOWUP_STATUS_CHOICES)


class SubmitRectificationFeedbackSerializer(serializers.Serializer):
    rectification_feedback = serializers.CharField()


class TaskTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = ['id', 'name', 'preparation_content', 'reception_content', 'closing_content', 'description']


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_detail = TaskTemplateDetailSerializer(source='template', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    can_hard_delete = serializers.BooleanField(read_only=True)
    flow_records = TaskFlowRecordSerializer(many=True, read_only=True)
    preparation = PreparationRecordSerializer(read_only=True)
    reception = ReceptionRecordSerializer(read_only=True)
    closing = ClosingRecordSerializer(read_only=True)
    exception_handlings = ExceptionHandlingSerializer(many=True, read_only=True)
    rectification_records = RectificationRecordSerializer(many=True, read_only=True)
    current_rectification = serializers.SerializerMethodField(read_only=True)
    reviews = TaskReviewSerializer(many=True, read_only=True)
    can_initiate_review = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'project', 'project_name', 'station', 'station_name',
                  'template', 'template_name', 'template_detail', 'executor', 'executor_name',
                  'reviewer', 'reviewer_name', 'status', 'status_display',
                  'scheduled_time', 'can_hard_delete', 'flow_records',
                  'preparation', 'reception', 'closing', 'exception_handlings',
                  'rectification_records', 'current_rectification', 'reviews',
                  'can_initiate_review',
                  'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'is_deleted', 'can_hard_delete']

    def get_can_initiate_review(self, obj):
        request = self.context.get('request')
        if request and request.user:
            if request.user.role in ['manager', 'reviewer'] and obj.status in ['completed', 'cancelled']:
                return True
        return False

    def get_current_rectification(self, obj):
        current = obj.rectification_records.filter(status='pending').first()
        if current:
            return RectificationRecordSerializer(current).data
        return None


class TaskTransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    remark = serializers.CharField(required=False, allow_blank=True)
