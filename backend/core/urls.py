from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'stations', views.StationViewSet)
router.register(r'task-templates', views.TaskTemplateViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'flow-records', views.TaskFlowRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
