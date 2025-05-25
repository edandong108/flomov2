from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
import random
import datetime
from django.db.models import Count
from django.core.management import call_command
from django.core.files.storage import default_storage
from .forms import ImportFlomoForm
import tempfile
import os
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import Note, Tag, Attachment
from .forms import NoteForm, TagForm, AttachmentForm, SearchForm
from .utils import get_mentor_advice, get_mentor_insights


def index(request):
    """首页视图，显示最近的笔记"""
    if request.user.is_authenticated:
        # 获取所有笔记
        all_notes = Note.objects.filter(user=request.user).order_by('-created_at')
        
        # 设置分页，每页20条
        paginator = Paginator(all_notes, 20)
        page = request.GET.get('page', 1)
        notes = paginator.get_page(page)
        
        form = NoteForm()
        tags = Tag.objects.filter(parent=None)
        
        # 生成日历热力图数据
        today = timezone.now().date()
        start_date = today - datetime.timedelta(days=90)  # 显示最近90天
        
        # 获取日期范围内的笔记数量
        notes_by_date = Note.objects.filter(
            user=request.user,
            created_at__date__gte=start_date,
            created_at__date__lte=today
        ).values('created_at__date').annotate(count=Count('id'))
        
        # 转换为字典格式，方便查找
        notes_count_dict = {item['created_at__date']: item['count'] for item in notes_by_date}
        
        # 生成日历网格数据
        calendar_data = []
        current_date = start_date
        
        # 计算最大笔记数，用于颜色渐变
        max_count = max(notes_count_dict.values()) if notes_count_dict else 1
        
        while current_date <= today:
            week = []
            for _ in range(7):  # 一周7天
                count = notes_count_dict.get(current_date, 0)
                # 根据笔记数量计算颜色
                if count == 0:
                    color = '#ebedf0'
                else:
                    intensity = min(count / max_count, 1.0)  # 归一化到0-1之间
                    if intensity < 0.25:
                        color = '#9be1ff'
                    elif intensity < 0.5:
                        color = '#40a9ff'
                    elif intensity < 0.75:
                        color = '#1890ff'
                    else:
                        color = '#0050b3'
                
                week.append({
                    'date': current_date,
                    'count': count,
                    'color': color
                })
                current_date += datetime.timedelta(days=1)
            calendar_data.append(week)
        
        # 获取总笔记数
        total_notes = all_notes.count()
        
        return render(request, 'notes/index.html', {
            'notes': notes,
            'form': form,
            'tags': tags,
            'calendar_data': calendar_data,
            'total_notes': total_notes,
        })
    else:
        return render(request, 'notes/welcome.html')


@login_required
def add_note(request):
    """添加笔记"""
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(user=request.user)
            
            # 处理附件
            files = request.FILES.getlist('file')
            for file in files:
                attachment = Attachment(note=note, file=file, filename=file.name)
                attachment.save()
                
            messages.success(request, '笔记已保存')
            
            # AJAX请求返回JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'note_id': note.id})
            return redirect('notes:index')
    else:
        form = NoteForm()
    
    return render(request, 'notes/add_note.html', {'form': form})


@login_required
def note_detail(request, note_id):
    """笔记详情"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required
def edit_note(request, note_id):
    """编辑笔记"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            
            # 处理附件
            files = request.FILES.getlist('file')
            for file in files:
                attachment = Attachment(note=note, file=file, filename=file.name)
                attachment.save()
                
            messages.success(request, '笔记已更新')
            return redirect('notes:note_detail', note_id=note.id)
    else:
        # 提取标签为格式化字符串
        tag_input = ', '.join([tag.full_path for tag in note.tags.all()])
        form = NoteForm(instance=note, initial={'tag_input': tag_input})
    
    return render(request, 'notes/edit_note.html', {'form': form, 'note': note})


@login_required
def delete_note(request, note_id):
    """删除笔记"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, '笔记已删除')
        return redirect('notes:index')
    
    return render(request, 'notes/delete_note.html', {'note': note})


@login_required
def toggle_favorite(request, note_id):
    """切换笔记的收藏状态"""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_favorited = not note.is_favorited
    note.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_favorited': note.is_favorited})
    
    return redirect('notes:note_detail', note_id=note.id)


@login_required
def tag_list(request):
    """标签列表"""
    tags = Tag.objects.filter(parent=None)
    return render(request, 'notes/tag_list.html', {'tags': tags})


@login_required
def add_tag(request):
    """添加标签"""
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '标签已添加')
            return redirect('notes:tag_list')
    else:
        form = TagForm()
    
    return render(request, 'notes/add_tag.html', {'form': form})


@login_required
def tag_detail(request, tag_id):
    """标签详情"""
    tag = get_object_or_404(Tag, id=tag_id)
    notes = Note.objects.filter(user=request.user, tags=tag).order_by('-created_at')
    return render(request, 'notes/tag_detail.html', {'tag': tag, 'notes': notes})


@login_required
def edit_tag(request, tag_id):
    """编辑标签"""
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, '标签已更新')
            return redirect('notes:tag_detail', tag_id=tag.id)
    else:
        form = TagForm(instance=tag)
    
    return render(request, 'notes/edit_tag.html', {'form': form, 'tag': tag})


@login_required
def delete_tag(request, tag_id):
    """删除标签"""
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        tag.delete()
        messages.success(request, '标签已删除')
        return redirect('notes:tag_list')
    
    return render(request, 'notes/delete_tag.html', {'tag': tag})


@login_required
def search(request):
    """搜索笔记"""
    form = SearchForm(request.GET)
    notes = Note.objects.filter(user=request.user)
    
    if form.is_valid():
        # 关键词搜索
        query = form.cleaned_data.get('query')
        if query:
            notes = notes.filter(content__icontains=query)
        
        # 标签筛选
        tags = form.cleaned_data.get('tags')
        if tags:
            notes = notes.filter(tags__in=tags).distinct()
        
        # 日期范围筛选
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            notes = notes.filter(created_at__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            # 设置时间为23:59:59以包含整天
            date_to = datetime.datetime.combine(date_to, datetime.time.max)
            notes = notes.filter(created_at__lte=date_to)
        
        # 是否收藏筛选
        is_favorited = form.cleaned_data.get('is_favorited')
        if is_favorited:
            notes = notes.filter(is_favorited=True)
    
    notes = notes.order_by('-created_at')
    return render(request, 'notes/search.html', {'form': form, 'notes': notes})


@login_required
def daily_review(request):
    """每日回顾"""
    # 获取当前日期的不同年份的笔记
    today = timezone.now().date()
    notes_by_year = {}
    
    # 最多查找过去5年的同一天笔记
    for i in range(5):
        year_ago = today.replace(year=today.year-i-1)
        # 获取同一天的笔记（只匹配月和日）
        notes = Note.objects.filter(
            user=request.user,
            created_at__month=today.month,
            created_at__day=today.day,
            created_at__year=today.year-i-1
        ).order_by('-created_at')
        
        if notes.exists():
            notes_by_year[today.year-i-1] = notes
    
    return render(request, 'notes/daily_review.html', {'notes_by_year': notes_by_year})


@login_required
def random_review(request):
    """随机回顾"""
    # 获取用户的所有笔记
    all_notes = list(Note.objects.filter(user=request.user))
    
    # 如果没有笔记，返回空列表
    if not all_notes:
        return render(request, 'notes/random_review.html', {'notes': []})
    
    # 随机选择5条笔记（或者所有笔记，如果不足5条）
    count = min(5, len(all_notes))
    random_notes = random.sample(all_notes, count)
    
    return render(request, 'notes/random_review.html', {'notes': random_notes})


def user_login(request):
    """用户登录"""
    if request.user.is_authenticated:
        return redirect('notes:index')
    
    # 创建测试账号
    test_username = 'test'
    test_password = 'test123456'
    User = get_user_model()
    if not User.objects.filter(username=test_username).exists():
        User.objects.create_user(username=test_username, password=test_password)
        print(f"创建测试账号: {test_username} / {test_password}")
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('notes:index')
            else:
                messages.error(request, '用户名或密码不正确')
    else:
        form = AuthenticationForm()
        # 在表单下方显示测试账号信息
        messages.info(request, f'测试账号：用户名 {test_username} / 密码 {test_password}')
    
    return render(request, 'notes/login.html', {'form': form})


def user_logout(request):
    """用户登出"""
    logout(request)
    return redirect('notes:login')


def user_register(request):
    """用户注册"""
    if request.user.is_authenticated:
        return redirect('notes:index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('notes:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'notes/register.html', {'form': form})


@login_required
def user_profile(request):
    """用户个人资料"""
    user = request.user
    note_count = Note.objects.filter(user=user).count()
    tag_count = Tag.objects.filter(notes__user=user).distinct().count()
    favorite_count = Note.objects.filter(user=user, is_favorited=True).count()
    
    return render(request, 'notes/profile.html', {
        'user': user,
        'note_count': note_count,
        'tag_count': tag_count,
        'favorite_count': favorite_count,
    })


@login_required
def get_mentor_insights_view(request):
    """处理AJAX请求获取导师建议"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': '非法请求'})
        
    mentor_type = request.GET.get('mentor_type', 'zeng')
    force_refresh = request.GET.get('force_refresh') == 'true'  # 添加force_refresh参数
    result = get_mentor_insights(request.user, mentor_type, force_refresh)
    
    if not result['success']:
        return JsonResponse({
            'success': False,
            'error': '获取导师建议失败，请稍后重试'
        })
    
    return JsonResponse({
        'success': True,
        'mentor_advice': result['mentor_advice'],
        'mentor_name': result['mentor_name']
    })


@login_required
def import_flomo(request):
    """导入Flomo笔记"""
    if request.method == 'POST':
        form = ImportFlomoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 创建临时文件保存上传的HTML
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
                    for chunk in request.FILES['html_file'].chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                # 调用导入命令
                call_command('import_flomo', temp_file_path, request.user.username)
                
                # 删除临时文件
                os.unlink(temp_file_path)
                
                messages.success(request, '笔记导入成功！')
                return redirect('notes:index')
            except Exception as e:
                messages.error(request, f'导入失败：{str(e)}')
                return redirect('notes:import_flomo')
    else:
        form = ImportFlomoForm()
    
    return render(request, 'notes/import_flomo.html', {'form': form}) 