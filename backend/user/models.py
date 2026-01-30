from django.db import models





class User(models.Model):
    """
    用户表（user）
    """

    username = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="用户名"
    )

    password = models.CharField(
        max_length=100,
        verbose_name="密码哈希"
    )

    real_name = models.CharField(
        max_length=20,
        verbose_name="真实姓名"
    )

    phone = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="手机号"
    )

    role = models.SmallIntegerField(
        verbose_name="角色"
    )

    status = models.SmallIntegerField(
        default=1,
        verbose_name="账号状态"
    )

    first_login = models.SmallIntegerField(
        default=1,
        verbose_name="是否首次登录"
    )

    last_login_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="最后登录时间"
    )

    last_login_ip = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="最后登录IP"
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    remark = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="备注"
    )

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = "用户"


