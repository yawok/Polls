from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last 5 published questions up until now(not including future questions)."""
        return Question.objects.filter(pub_date__lte=timezone.now()).filter().order_by('-pub_date').exclude(choice__isnull=True)[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__isnull=True)



class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """Exclude all questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__isnull=True)


def vote(request, question_id):
    """Voting page for question choices."""
    queryset = Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__isnull=True)
    question = get_object_or_404(queryset, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html", {'question': question, "error_message": "You didn't select a choice."})
    else:
        # To avoid race condition
        selected_choice.vote = F("vote") + 1
        selected_choice.save()
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    


