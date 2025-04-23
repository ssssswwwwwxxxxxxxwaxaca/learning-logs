from django import forms
from django.forms import ModelForm

from .models import Topic, Entry, Comment

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
