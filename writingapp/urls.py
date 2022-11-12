from django.urls import path
from .views import CreateEssayRoom, EditEssayRoom, GetEssayRoomData, GetEssayRoomList, JoinEssayRoom, EssayWritingIndividual, CheckEssayRoomUser, UnJoinEssayRoom, DeleteEssayRoom, AccessEditEssayRoom, SubmitEssayComment, DefineEssayWritingEditor, GetEditView, EssayEdit, EditPermission, DeleteEdit, CreateBookWritingRoom, DeleteBookWritingRoom, EditBookWritingRoom, AccessEditBookWritingRoom, GetBookWritingRoomData, GetBookWritingRoomList, JoinBookWritingRoom, UnJoinBookWritingRoom, CheckBookWritingRoomUser, BookWritingIndividual, SubmitBookWritingComment, DefineBookWritingEditor, BookWritingEdit


app_name = 'writingapp'

urlpatterns = [
   path('create-essay-room/', CreateEssayRoom.as_view(), name="create-essay-room"),
   path('delete-essay-room/<int:id>', DeleteEssayRoom.as_view(), name="delete-essay-room"),
   path('edit-essay-room/<int:id>', EditEssayRoom.as_view(), name="edit-essay-room"),
   path('access-edit-essay-room/<int:id>', AccessEditEssayRoom.as_view(), name="access-edit-essay-room"),
   path('get-essay-room-data/<int:id>', GetEssayRoomData.as_view(), name="get-essay-room-data-for-edit"),
   path('get-essay-room-list/', GetEssayRoomList.as_view(), name="get-essay-room-list"),
   path('join-essay-room/<int:id>', JoinEssayRoom.as_view(), name="join-essay-room"),
   path('unjoin-essay-room/<int:id>', UnJoinEssayRoom.as_view(), name="unjoin-essay-room"),
   path('check-if-essay-participant-user/<int:id>/<int:userid>', CheckEssayRoomUser.as_view(), name="check-if-is-able-to-edit"),
   path('get-essay-writing-data/<str:type>/<int:id>/<int:userid>', EssayWritingIndividual.as_view(), name="get-essay-writing-data"),
   path('submit-essay-comment/<int:id>/<int:userid>', SubmitEssayComment.as_view(), name="submit-essay-comment"),
   path('define-essay-editor/<int:id>/<int:userid>', DefineEssayWritingEditor.as_view(), name="define-essay-editor"),
   path('get-edit-view/', GetEditView.as_view(), name="get-edit-view"), # 책 글쓰기+ 에세이 글쓰기 첨삭 자료들 모두 불러가기.
   path('edit-essay/<int:id>', EssayEdit.as_view(), name="edit-essay"), # 에세이 첨삭.
   path('check-editor-permission/<str:type>/<int:id>', EditPermission.as_view(), name="check-editor-permission"),
   path('delete-editor-data/<str:type>/<int:id>', DeleteEdit.as_view(), name="delete-editor-material"), # 에세이 첨삭한 자료 제거
   # book writing 옵션들.
   path('create-book-writing-room/', CreateBookWritingRoom.as_view(), name="create-book-writing-room"),
   path('delete-book-writing-room/<int:id>', DeleteBookWritingRoom.as_view(), name="delete-book-writing-room"),
   path('edit-book-writing-room/<int:id>', EditBookWritingRoom.as_view(), name="edit-book-writing-room"),
   path('access-edit-book-writing-room/<int:id>', AccessEditBookWritingRoom.as_view(), name="access-edit-book-writing-room"),
   path('get-book-writing-room-data/<int:id>', GetBookWritingRoomData.as_view(), name="get-book-writing-room-data-for-edit"),
   path('get-book-writing-room-list/', GetBookWritingRoomList.as_view(), name="get-book-writing-room-list"),
   path('join-book-writing-room/<int:id>', JoinBookWritingRoom.as_view(), name="join-book-writing-room"),
   path('unjoin-book-writing-room/<int:id>', UnJoinBookWritingRoom.as_view(), name="unjoin-book-writing-room"),
   path('check-if-book-writing-participant-user/<int:id>/<int:userid>', CheckBookWritingRoomUser.as_view(), name="check-if-is-able-to-edit-book-writing"),
   path('get-book-writing-data/<str:type>/<int:id>/<int:userid>', BookWritingIndividual.as_view(), name="get-book-writing-data"),
   path('submit-book-writing-comment/<int:id>/<int:userid>', SubmitBookWritingComment.as_view(), name="submit-book-writing-comment"),
   path('define-book-writing-editor/<int:id>/<int:userid>', DefineBookWritingEditor.as_view(), name="define-book-writing-editor"),
   path('edit-book-writing/<int:id>', BookWritingEdit.as_view(), name="edit-book-writing"), # 책 글쓰기 첨삭.
]