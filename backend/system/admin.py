from django.contrib import admin
from .models import BackupRecord, ExportTask, OperationLog

admin.site.register(BackupRecord)
admin.site.register(ExportTask)
admin.site.register(OperationLog)