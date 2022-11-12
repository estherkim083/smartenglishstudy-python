from django.urls import path
from .views import GetProfileData, UpdateImgData, DeleteMyAccount, AccountEmailChange, AccountPasswordChange, AboutEditHashTags, ProfileSearch, AddFriends, DeleteFriends, AboutDeleteHashTags, DeleteImgData, FollowFriends, LikeFriends,MoveGroups, AddGroups, ProfileSearchBasedOnGroup, ProfileSearchBasedOnFriends, UnFollowFriends, UnLikeFriends, InboxData, InboxEditData, InboxDeletetData, AddChats, GetChats

app_name = 'mypage'

urlpatterns = [
    path('get-my-profile-data/', GetProfileData.as_view(), name="get-my-profile-data"),
    path('update-img-data/<str:type>', UpdateImgData.as_view(), name="update-img-data"),
    path('delete-img-data/', DeleteImgData.as_view(), name="delete-img-data"),
    path('my-account/delete/', DeleteMyAccount.as_view(), name="delete-my-account"),
    path('my-account/email-change/', AccountEmailChange.as_view(), name="change-my-account's-email"),
    path('my-account/password-change/', AccountPasswordChange.as_view(), name="change-my-account's-password"),
    path('inbox-data/', InboxData.as_view(), name="post-and-get-inbox-data"),
    path('inbox-edit/', InboxEditData.as_view(), name="edit-inbox-data"),
    path('inbox-delete/', InboxDeletetData.as_view(), name="delete-inbox-data"),
    path('about-edit-hashtags/', AboutEditHashTags.as_view(), name="about-edit-hashtags"),
    path('delete-about-hashtags/', AboutDeleteHashTags.as_view(), name="delete-about-hashtags"),
    path('profile-search/', ProfileSearch.as_view(), name="profile-search"),
    path('add-friends/', AddFriends.as_view(), name="add-friends"),
    path('delete-friends/', DeleteFriends.as_view(), name="delete-friends"),
    path('follow-friends/', FollowFriends.as_view(), name="follow-friends"),
    path('like-friends/', LikeFriends.as_view(), name="like-friends"),
    path('unfollow-friends/', UnFollowFriends.as_view(), name="unfollow-friends"),
    path('unlike-friends/', UnLikeFriends.as_view(), name="unlike-friends"),
    path('move-groups/', MoveGroups.as_view(), name="move-groups"),
    path('add-groups/', AddGroups.as_view(), name="add-groups"),
    path('profile-search-based-on-groups/', ProfileSearchBasedOnGroup.as_view(), name="search-groups"),
    path('profile-search-based-on-friends/', ProfileSearchBasedOnFriends.as_view(), name="friends-search"),
    path('get-chats/', GetChats.as_view(), name="get-chats"),
    path('add-chats/', AddChats.as_view(), name="add-chats"),
]