from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.forms import modelformset_factory

from .models import Question, Choice
from .forms import QuestionForm

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
    

def add_question(request):
    """Add new question with choices"""
    ChoiceFormSet = modelformset_factory(Choice, fields=('choice_text',), extra=3,)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST)
        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save()
            choices = choice_formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
            return HttpResponseRedirect(reverse("polls:index"))
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet(queryset=Choice.objects.none())
    return render(request, 'polls/add_question.html', {'question_form': question_form, 'choice_formset': choice_formset})

