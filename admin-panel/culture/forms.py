from culture.models import Survey
from django import forms


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ('most_memorable', 'emotions', 'proposal')
