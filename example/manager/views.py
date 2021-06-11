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
from snatch import viewsets


class ActionViewSet(viewsets.SnatchModelViewSet):
    queryset = ActionModel.objects.all()
    serializer_class = ActionSerializer


class TaskStatusViewSet(viewsets.SnatchReadOnlyModelViewSet):
    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer


class BaseTaskViewSet(viewsets.SnatchModelViewSet):
    queryset = BaseTaskModel.objects.all()
    serializer_class = BaseTaskSerializer


class BaseTaskLogViewSet(viewsets.SnatchModelViewSet):
    queryset = BaseTaskLogModel.objects.all()
    serializer_class = BaseTaskLogSerializer


class TaskViewSet(viewsets.SnatchModelViewSet):
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer


class TaskSequenceViewSet(viewsets.SnatchModelViewSet):
    queryset = TaskSequenceModel.objects.all()
    serializer_class = TaskSequenceSerializer
