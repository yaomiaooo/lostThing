from django.db import models


class Item(models.Model):
    """
    物品信息表（item）
    """

    # 发布人 ID（关联 user 表 id）
    user_id = models.BigIntegerField(
        verbose_name="发布人ID"
    )

    # 物品类型（关联 category 表 id）
    item_type = models.SmallIntegerField(
        verbose_name="物品类型ID"
    )

    # 信息类型：1-失物，2-招领
    item_category = models.SmallIntegerField(
        verbose_name="信息类型"
    )

    # 物品名称
    name = models.CharField(
        max_length=50,
        verbose_name="物品名称"
    )

    # 丢失 / 拾取地点 ID（关联 location 表 id）
    location_id = models.BigIntegerField(
        verbose_name="地点ID"
    )

    # 丢失 / 拾取时间
    happen_time = models.DateTimeField(
        verbose_name="发生时间"
    )

    # 物品特征描述
    feature = models.TextField(
        verbose_name="物品特征描述"
    )

    # 悬赏金额（仅失物有效）
    reward_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="悬赏金额"
    )

    # 悬赏说明
    reward_desc = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="悬赏说明"
    )

    # 联系人姓名
    contact_name = models.CharField(
        max_length=20,
        verbose_name="联系人姓名"
    )

    # 联系人电话
    contact_phone = models.CharField(
        max_length=11,
        verbose_name="联系人电话"
    )

    # 当前状态
    current_status = models.SmallIntegerField(
        verbose_name="当前状态"
    )

    # 驳回原因
    reject_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="驳回原因"
    )

    # 归档说明
    archive_desc = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="归档说明"
    )

    # 创建时间
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    # 更新时间
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    # 审核人 ID
    audit_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="审核人ID"
    )

    # 审核时间
    audit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="审核时间"
    )

    class Meta:
        db_table = "item"
        verbose_name = "物品信息"
        verbose_name_plural = "物品信息" 


class ItemImage(models.Model):
    """
    物品图片表（item_image）
    """

    item_id = models.BigIntegerField(
        verbose_name="物品ID"
    )

    image_url = models.CharField(
        max_length=255,
        verbose_name="图片地址"
    )

    image_type = models.SmallIntegerField(
        verbose_name="图片类型"
    )

    sort = models.SmallIntegerField(
        verbose_name="排序"
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    class Meta:
        db_table = "item_image"
        verbose_name = "物品图片"
        verbose_name_plural = "物品图片"


class ItemStatusHistory(models.Model):
    """
    物品状态历史表（item_status_history）
    """

    item_id = models.BigIntegerField(
        verbose_name="物品ID"
    )

    old_status = models.SmallIntegerField(
        verbose_name="原状态"
    )

    new_status = models.SmallIntegerField(
        verbose_name="新状态"
    )

    operator_id = models.BigIntegerField(
        verbose_name="操作人ID"
    )

    operator_type = models.SmallIntegerField(
        verbose_name="操作人类型"
    )

    operate_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="操作原因"
    )

    operate_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="操作时间"
    )

    class Meta:
        db_table = "item_status_history"
        verbose_name = "物品状态历史"
        verbose_name_plural = "物品状态历史"

class Category(models.Model):
    """
    分类表（category）
    """

    name = models.CharField(
        max_length=50,
        verbose_name="分类名称"
    )

    parent_id = models.BigIntegerField(
        verbose_name="父分类ID"
    )

    sort = models.SmallIntegerField(
        verbose_name="排序"
    )

    status = models.SmallIntegerField(
        default=1,
        verbose_name="状态"
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
        db_table = "category"
        verbose_name = "分类"
        verbose_name_plural = "分类"


class Location(models.Model):
    """
    地点表（location）
    """

    name = models.CharField(
        max_length=100,
        verbose_name="地点名称"
    )

    parent_id = models.BigIntegerField(
        verbose_name="父地点ID"
    )

    sort = models.SmallIntegerField(
        verbose_name="排序"
    )

    status = models.SmallIntegerField(
        default=1,
        verbose_name="状态"
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
        db_table = "location"
        verbose_name = "地点"
        verbose_name_plural = "地点"


class Claim(models.Model):
    """
    认领申请表（claim）
    """

    item_id = models.BigIntegerField(
        verbose_name="物品ID"
    )

    claim_user_id = models.BigIntegerField(
        verbose_name="认领人ID"
    )

    proof_feature = models.TextField(
        verbose_name="证明特征"
    )

    status = models.SmallIntegerField(
        verbose_name="状态"
    )

    reject_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="驳回原因"
    )

    audit_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="审核人ID"
    )

    audit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="审核时间"
    )

    claim_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="认领时间"
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
        db_table = "claim"
        verbose_name = "认领申请"
        verbose_name_plural = "认领申请"


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


class OperationLog(models.Model):
    """
    操作日志表（operation_log）
    """

    user_id = models.BigIntegerField(
        verbose_name="用户ID"
    )

    user_role = models.SmallIntegerField(
        verbose_name="用户角色"
    )

    module = models.CharField(
        max_length=50,
        verbose_name="操作模块"
    )

    operation = models.CharField(
        max_length=50,
        verbose_name="操作名称"
    )

    related_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="关联ID"
    )

    content = models.TextField(
        verbose_name="操作内容"
    )

    ip_address = models.CharField(
        max_length=50,
        verbose_name="IP地址"
    )

    operation_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="操作时间"
    )

    class Meta:
        db_table = "operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"





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


