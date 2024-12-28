from django import forms
from .models import Post, Comment


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('is_published', 'author')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ('post', 'author', )
