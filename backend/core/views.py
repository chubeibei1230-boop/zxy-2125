from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    User, Project, Station, TaskTemplate, Task,
    TaskFlowRecord, PreparationRecord, ReceptionRecord,
    ClosingRecord, ExceptionHandling, RectificationRecord, TaskReview
)
from .serializers import (
    UserSerializer, UserCreateSerializer, ProjectSerializer,
    StationSerializer, TaskTemplateSerializer, TaskSerializer,
    TaskFlowRecordSerializer, PreparationRecordSerializer,
    ReceptionRecordSerializer, ClosingRecordSerializer,
    ExceptionHandlingSerializer, TaskTransitionSerializer,
    InitiateRectificationSerializer, SubmitRectificationSerializer,
    RectificationRecordSerializer, TaskReviewSerializer,
    CreateTaskReviewSerializer, UpdateTaskReviewStatusSerializer,
    SubmitRectificationFeedbackSerializer
)


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'manager'


class IsExecutor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'executor'


class IsReviewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'reviewer'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_role(self, request):
        role = request.query_params.get('role')
        if role:
            users = User.objects.filter(role=role)
        else:
            users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class BaseModelViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        queryset = super().get_queryset()
        show_deleted = self.request.query_params.get('show_deleted', 'false').lower() == 'true'
        if not show_deleted:
            queryset = queryset.filter(is_deleted=False)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(BaseModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_fields = ['manager']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]


class StationViewSet(BaseModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filterset_fields = ['project']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]


class TaskTemplateViewSet(BaseModelViewSet):
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    filterset_fields = ['project']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]


class TaskViewSet(BaseModelViewSet):
    queryset = Task.objects.select_related(
        'project', 'station', 'template', 'executor', 'reviewer'
    ).prefetch_related(
        'flow_records', 'preparation', 'reception', 'closing', 
        'exception_handlings', 'rectification_records'
    ).all()
    serializer_class = TaskSerializer
    filterset_fields = ['project', 'station', 'executor', 'reviewer', 'status']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        hard_delete = request.query_params.get('hard', 'false').lower() == 'true'
        
        if hard_delete:
            if instance.can_hard_delete():
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'detail': '该任务已有流转记录，无法硬删除，请使用软删除'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            instance.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        task = self.get_object()
        serializer = TaskTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['new_status']
        remark = serializer.validated_data.get('remark', '')
        
        try:
            task.transition_to(new_status, request.user, remark)
            return Response(TaskSerializer(task).data)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsExecutor])
    def submit_preparation(self, request, pk=None):
        task = self.get_object()
        if hasattr(task, 'preparation'):
            return Response({'detail': '准备记录已存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PreparationRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, operator=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsExecutor])
    def submit_reception(self, request, pk=None):
        task = self.get_object()
        if hasattr(task, 'reception'):
            return Response({'detail': '接待记录已存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ReceptionRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, operator=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsExecutor])
    def submit_closing(self, request, pk=None):
        task = self.get_object()
        if hasattr(task, 'closing'):
            return Response({'detail': '收尾记录已存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ClosingRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, operator=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsReviewer])
    def handle_exception(self, request, pk=None):
        task = self.get_object()
        serializer = ExceptionHandlingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, reviewer=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsReviewer])
    def initiate_rectification(self, request, pk=None):
        task = self.get_object()
        if task.status not in ['pending_review', 'rectified_pending_review']:
            return Response(
                {'detail': '当前状态不能发起整改'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InitiateRectificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rectification = RectificationRecord.objects.create(
            task=task,
            stage=serializer.validated_data['stage'],
            rectification_content=serializer.validated_data['rectification_content'],
            reviewer=request.user,
            executor=task.executor
        )
        
        task.transition_to('rectification_pending', request.user, f'发起{rectification.get_stage_display()}整改', skip_rectification_check=True)
        
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsExecutor])
    def submit_rectification(self, request, pk=None):
        task = self.get_object()
        if task.status != 'rectification_pending':
            return Response(
                {'detail': '当前状态不能提交整改'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitRectificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rectification = RectificationRecord.objects.filter(
            id=serializer.validated_data['rectification_id'],
            task=task,
            status='pending'
        ).first()
        
        if not rectification:
            return Response(
                {'detail': '整改记录不存在或已处理'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if rectification.executor != request.user:
            return Response(
                {'detail': '您不是该整改的执行人'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.utils import timezone
        rectification.rectification_note = serializer.validated_data['rectification_note']
        rectification.status = 'rectified'
        rectification.rectified_at = timezone.now()
        rectification.save()
        
        task.transition_to('rectified_pending_review', request.user, '提交整改完成，等待复核', skip_rectification_check=True)
        
        return Response(TaskSerializer(task).data)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        user = request.user
        if user.role == 'executor':
            tasks = self.get_queryset().filter(executor=user)
        elif user.role == 'reviewer':
            tasks = self.get_queryset().filter(reviewer=user)
        else:
            tasks = self.get_queryset()
        
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskFlowRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskFlowRecord.objects.select_related('task', 'operator').all()
    serializer_class = TaskFlowRecordSerializer
    filterset_fields = ['task']
    permission_classes = [permissions.IsAuthenticated]


class IsManagerOrReviewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['manager', 'reviewer']


class TaskReviewViewSet(viewsets.ModelViewSet):
    queryset = TaskReview.objects.select_related(
        'task', 'task__project', 'task__station', 'task__executor', 'initiator'
    ).all()
    serializer_class = TaskReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'problem_type', 'responsibility_stage', 'followup_status']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == 'executor':
            queryset = queryset.filter(task__executor=user)
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(task__project_id=project)
        station = self.request.query_params.get('station')
        if station:
            queryset = queryset.filter(task__station_id=station)
        task_status = self.request.query_params.get('task_status')
        if task_status:
            queryset = queryset.filter(task__status=task_status)
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrReviewer()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateTaskReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.validated_data['task']
        if task.status not in ['completed', 'cancelled']:
            return Response(
                {'detail': '只能对已完成或已取消的任务发起复盘'},
                status=status.HTTP_400_BAD_REQUEST
            )
        review = TaskReview.objects.create(
            task=task,
            conclusion=serializer.validated_data['conclusion'],
            problem_type=serializer.validated_data['problem_type'],
            responsibility_stage=serializer.validated_data['responsibility_stage'],
            improvement_suggestion=serializer.validated_data['improvement_suggestion'],
            initiator=request.user
        )
        return Response(TaskReviewSerializer(review, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_edit(request.user):
            return Response(
                {'detail': '您没有权限编辑此复盘记录'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_edit(request.user):
            return Response(
                {'detail': '您没有权限编辑此复盘记录'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_edit(request.user):
            return Response(
                {'detail': '您没有权限删除此复盘记录'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrReviewer])
    def update_status(self, request, pk=None):
        review = self.get_object()
        if not review.can_edit(request.user):
            return Response(
                {'detail': '您没有权限修改此复盘记录的状态'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UpdateTaskReviewStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.followup_status = serializer.validated_data['followup_status']
        review.save()
        return Response(TaskReviewSerializer(review, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsExecutor])
    def submit_feedback(self, request, pk=None):
        review = self.get_object()
        if not review.can_submit_feedback(request.user):
            return Response(
                {'detail': '您没有权限提交此复盘记录的整改反馈'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = SubmitRectificationFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from django.utils import timezone
        review.rectification_feedback = serializer.validated_data['rectification_feedback']
        review.rectification_feedback_at = timezone.now()
        if review.followup_status == 'pending':
            review.followup_status = 'processing'
        review.save()
        return Response(TaskReviewSerializer(review, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        user = request.user
        if user.role == 'executor':
            reviews = self.get_queryset().filter(task__executor=user)
        elif user.role == 'reviewer':
            reviews = self.get_queryset().filter(initiator=user)
        else:
            reviews = self.get_queryset()
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        queryset = self.get_queryset()
        pending_count = queryset.filter(followup_status='pending').count()
        processing_count = queryset.filter(followup_status='processing').count()
        completed_count = queryset.filter(followup_status='completed').count()
        closed_count = queryset.filter(followup_status='closed').count()
        
        if user.role == 'executor':
            pending_feedback = queryset.filter(
                task__executor=user,
                rectification_feedback=''
            ).count()
        else:
            pending_feedback = 0
        
        return Response({
            'pending': pending_count,
            'processing': processing_count,
            'completed': completed_count,
            'closed': closed_count,
            'pending_feedback': pending_feedback,
            'total': pending_count + processing_count + completed_count + closed_count
        })
