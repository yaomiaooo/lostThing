from django.urls import path
from . import views

urlpatterns = [
    # 数据统计
    path('data/stats', views.get_data_stats, name='get_data_stats'),
    
    # 备份相关
    path('backups', views.get_backups, name='get_backups'),
    path('backups/create', views.create_backup, name='create_backup'),
    path('backups/<int:backup_id>/download', views.download_backup, name='download_backup'),
    path('backups/<int:backup_id>/restore', views.restore_backup, name='restore_backup'),
    path('backups/<int:backup_id>', views.delete_backup, name='delete_backup'),
    path('backup-config', views.save_backup_config, name='save_backup_config'),
    
    # 导出相关
    path('exports', views.get_exports, name='get_exports'),
    path('exports/create', views.create_export, name='create_export'),
    path('exports/<int:task_id>/download', views.download_export, name='download_export'),
    path('exports/<int:task_id>/retry', views.retry_export, name='retry_export'),
    path('exports/<int:task_id>', views.delete_export, name='delete_export'),
    
    # 清理相关
    path('cleanup/stats', views.get_cleanup_stats, name='get_cleanup_stats'),
    path('cleanup', views.execute_cleanup, name='execute_cleanup'),
    
    # 反馈相关
    path('feedback', views.get_feedback, name='get_feedback'),
    path('feedback/<int:feedback_id>/reply', views.reply_feedback, name='reply_feedback'),
    path('feedback/<int:feedback_id>/resolve', views.resolve_feedback, name='resolve_feedback'),
]