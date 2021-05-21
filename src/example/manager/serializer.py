from rest_framework_recursive.fields import RecursiveField

from rest.brave_rest_framework.serializers import CustomSerializer
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
    class Meta:
        model = TaskModel
        fields = "__all__"


class TaskSequenceSerializer(CustomSerializer):
    base_task = BaseTaskSerializer()
    task = TaskSerializer()

    class Meta:
        model = TaskSequenceModel
        fields = "__all__"


class ModuleSerializer(CustomSerializer):
    class Meta:
        model = ModuleModel
        fields = "__all__"


class MethodModuleSerializer(CustomSerializer):
    module = ModuleSerializer(required=False)

    class Meta:
        model = MethodModuleModel
        fields = "__all__"


class ActionSerializer(CustomSerializer):
    task = TaskSerializer()
    method = MethodModuleSerializer()

    class Meta:
        model = ActionModel
        fields = "__all__"


class TaskLogSerializer(CustomSerializer):
    main_task_log = BaseTaskLogSerializer()
    action = ActionSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = TaskLogModel
        fields = "__all__"


class CommandSerializer(CustomSerializer):
    action = ActionSerializer()
    method = MethodModuleSerializer()
    parent = RecursiveField()

    class Meta:
        model = CommandModel
        fields = "__all__"


class CommandLogSerializer(CustomSerializer):
    task_log = TaskLogSerializer()
    parent = RecursiveField()
    command = CommandSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = CommandLogModel
        fields = "__all__"


class MessageSerializer(CustomSerializer):
    task_log = TaskLogSerializer()
    command_log = CommandLogSerializer()
    parent_msg = RecursiveField()
    sender = ModuleSerializer()
    recipient = ModuleSerializer()

    class Meta:
        model = MessageModel
        fields = "__all__"


class NotifyCountSerializer(CustomSerializer):

    class Meta:
        model = NotifyCountModel
        fields = "__all__"
