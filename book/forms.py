from django import forms
from book.models import Review, Rental


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('content',)

class DateInput(forms.DateInput):
    input_type = 'date'

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ('return_date',)
        widgets = {
            'return_date': DateInput()
        }