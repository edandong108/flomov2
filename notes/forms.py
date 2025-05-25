from django import forms
from django.utils.text import slugify
from .models import Note, Tag, Attachment


class NoteForm(forms.ModelForm):
    """笔记表单"""
    tag_input = forms.CharField(
        label='标签',
        required=False,
        help_text='使用逗号分隔多个标签，使用斜杠表示层级关系（如：工作/项目/任务）',
        widget=forms.TextInput(attrs={'class': 'tag-input', 'placeholder': '输入标签，用逗号分隔'})
    )
    
    class Meta:
        model = Note
        fields = ['content', 'is_favorited']
        widgets = {
            'content': forms.HiddenInput(),  # 使用隐藏字段，内容由 Quill 编辑器提供
            'is_favorited': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def save(self, commit=True, user=None):
        note = super().save(commit=False)
        if user:
            note.user = user
        
        if commit:
            note.save()
            
            # 处理标签
            if self.cleaned_data.get('tag_input'):
                tag_names = [tag.strip() for tag in self.cleaned_data['tag_input'].split(',') if tag.strip()]
                for tag_path in tag_names:
                    self._process_tag_path(tag_path, note)
                    
            self.save_m2m()  # 保存多对多关系
        
        return note
    
    def _process_tag_path(self, tag_path, note):
        """处理标签路径，创建多级标签"""
        parts = [part.strip() for part in tag_path.split('/') if part.strip()]
        if not parts:
            return
        
        parent = None
        for i, part in enumerate(parts):
            # 查找或创建标签
            tag, created = Tag.objects.get_or_create(
                name=part,
                parent=parent,
                defaults={'color': '#3498db'}  # 默认颜色
            )
            parent = tag
            
            # 将最后一级标签添加到笔记中
            if i == len(parts) - 1:
                note.tags.add(tag)


class TagForm(forms.ModelForm):
    """标签表单"""
    class Meta:
        model = Tag
        fields = ['name', 'parent', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class AttachmentForm(forms.ModelForm):
    """附件表单"""
    class Meta:
        model = Attachment
        fields = ['file']
        
    def save(self, commit=True, note=None):
        attachment = super().save(commit=False)
        if note:
            attachment.note = note
        
        # 设置文件名
        if attachment.file:
            attachment.filename = attachment.file.name
            
        if commit:
            attachment.save()
        
        return attachment


class SearchForm(forms.Form):
    """搜索表单"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '搜索笔记...'
        })
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    is_favorited = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ImportFlomoForm(forms.Form):
    """Flomo导入表单"""
    html_file = forms.FileField(
        label='HTML文件',
        help_text='请选择从Flomo导出的HTML文件',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.html'
        })
    ) 