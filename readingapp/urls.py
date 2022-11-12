from django.urls import path
from .views import ReadingDataCreate, ReadingBoardView, ReadingEditData, ReadingDeleteData, ReadingSpecEditData, ReadingShareData, ReadingGetData, ReadingVocabBoardView, ReadingVocabEdit, ReadingVocabDelete, ReadingGetFriendsData

app_name = 'readingapp'

urlpatterns = [
    path('reading-create/', ReadingDataCreate.as_view(), name="create-reading-data"),
    path('reading-view/', ReadingBoardView.as_view(), name="reading-view-data"),
    path('reading-data-edit/<int:id>', ReadingEditData.as_view(), name="reading-edit-data"),
    path('reading-delete/<int:id>', ReadingDeleteData.as_view(), name="reading-delete-data"),
    path('reading-edit-specific/<int:id>', ReadingSpecEditData.as_view(), name="reading-edit-specific-data"),
    path('reading-share/<int:id>', ReadingShareData.as_view(), name="reading-edit-specific-data"),
    path('reading-get-data/<int:id>', ReadingGetData.as_view(), name= "for-listening-delete-data-url"),    
    path('reading-get-friends-data/<int:id>', ReadingGetFriendsData.as_view(), name= "reading-get-friends-data"),   
    path('reading-vocab/', ReadingVocabBoardView.as_view(), name="reading-vocab-board-view"),  
    path('reading-vocab-edit/<int:id>', ReadingVocabEdit.as_view(), name="reading-vocab-edit"),  
    path('reading-vocab-delete/<int:id>', ReadingVocabDelete.as_view(), name="reading-vocab-delete"),  
]