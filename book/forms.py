from django import forms
from book.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('content',)