from rest.brave_rest_framework import viewsets
from rest.manager.models import ActionModel
from rest.manager.models import BaseTaskLogModel
from rest.manager.models import BaseTaskModel
from rest.manager.models import CommandLogModel
from rest.manager.models import CommandModel
from rest.manager.models import MessageModel
from rest.manager.models import MethodModuleModel
from rest.manager.models import ModuleModel
from rest.manager.models import NotifyCountModel
from rest.manager.models import TaskLogModel
from rest.manager.models import TaskModel
from rest.manager.models import TaskSequenceModel
from rest.manager.models import TaskStatusModel
from rest.manager.serializer import ActionSerializer
from rest.manager.serializer import BaseTaskLogSerializer
from rest.manager.serializer import BaseTaskSerializer
from rest.manager.serializer import CommandLogSerializer
from rest.manager.serializer import CommandSerializer
from rest.manager.serializer import MessageSerializer
from rest.manager.serializer import MethodModuleSerializer
from rest.manager.serializer import ModuleSerializer
from rest.manager.serializer import NotifyCountSerializer
from rest.manager.serializer import TaskLogSerializer
from rest.manager.serializer import TaskSequenceSerializer
from rest.manager.serializer import TaskSerializer
from rest.manager.serializer import TaskStatusSerializer


class ActionViewSet(viewsets.CustomModelViewSet):
    queryset = ActionModel.objects.all()
    serializer_class = ActionSerializer


class CommandViewSet(viewsets.CustomModelViewSet):
    queryset = CommandModel.objects.all()
    serializer_class = CommandSerializer


class CommandLogViewSet(viewsets.CustomModelViewSet):
    queryset = CommandLogModel.objects.all()
    serializer_class = CommandLogSerializer


class MessageViewSet(viewsets.CustomModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageSerializer


class MethodModuleViewSet(viewsets.CustomModelViewSet):
    queryset = MethodModuleModel.objects.all()
    serializer_class = MethodModuleSerializer


class ModuleViewSet(viewsets.CustomModelViewSet):
    queryset = ModuleModel.objects.all()
    serializer_class = ModuleSerializer


class TaskLogViewSet(viewsets.CustomModelViewSet):
    queryset = TaskLogModel.objects.all()
    serializer_class = TaskLogSerializer


class TaskStatusViewSet(viewsets.CustomReadOnlyModelViewSet):
    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer


class BaseTaskViewSet(viewsets.CustomModelViewSet):
    queryset = BaseTaskModel.objects.all()
    serializer_class = BaseTaskSerializer


class BaseTaskLogViewSet(viewsets.CustomModelViewSet):
    queryset = BaseTaskLogModel.objects.all()
    serializer_class = BaseTaskLogSerializer


class TaskViewSet(viewsets.CustomModelViewSet):
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer


class TaskSequenceViewSet(viewsets.CustomModelViewSet):
    queryset = TaskSequenceModel.objects.all()
    serializer_class = TaskSequenceSerializer


class NotifyCountViewSet(viewsets.CustomModelViewSet):
    queryset = NotifyCountModel.objects.all()
    serializer_class = NotifyCountSerializer
