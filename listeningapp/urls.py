from django.urls import path
from .views import ListeningDataCreate, ListeningBoardList, ListeningBoardView, ListeningBlankCreate, ListeningBlankGrade,ListeningDataEdit, ListeningDataDelete, ListeningGetData


app_name = 'listeningapp'

urlpatterns = [
    path('listening-create-scripts/', ListeningDataCreate.as_view(), name="create-listening-data"),
    path('', ListeningBoardList.as_view(), name="listening-board-list-data"),
    path('listening-view-scripts/', ListeningBoardView.as_view(), name="listening-view-data"),
    path('listening-edit-scripts/<int:id>', ListeningDataEdit.as_view(), name="listening-edit-data"),
    path('listening-delete-scripts/<int:id>', ListeningDataDelete.as_view(), name= "listening-delete-data"),
    path('listening-get-data/<int:id>', ListeningGetData.as_view(), name= "for-listening-delete-data-url"),
    path('listening-blank-create/', ListeningBlankCreate.as_view(), name="listening-create-blank"),
    path('listening-blank-grade/', ListeningBlankGrade.as_view(), name= "listening-grade-blank")
]