from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.index, name='index'),
    path('notes/add/', views.add_note, name='add_note'),
    path('notes/<int:note_id>/', views.note_detail, name='note_detail'),
    path('notes/<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('notes/<int:note_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # 标签相关
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/add/', views.add_tag, name='add_tag'),
    path('tags/<int:tag_id>/', views.tag_detail, name='tag_detail'),
    path('tags/<int:tag_id>/edit/', views.edit_tag, name='edit_tag'),
    path('tags/<int:tag_id>/delete/', views.delete_tag, name='delete_tag'),
    path('api/notes/filter-by-tag/', views.filter_notes_by_tag, name='filter_notes_by_tag'),
    
    # 搜索和回顾
    path('search/', views.search, name='search'),
    path('daily-review/', views.daily_review, name='daily_review'),
    path('random-review/', views.random_review, name='random_review'),
    
    # 账户管理
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.user_profile, name='profile'),
    
    # 星图导师API
    path('get-mentor-insights/', views.get_mentor_insights_view, name='get_mentor_insights'),

    # 导入功能
    path('import-flomo/', views.import_flomo, name='import_flomo'),
] 