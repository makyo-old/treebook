from django import forms
from ebook.models import *

class ChapterForm(forms.ModelForm):
    body = forms.CharField(widget = forms.Textarea({'rows': 25, 'cols': 78}))
    class Meta:
        model = Manifesto
        exclude = ('owner', 'views', 'stars', 'featured', 'weight', 'ctime')

class CommentForm(forms.ModelForm):
    body = forms.CharField(widget = forms.Textarea({'cols': 78}))
    class Meta:
        model = Comment
        exclude = ('post', 'parent', 'ctime', 'owner', 'published')
