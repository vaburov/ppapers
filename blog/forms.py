from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)

class PanamaForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)
