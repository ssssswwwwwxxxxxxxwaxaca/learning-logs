from django import forms
from django.forms import ModelForm

from .models import Topic, Entry, Comment, LearningPath, PathStep, StepResource

class TopicForm(forms.ModelForm):
    class Meta:
        model=Topic
        fields=['text']
        labels={'text':''}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text', 'completed']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'text': 'Entry:',
            'completed': '标记为已完成',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment here...'}),
        }
        labels = {
            'text': '',
        }

class LearningPathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ['title', 'description', 'estimated_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PathStepForm(forms.ModelForm):
    class Meta:
        model = PathStep
        fields = ['topic', 'description', 'estimated_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super(PathStepForm, self).__init__(*args, **kwargs)
        # 只显示用户自己的话题
        self.fields['topic'].queryset = Topic.objects.filter(owner=user)

class StepResourceForm(forms.ModelForm):
    class Meta:
        model = StepResource
        fields = ['title', 'url', 'resource_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


#处理ai的表单
class AIQuestionForm(forms.Form):
    """AI问题表单"""
    question=forms.CharField(
        widget=forms.Textarea(attrs={'rows':3,'placeholder':'Please enter your question here...'})
        ,label='Your Question'
    )
    
    
class AIFeatureForm(forms.Form):
    """AI功能表单"""
    FEATURE_CHOICES=[
        ('topic_summary','Topic Summary'),
        ('quiz','Quiz'),
        ('recommendation','Get Learning Recommendation')
    ]
    feature_type=forms.ChoiceField(
        choices=FEATURE_CHOICES,
        widget=forms.RadioSelect,
        label="Select a Feature"
    )
    