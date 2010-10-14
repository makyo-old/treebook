from django import forms

class PostForm(forms.Form):
    title = forms.CharField(max_length = 250, required = False)
    body = forms.CharField(widget = forms.Textarea)

class PostEditForm(forms.Form):
    title = forms.CharField(max_length = 250, required = False)
    body = forms.CharField(widget = forms.Textarea)
    reason = forms.CharField(max_length = 250, required = False)
