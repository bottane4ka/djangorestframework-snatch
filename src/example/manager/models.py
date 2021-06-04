from datetime import datetime
from uuid import uuid4

from django.db import models


class ActionModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    task = models.ForeignKey(
        "manager.TaskModel",
        db_column="task_id",
        on_delete=models.CASCADE,
        related_name="action_list",
        verbose_name="Задача",
    )
    parent = models.ForeignKey(
        "manager.ActionModel",
        db_column="parent_id",
        on_delete=models.CASCADE,
        null=True,
        related_name="action_list",
        verbose_name="Родительское действие",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")
    number = models.IntegerField(
        db_column="number", default=1, blank=True, verbose_name="Порядковый номер"
    )

    class Meta:
        db_table = 'manager"."action'
        verbose_name = "Действие"
        verbose_name_plural = "Действия"


class BaseTaskModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")

    class Meta:
        db_table = 'manager"."base_task'
        verbose_name = "Базовая задача"
        verbose_name_plural = "Базовые задачи"


class BaseTaskLogModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    base_task = models.ForeignKey(
        "manager.BaseTaskModel",
        db_column="base_task_id",
        on_delete=models.CASCADE,
        related_name="main_task_log_list",
        verbose_name="Базовая задача",
    )
    status = models.ForeignKey(
        "manager.TaskStatusModel",
        db_column="status_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="main_task_log_list",
        verbose_name="Статус выполнения задачи",
    )
    add_task_date = models.DateTimeField(
        db_column="add_task_date",
        default=datetime.now,
        blank=True,
        verbose_name="Дата постановки базовой задачи",
    )
    exec_task_date = models.DateTimeField(
        db_column="exec_task_date",
        null=True,
        blank=True,
        verbose_name="Дата начала выполнения задачи",
    )
    end_task_date = models.DateTimeField(
        db_column="end_task_date",
        null=True,
        blank=True,
        verbose_name="Дата окончания выполнения задачи",
    )

    class Meta:
        db_table = 'manager"."base_task_log'
        verbose_name = "Аудит выполнения базовой задачи"
        verbose_name_plural = "Аудит выполнения базовых задач"


class TaskModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")

    class Meta:
        db_table = 'manager"."task'
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class TaskSequenceModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    base_task = models.ForeignKey(
        "manager.BaseTaskModel",
        db_column="base_task_id",
        on_delete=models.CASCADE,
        related_name="task_sequence_list",
        verbose_name="Базовая задача",
    )
    task = models.ForeignKey(
        "manager.TaskModel",
        db_column="task_id",
        on_delete=models.CASCADE,
        related_name="task_sequence_list",
        verbose_name="Задача",
    )
    number = models.IntegerField(
        db_column="number", default=1, blank=True, verbose_name="Порядковый номер"
    )

    class Meta:
        db_table = 'manager"."task_sequence'
        verbose_name = "Последовательность задач"
        verbose_name_plural = "Последовательности задач"


class TaskStatusModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")
    system_name = models.TextField(
        db_column="system_name", verbose_name="Системное наименование"
    )

    class Meta:
        db_table = 'manager"."task_status'
        verbose_name = "Статус выполнения задачи"
        verbose_name_plural = "Статусы выполнения задачи"
