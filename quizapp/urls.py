from django.urls import path
from .views import CreateQuizQues, GetQuizOwnerQuesList, QuizDetail, DeleteQuizRoom, EditQuizBigQuestion, GetQuizRoomList, QuizDetailSolveRoom, QuizSubmitAnswers, QuizScoreList, QuizScoreView, QuizStudentScoreList

app_name = 'quizapp'

urlpatterns = [    
    path('create-quiz/', CreateQuizQues.as_view(), name="create-reading-data"),
    path('delete-quiz-room/<int:id>', DeleteQuizRoom.as_view(), name="delete-quiz-room"),
    path('get-owner-quiz-list/', GetQuizOwnerQuesList.as_view(), name="get-owner-quiz-list"),
    path('quiz-detail/<int:id>/<int:quesid>', QuizDetail.as_view(), name="quiz-detail"),
    path('edit-quiz-big-question/<int:id>', EditQuizBigQuestion.as_view(), name="edit-quiz-big-question"),
    path('get-quiz-room-list/', GetQuizRoomList.as_view(), name="get-quiz-room-list"),
    path('quiz-detail-solveroom/<int:id>/<int:quesid>', QuizDetailSolveRoom.as_view(), name="quiz-detail"),
    path('quiz-submit-answers/<int:id>', QuizSubmitAnswers.as_view(), name="quiz-submit-answers"),
    path('quiz-score-list/', QuizScoreList.as_view(), name="quiz-score-list"),
    path('quiz-score-view/<int:id>', QuizScoreView.as_view(), name="quiz-score-view"),
    path('quiz-student-score-list/', QuizStudentScoreList.as_view(), name="quiz-student-score-list"),
]