from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notes.models import Note, Tag
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = '从Flomo HTML文件导入笔记'

    def add_arguments(self, parser):
        parser.add_argument('html_file', type=str, help='HTML文件路径')
        parser.add_argument('username', type=str, help='导入到哪个用户名下')

    def handle(self, *args, **options):
        html_file = options['html_file']
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户 {username} 不存在'))
            return

        # 读取HTML文件
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        memos = soup.find_all('div', class_='memo')

        tag_cache = {}  # 用于缓存已创建的标签
        imported_count = 0

        for memo in memos:
            content_div = memo.find('div', class_='content')
            if not content_div:
                continue

            # 获取时间
            time_div = memo.find('div', class_='time')
            if time_div:
                time_str = time_div.text.strip()
                try:
                    created_at = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    created_at = pytz.timezone('Asia/Shanghai').localize(created_at)
                except ValueError:
                    created_at = None
            
            # 解析内容
            content_html = str(content_div)
            
            # 提取标签
            tags = []
            tag_pattern = re.compile(r'#([^#\s<>]+)')
            for p in content_div.find_all('p'):
                p_text = p.get_text()
                tag_matches = tag_pattern.findall(p_text)
                for tag_path in tag_matches:
                    tag_path = tag_path.strip()
                    if tag_path:
                        self._process_tag_path(tag_path, tags, tag_cache)

            # 创建笔记
            note = Note.objects.create(
                user=user,
                content=content_html,
                created_at=created_at or None
            )
            
            # 添加标签
            for tag in tags:
                note.tags.add(tag)

            imported_count += 1
            if imported_count % 50 == 0:
                self.stdout.write(f'已导入 {imported_count} 条笔记...')

        self.stdout.write(self.style.SUCCESS(f'成功导入 {imported_count} 条笔记和 {len(tag_cache)} 个标签'))

    def _process_tag_path(self, tag_path, tags, tag_cache):
        """处理标签路径，创建多级标签"""
        parts = [part.strip() for part in tag_path.split('/') if part.strip()]
        if not parts:
            return

        parent = None
        current_path = ''
        
        for i, part in enumerate(parts):
            current_path = current_path + '/' + part if current_path else part
            
            if current_path in tag_cache:
                tag = tag_cache[current_path]
            else:
                # 查找或创建标签
                tag, created = Tag.objects.get_or_create(
                    name=part,
                    parent=parent,
                    defaults={'color': '#3498db'}  # 默认颜色
                )
                tag_cache[current_path] = tag
            
            parent = tag
            
            # 将最后一级标签添加到笔记中
            if i == len(parts) - 1:
                tags.append(tag) 