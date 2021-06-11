from django.contrib import admin

from manager import models

admin.site.register(models.BaseTaskModel)
admin.site.register(models.BaseTaskLogModel)
admin.site.register(models.TaskModel)
admin.site.register(models.TaskStatusModel)
admin.site.register(models.TaskSequenceModel)
admin.site.register(models.ActionModel)
