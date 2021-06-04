from rest_framework_recursive.fields import RecursiveField

from snatch.serializers import CustomSerializer
from snatch.fields import CustomListField
from manager.models import ActionModel
from manager.models import BaseTaskLogModel
from manager.models import BaseTaskModel
from manager.models import TaskModel
from manager.models import TaskSequenceModel
from manager.models import TaskStatusModel


class TaskStatusSerializer(CustomSerializer):
    class Meta:
        model = TaskStatusModel
        fields = "__all__"


class BaseTaskSerializer(CustomSerializer):
    class Meta:
        model = BaseTaskModel
        fields = "__all__"


class BaseTaskLogSerializer(CustomSerializer):
    base_task = BaseTaskSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = BaseTaskLogModel
        fields = "__all__"


class TaskSerializer(CustomSerializer):
    action_list = CustomListField(child=RecursiveField())

    class Meta:
        model = TaskModel
        fields = "__all__"


class TaskSequenceSerializer(CustomSerializer):
    base_task = BaseTaskSerializer()
    task = TaskSerializer()

    class Meta:
        model = TaskSequenceModel
        fields = "__all__"


class ActionSerializer(CustomSerializer):
    task = TaskSerializer()
    parent = RecursiveField()

    class Meta:
        model = ActionModel
        fields = "__all__"
