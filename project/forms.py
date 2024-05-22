from .models import Proj_Comment
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Proj_Comment
        fields = ('content',)
