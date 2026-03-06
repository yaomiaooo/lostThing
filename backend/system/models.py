from django.db import models
from user.models import User


class Feedback(models.Model):
    """
    用户反馈表
    """
    TYPE_CHOICES = [
        ('technical', '技术问题'),
        ('usage', '使用问题'),
        ('suggestion', '意见建议'),
        ('other', '其他'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='用户')
    feedback_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other', verbose_name='问题类型')
    content = models.TextField(verbose_name='反馈内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    reply = models.TextField(blank=True, null=True, verbose_name='管理员回复')
    reply_time = models.DateTimeField(blank=True, null=True, verbose_name='回复时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'feedback'
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'
        ordering = ['-create_time']


class BackupRecord(models.Model):
    """
    数据备份记录表
    """
    BACKUP_TYPE_CHOICES = [
        ('full', '全量备份'),
        ('incremental', '增量备份'),
    ]
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('processing', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    name = models.CharField(max_length=255, verbose_name='备份名称')
    backup_type = models.CharField(
        max_length=20, 
        choices=BACKUP_TYPE_CHOICES, 
        default='full',
        verbose_name='备份类型'
    )
    file_path = models.CharField(max_length=500, verbose_name='文件路径')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    tables = models.JSONField(default=list, verbose_name='包含的表')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='状态'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    created_by = models.BigIntegerField(verbose_name='创建人ID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_time = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')

    class Meta:
        db_table = 'backup_record'
        verbose_name = '备份记录'
        verbose_name_plural = '备份记录'
        ordering = ['-created_time']


class ExportTask(models.Model):
    """
    数据导出任务表
    """
    FORMAT_CHOICES = [
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('processing', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    name = models.CharField(max_length=255, verbose_name='任务名称')
    data_types = models.JSONField(default=list, verbose_name='数据类型')
    export_format = models.CharField(
        max_length=20, 
        choices=FORMAT_CHOICES, 
        default='excel',
        verbose_name='导出格式'
    )
    date_range_start = models.DateTimeField(blank=True, null=True, verbose_name='开始日期')
    date_range_end = models.DateTimeField(blank=True, null=True, verbose_name='结束日期')
    include_images = models.BooleanField(default=False, verbose_name='包含图片')
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='文件路径')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    record_count = models.IntegerField(default=0, verbose_name='记录数')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='状态'
    )
    progress = models.IntegerField(default=0, verbose_name='进度(%)')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    created_by = models.BigIntegerField(verbose_name='创建人ID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_time = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')

    class Meta:
        db_table = 'export_task'
        verbose_name = '导出任务'
        verbose_name_plural = '导出任务'
        ordering = ['-created_time']


class OperationLog(models.Model):
    """
    操作日志表
    """
    OPERATION_TYPE_CHOICES = [
        ('backup', '数据备份'),
        ('restore', '数据恢复'),
        ('export', '数据导出'),
        ('cleanup', '数据清理'),
    ]

    operation_type = models.CharField(
        max_length=50, 
        choices=OPERATION_TYPE_CHOICES,
        verbose_name='操作类型'
    )
    operation_detail = models.TextField(verbose_name='操作详情')
    ip_address = models.CharField(max_length=50, verbose_name='IP地址')
    user_id = models.BigIntegerField(verbose_name='用户ID')
    user_name = models.CharField(max_length=100, verbose_name='用户名')
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'system_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-operation_time']