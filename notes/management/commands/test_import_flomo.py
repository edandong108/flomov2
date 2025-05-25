from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from notes.models import Note, Tag
from bs4 import BeautifulSoup
from django.utils.timezone import make_aware
from datetime import datetime
import os
import re
import traceback

class Command(BaseCommand):
    help = '测试Flomo导入功能'

    def add_arguments(self, parser):
        parser.add_argument('test_file', type=str, help='测试用的HTML文件路径')

    def _process_tag_path(self, tag_path, note, tag_cache):
        """处理标签路径，创建标签层级关系"""
        parts = [p.strip() for p in tag_path.split('/')]
        parent = None
        full_path = ''
        
        for part in parts:
            if not part:
                continue
                
            full_path = (full_path + '/' + part).lstrip('/')
            if full_path in tag_cache:
                tag = tag_cache[full_path]
            else:
                tag = Tag.objects.create(name=part, parent=parent)
                tag_cache[full_path] = tag
            parent = tag
            note.tags.add(tag)

    def handle(self, *args, **options):
        test_file = options['test_file']
        print(f'开始测试导入: {test_file}')

        try:
            # 创建测试用户
            test_user, created = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            if created:
                test_user.set_password('test123')
                test_user.save()
                print('创建测试用户成功')
            else:
                print('使用已存在的测试用户')

            if not os.path.exists(test_file):
                print(f'测试文件不存在: {test_file}')
                return

            try:
                # 清理之前的测试数据
                notes_count = Note.objects.filter(user=test_user).count()
                tags_count = Tag.objects.count()
                Note.objects.filter(user=test_user).delete()
                Tag.objects.all().delete()
                print(f'清理测试数据: {notes_count} 条笔记, {tags_count} 个标签')

                # 读取测试文件
                print('正在读取测试文件...')
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f'文件大小: {len(content)} 字节')
                    soup = BeautifulSoup(content, 'html.parser')

                # 获取所有笔记
                memos = soup.find_all('div', class_='memo')
                total_count = len(memos)
                print(f'找到 {total_count} 条测试笔记')

                # 创建标签缓存
                tag_cache = {}
                success_count = 0
                error_count = 0

                # 处理每条笔记
                for i, memo in enumerate(memos, 1):
                    try:
                        print(f'处理第 {i}/{total_count} 条笔记...')
                        
                        # 解析时间
                        time_div = memo.find('div', class_='time')
                        if not time_div:
                            raise ValueError('找不到时间信息')
                        time_str = time_div.text.strip()
                        created_at = make_aware(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S'))

                        # 解析内容 - 保留HTML格式
                        content_div = memo.find('div', class_='content')
                        if not content_div:
                            raise ValueError('找不到内容信息')
                        
                        # 直接获取content_div的内部HTML内容
                        content_html = content_div.decode_contents()
                        # 提取纯文本用于标签处理
                        content_text = content_div.get_text('\n', strip=True)

                        # 创建笔记 - 使用HTML内容
                        note = Note.objects.create(
                            user=test_user,
                            content=content_html,
                            created_at=created_at,
                            updated_at=created_at
                        )
                        print(f'  - 创建笔记成功: ID={note.id}')

                        # 处理标签
                        tag_pattern = r'#([^#\n]+)'
                        tags = re.findall(tag_pattern, content_text)
                        for tag_path in tags:
                            tag_path = tag_path.strip()
                            if tag_path:
                                self._process_tag_path(tag_path, note, tag_cache)
                                print(f'  - 处理标签: {tag_path}')

                        success_count += 1

                    except Exception as e:
                        error_count += 1
                        print(f'\n处理第 {i} 条笔记时出错:')
                        print(str(e))
                        print(traceback.format_exc())

                # 打印导入统计
                print('\n' + '='*50)
                print('测试完成！')
                print(f'总计笔记: {total_count} 条')
                print(f'成功导入: {success_count} 条')
                print(f'导入失败: {error_count} 条')
                print(f'标签数量: {len(tag_cache)} 个')

                # 验证导入数据
                print('\n验证导入数据:')
                print(f'- 笔记总数: {Note.objects.filter(user=test_user).count()}')
                print(f'- 总标签数: {Tag.objects.count()}')
                print(f'- 一级标签数: {Tag.objects.filter(parent=None).count()}')
                max_level = 1
                tags = Tag.objects.all()
                for tag in tags:
                    level = 1
                    parent = tag.parent
                    while parent:
                        level += 1
                        parent = parent.parent
                    max_level = max(max_level, level)
                print(f'- 最大标签层级: {max_level}')

            except Exception as e:
                print(f'导入过程出错: {str(e)}')
                print(traceback.format_exc())

        except Exception as e:
            print(f'测试过程出错: {str(e)}')
            print(traceback.format_exc()) 