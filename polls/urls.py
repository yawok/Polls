from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name="detail"),
    path('<int:pk>/results/', views.ResultsView.as_view(), name="results"),
    path('<int:question_id>/vote/', views.vote, name="vote"),
    path('add_question/', views.add_question, name="add_question"),
    path('published_questions/', views.PublishedQuestionsView.as_view(), name="published_questions"),

]