from django.urls import path
from .views import *

urlpatterns = [
    path('friend',SendFriendRequestView.as_view(),name='change-password'),
    path('accept-friend-request',AcceptFriendRequest.as_view(),name='accept-friend-request'),
    path('reject-friend-request',RejectFriendRequest.as_view(),name='reject-friend-request'),
    path('block-unblock',BlockUserView.as_view(),name='block-unblock'),

    path('my-friends',GetFriendsByUser.as_view(),name='my-friends'),
    path('friendship-invites',GetFriendInvitationsByUser.as_view(),name='friendship-invites'),
    path('friend-suggestions',GetFriendSuggestionsByUser.as_view(),name='friend-suggestions'),
]