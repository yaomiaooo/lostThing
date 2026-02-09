from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    会话表
    规则：
    - 会话由：物品 + 失主 + 拾主 唯一确定
    - 角色在创建时确定，后续不可变
    - 即使物品状态变化，会话仍可查看（但可能只读）
    """

    item = models.ForeignKey(
        'items.Item',
        on_delete=models.CASCADE,
        verbose_name="关联物品"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_conversations',
        verbose_name="失主"
    )

    finder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='finder_conversations',
        verbose_name="拾主"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    class Meta:
        db_table = 'conversation'
        verbose_name = '沟通会话'
        verbose_name_plural = '沟通会话'
        # ★ 核心规则：同一物品 + 同一失主 + 同一拾主，只能有一条会话
        unique_together = ('item', 'owner', 'finder')

    def __str__(self):
        return f'Conversation(item={self.item_id}, owner={self.owner_id}, finder={self.finder_id})'


class Message(models.Model):
    """
    消息表
    - 当前仅支持文本
    - 后续可扩展为图片 / 证明材料
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="所属会话"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="发送者"
    )

    content = models.TextField(
        verbose_name="消息内容"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="发送时间"
    )

    class Meta:
        db_table = 'message'
        verbose_name = '沟通消息'
        verbose_name_plural = '沟通消息'
        ordering = ['created_at']

    def __str__(self):
        return f'Message(conversation={self.conversation_id}, sender={self.sender_id})'
