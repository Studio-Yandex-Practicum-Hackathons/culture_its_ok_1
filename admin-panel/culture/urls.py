from culture.views import take_survey
from django.urls import path

app_name = 'culture'

urlpatterns = [
    path('survey/<int:progress_id>/', take_survey, name='survey'),
]
