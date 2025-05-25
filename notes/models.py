from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import strip_tags


class Tag(models.Model):
    """标签模型"""
    name = models.CharField('名称', max_length=50)
    color = models.CharField('颜色', max_length=7, default='#3498db')  # 使用 HEX 颜色码
    parent = models.ForeignKey('self', verbose_name='父标签', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """返回完整的标签路径"""
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return self.name


class Note(models.Model):
    """笔记模型"""
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    content = models.TextField('内容')
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True, related_name='notes')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_favorited = models.BooleanField('是否收藏', default=False)
    
    class Meta:
        verbose_name = '笔记'
        verbose_name_plural = '笔记'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.content[:50]}..."
    
    @property
    def short_content(self):
        """返回简短内容用于预览"""
        text_content = strip_tags(self.content)
        if len(text_content) > 100:
            return f"{text_content[:100]}..."
        return text_content


class Attachment(models.Model):
    """附件模型"""
    note = models.ForeignKey(Note, verbose_name='笔记', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField('文件', upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField('文件名', max_length=255)
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '附件'
        verbose_name_plural = '附件'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.filename 