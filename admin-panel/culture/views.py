from datetime import datetime, timedelta

from culture.forms import SurveyForm
from culture.models import Progress, Survey
from django.http import Http404
from django.shortcuts import get_object_or_404, render

MIN_TO_TAKE_SURVEY = 15


def take_survey(request, progress_id: int):
    progress = get_object_or_404(Progress, id=progress_id)

    # проверяем, что пользователь ещё не проходил данный опрос
    if Survey.objects.filter(progress_id=progress_id).exists():
        raise Http404

    # проверяем, что пользователь закончил маршрут недавно
    now = datetime.now(tz=progress.finished_at.tzinfo)
    if now - timedelta(minutes=MIN_TO_TAKE_SURVEY) > progress.finished_at:
        raise Http404

    template = 'survey.html'
    form = SurveyForm(request.POST or None)

    if form.is_valid():
        new_survey = form.save(commit=False)
        new_survey.progress_id = progress_id
        new_survey.save()
        return render(request, 'thankyou.html')

    context = {
        'form': form
    }
    return render(request, template, context)
