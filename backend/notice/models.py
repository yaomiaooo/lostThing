from django.db import models

class Notice(models.Model):
    """
    公告表（notice）
    """

    title = models.CharField(
        max_length=100,
        verbose_name="公告标题"
    )

    content = models.TextField(
        verbose_name="公告内容"
    )

    priority = models.SmallIntegerField(
        default=2,
        verbose_name="优先级"
    )

    start_time = models.DateTimeField(
        verbose_name="开始时间"
    )

    end_time = models.DateTimeField(
        verbose_name="结束时间"
    )

    status = models.SmallIntegerField(
        verbose_name="状态"
    )

    create_user_id = models.BigIntegerField(
        verbose_name="创建人ID"
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        db_table = "notice"
        verbose_name = "公告"
        verbose_name_plural = "公告"


class Notification(models.Model):
    """
    站内通知表（notification）
    """

    user_id = models.BigIntegerField(
        verbose_name="用户ID"
    )

    title = models.CharField(
        max_length=100,
        verbose_name="通知标题"
    )

    content = models.TextField(
        verbose_name="通知内容"
    )

    type = models.SmallIntegerField(
        verbose_name="通知类型"
    )

    is_read = models.SmallIntegerField(
        default=0,
        verbose_name="是否已读"
    )

    related_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="关联ID"
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    read_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="阅读时间"
    )

    class Meta:
        db_table = "notification"
        verbose_name = "站内通知"
        verbose_name_plural = "站内通知"
