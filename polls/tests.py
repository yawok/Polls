from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

import datetime, threading

from .models import Question, Choice

class QuestionModelTests(TestCase):
    """Test Question model."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently returns False for questions yet to be published."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently returns False for questions published 1 or more days ago."""
        time = timezone.now() - datetime.timedelta(days=1)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        """was_published_recently returns True for questions published within the last 24 hours."""
        time = timezone.now() - datetime.timedelta(days=1)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)
        
def create_question(question_text, days):
    """Create a new question with question text and days ofset to now.(- for past dates and vice versa)"""

    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text):
    """Create a choice for the given question with the given choice_text."""
    return Choice.objects.create(question=question, choice_text=choice_text)

class QuestionIndexViewTests(TestCase):
    """Test Question index view"""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_question_with_no_choice(self):
        """Questions with no choices are not displayed on the index page."""
        create_question("Past Question?", -20)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    
    def test_past_questions(self):
        """Questions with past pub_dates are displayed on the index page."""
        question = create_question("Past Question?", -20)
        create_choice(question, "Test choice")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])


    def test_future_questions(self):
        """Questions with future pub_dates are not displayed on the index page"""
        future_question = create_question("Future question?", 20)
        create_choice(future_question, "Test choice")
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    
    def test_future_and_past_questions(self):
        """Display only questions with past pub_dates on the index page."""
        question = create_question("Past question?", -5)
        create_question("Future question?", +5)
        create_choice(question, "Test choice")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    
    def test_two_past_questions(self):
        """Display 2 questions with past pub_dates on the index page."""
        
        question1 = create_question("Past question 1?", -5)
        question2 = create_question("Past question 2?", -4)
        create_choice(question1, "Test choice1")
        create_choice(question2, "Test choice2")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1])


class QuestionDetailViewTests(TestCase):
    """Test question detail view."""
    def test_future_question(self):
        """Display no future question details."""
        future_question = create_question("Future question?", 34)
        create_choice(future_question, "Test choice")
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    
    def test_past_question(self):
        """Display details of a past question."""
        past_question = create_question("Past Question?", -3)
        create_choice(past_question, "Test choice")
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        
    
    def test_past_question_with_no_choices(self):
        """Display no details of a past question without choices."""
        past_question = create_question("Past Question?", -3)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    
class ResultsDetailViewTests(TestCase):
    """Test results detail view."""
    def test_past_question_results(self):
        """Display results of a past question."""
        past_question = create_question("Past Question?", -3)
        create_choice(past_question, "Test choice")
        response = self.client.get(reverse('polls:results', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)

        
    def test_past_question_with_no_choices_results(self):
        """Display no results of a past question without choices."""
        past_question = create_question("Past Question?", -3)
        response = self.client.get(reverse('polls:results', args=(past_question.id,)))
        self.assertEqual(response.status_code, 404)

    
    def test_future_question(self):
        """Display no results for a future question."""
        future_question = create_question("Future Question?", 4)
        create_choice(future_question, "Test choice")
        response = self.client.get(reverse('polls:results', args=(future_question.id, )))
        self.assertEqual(response.status_code, 404)
        

class VoteViewTests(TestCase):
    """Tests for the vote view."""
    def test_vote_for_previous_question(self):
        """Cast for for a published question."""
        question = create_question("Vote", -3)
        choice = create_choice(question, "Choice 1")
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(url, {"choice": "1",} )
        self.assertEqual(response.status_code, 302)
        choice = Choice.objects.get(pk=1)
        self.assertEqual(choice.vote, 1)

        
    def test_vote_for_previous_question_with_no_choices(self):
        """Restrict voting for a published question without choices."""
        question = create_question("Vote", -3)
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(url, {"choice": "1",} )
        self.assertEqual(response.status_code, 404)
        
        
    def test_vote_for_future_question(self):
        """Restrict voting for questions yet to be published."""
        question = create_question("Vote", 3)
        choice = create_choice(question, "Choice 1")
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(url, {"choice": "1",} )
        self.assertEqual(response.status_code, 404)
        choice = Choice.objects.get(pk=1)
        self.assertEqual(choice.vote, 0)
            
    
       
        
        