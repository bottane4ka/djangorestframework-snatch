import copy

from rest_framework_recursive.fields import RecursiveField

from manager.models import ActionModel
from manager.models import BaseTaskLogModel
from manager.models import BaseTaskModel
from manager.models import TaskModel
from manager.models import TaskSequenceModel
from manager.models import TaskStatusModel
from snatch.fields import SnatchSerializerMethodField
from snatch.serializers import SnatchSerializer


class TaskStatusSerializer(SnatchSerializer):
    class Meta:
        model = TaskStatusModel
        fields = "__all__"


class BaseTaskSerializer(SnatchSerializer):
    task_sequence_list = SnatchSerializerMethodField()

    def get_task_sequence_list(self, instance):
        context = copy.copy(self.context)
        context["is_child"] = True
        return TaskSequenceSerializer(instance, many=True, context=context).data

    class Meta:
        model = BaseTaskModel
        fields = ("id", "name", "task_sequence_list")


class BaseTaskLogSerializer(SnatchSerializer):
    base_task = BaseTaskSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = BaseTaskLogModel
        fields = "__all__"


class TaskSerializer(SnatchSerializer):
    action_list = SnatchSerializerMethodField()

    def get_action_list(self, instance):
        return ActionSerializer(instance, many=True, context=self.context).data

    class Meta:
        model = TaskModel
        fields = ("id", "name", "action_list")


class TaskSequenceSerializer(SnatchSerializer):
    base_task = BaseTaskSerializer()
    task = TaskSerializer()

    class Meta:
        model = TaskSequenceModel
        fields = "__all__"


class ActionSerializer(SnatchSerializer):
    task = TaskSerializer()
    parent = RecursiveField()

    class Meta:
        model = ActionModel
        fields = "__all__"
