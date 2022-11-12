from django.urls import path
from .views import Vocab, VocabEdit, VocabDelete, VocabQuizView, VocabQuizResult

app_name = 'vocabapp'

urlpatterns = [      
    path('', Vocab.as_view(), name="vocab-board-view"),  
    path('vocab-edit/<int:id>', VocabEdit.as_view(), name="vocab-edit"),  
    path('vocab-delete/<int:id>', VocabDelete.as_view(), name="vocab-delete"),  
    path('vocab-quiz/', VocabQuizView.as_view(), name="vocab-quiz"),   
    path('vocab-quiz-result/', VocabQuizResult.as_view(), name="vocab-quiz-result"),  
]