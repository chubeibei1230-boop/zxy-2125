from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    User, Project, Station, TaskTemplate, Task,
    TaskFlowRecord, PreparationRecord, ReceptionRecord,
    ClosingRecord, ExceptionHandling
)
from .serializers import (
    UserSerializer, UserCreateSerializer, ProjectSerializer,
    StationSerializer, TaskTemplateSerializer, TaskSerializer,
    TaskFlowRecordSerializer, PreparationRecordSerializer,
    ReceptionRecordSerializer, ClosingRecordSerializer,
    ExceptionHandlingSerializer, TaskTransitionSerializer
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
        'flow_records', 'preparation', 'reception', 'closing', 'exception_handlings'
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

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        user = request.user
        if user.role == 'executor':
            tasks = self.get_queryset().filter(executor=user)
        elif user.role == 'reviewer':
            tasks = self.get_queryset().filter(reviewer=user)
        else:
            tasks = self.get_queryset()
        
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
