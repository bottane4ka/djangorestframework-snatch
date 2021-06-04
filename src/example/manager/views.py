from snatch import viewsets
from manager.models import ActionModel
from manager.models import BaseTaskLogModel
from manager.models import BaseTaskModel
from manager.models import TaskModel
from manager.models import TaskSequenceModel
from manager.models import TaskStatusModel
from manager.serializer import ActionSerializer
from manager.serializer import BaseTaskLogSerializer
from manager.serializer import BaseTaskSerializer
from manager.serializer import TaskSequenceSerializer
from manager.serializer import TaskSerializer
from manager.serializer import TaskStatusSerializer


class ActionViewSet(viewsets.CustomModelViewSet):
    queryset = ActionModel.objects.all()
    serializer_class = ActionSerializer


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
