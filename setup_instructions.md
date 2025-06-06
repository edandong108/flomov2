# Flomo2 项目安装和使用说明

## 安装步骤

1. **安装Python**
   - 下载并安装Python 3.8+: https://www.python.org/downloads/
   - 确保将Python添加到PATH环境变量中

2. **安装项目依赖**
   ```
   pip install -r requirements.txt
   ```

3. **数据库迁移**
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **创建超级用户**
   ```
   python manage.py createsuperuser
   ```
   按照提示输入用户名、邮箱和密码

5. **运行开发服务器**
   ```
   python manage.py runserver
   ```

6. **访问应用**
   - 在浏览器中打开: http://127.0.0.1:8000

## 功能使用说明

### 快速记录
- 在首页的记录框中输入内容，直接点击"保存"按钮
- 也可以使用右下角的"+"按钮，在任何页面快速添加笔记

### 多级标签
- 在记录笔记时，可以在标签输入框中添加标签
- 使用逗号分隔多个标签，如：`工作, 学习, 生活`
- 使用斜杠表示层级关系，如：`工作/项目/任务A`
- 在"标签管理"页面可以编辑、删除和整理标签

### 每日回顾
- 在导航栏的"回顾"下拉菜单中选择"每日回顾"
- 系统会自动显示往年今天的笔记内容
- 帮助重温过去的想法和记录

### 随机回顾
- 在导航栏的"回顾"下拉菜单中选择"随机回顾"
- 系统会随机展示以前的笔记内容
- 点击"再来一组"按钮获取新的随机笔记

### 搜索功能
- 使用导航栏的"搜索"或首页右侧的搜索框
- 支持按关键词、标签、日期范围和收藏状态搜索
- 高级搜索功能可以组合多个条件

## 最佳实践

1. **有效使用标签**
   - 建立一个合理的标签体系，避免创建过于相似的标签
   - 使用多级标签来组织相关内容

2. **定期回顾**
   - 养成每天查看"每日回顾"的习惯
   - 定期使用"随机回顾"功能发现过去的灵感

3. **持续记录**
   - 养成随时记录想法的习惯
   - 不必担心格式和排版，重点是捕捉思想

4. **及时整理**
   - 定期整理和归类笔记
   - 为重要的笔记添加适当的标签

## 常见问题

**Q: 如何修改已创建的笔记?**
A: 在笔记列表中点击"编辑"按钮，修改后保存即可。

**Q: 如何导出我的笔记?**
A: 目前暂不支持导出功能，将在未来版本中添加。

**Q: 如何更改密码?**
A: 在个人资料页面可以修改密码和其他账户信息。 