from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import FriendUser, BlockUser, ChatRoomUser
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from services.pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from authentication.models import UserProfile
from .serializer import (
    FriendInvitationSerializer,
    FriendSuggestionSerializer,
    UserProfileSerializer,
    BlockUserSerializer,
)


class SendFriendRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            friend_id = request.data.get("friend_id")

            # Check if the user is trying to send a request to themselves
            if user.id == friend_id:
                return Response(
                    {
                        "code": 400,
                        "message": "You cannot send a friend request to yourself.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the friend request already exists
            if FriendUser.objects.filter(
                Q(user=user, friend_id=friend_id) | Q(user=friend_id, friend=user)
            ).exists():
                return Response(
                    {"code": 400, "message": "Friend request already sent"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Retrieve the friend object
            if not User.objects.filter(id=friend_id).exists():
                return Response(
                    {"code": 400, "message": "Invalid user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            friend_obj = User.objects.get(id=friend_id)
            # Create a new friend request
            user_friend = FriendUser(user=user, friend=friend_obj, invited_by=user)
            user_friend.save()

            return Response(
                {"code": 200, "message": "Friend request sent successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            friend_id = request.query_params.get("friend_id")
            # Retrieve the friend relationship
            friend_relationship = FriendUser.objects.filter(
                user=request.user, friend=friend_id, status=True
            )

            if friend_relationship.exists():
                # Delete the friend relationship and its reciprocal relationship
                friend_relationship.delete()

                # Check for the reciprocal relationship
                reciprocal_relationship = FriendUser.objects.filter(
                    user=friend_id, status=True, friend=request.user
                )
                if reciprocal_relationship.exists():
                    reciprocal_relationship.delete()

                return Response(
                    {"code": 200, "message": "Friend removed successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "code": 400,
                        "message": "Invalid friend id or friend relationship not found",
                    },
                    status=status.HTTP_BAD_REQUEST,
                )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class AcceptFriendRequest(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            invite_id = request.query_params.get("invite_id")

            # Find the friend request
            friend_request = FriendUser.objects.get(
                id=invite_id, status=False
            )  # Assuming status 0 means pending
            # Update the friend request to accepted (status 1)
            friend_request.status = True
            friend_request.save()

            # Create a reciprocal friend request (to make both users friends)
            reciprocal_friend_request = FriendUser.objects.get_or_create(
                user=friend_request.friend,
                friend=friend_request.user,
                invited_by=friend_request.friend,
                status=True,
            )
            return Response(
                {"code": 200, "message": "Friend request accepted"},
                status=status.HTTP_200_OK,
            )
        except FriendUser.DoesNotExist:
            return Response(
                {
                    "code": 400,
                    "message": "Friend request not found or already accepted",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class RejectFriendRequest(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            invite_id = request.query_params.get("invite_id")

            # Retrieve the friend request
            friend_request = FriendUser.objects.get(id=invite_id)

            # Delete the friend request and its reciprocal request
            FriendUser.objects.filter(
                Q(user=friend_request.user, friend=friend_request.friend)
                | Q(user=friend_request.friend, friend=friend_request.user)
            ).delete()

            return Response(
                {"code": 200, "message": "Friend request rejected"},
                status=status.HTTP_200_OK,
            )
        except FriendUser.DoesNotExist:
            return Response(
                {"code": 400, "message": "Friend request not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFriendView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            friend_id = request.query_params.get("friend_id")
            # Find the user's friendship record by friend_id
            friendship = FriendUser.objects.filter(
                friend_id=friend_id, user=request.user
            ).first()

            if friendship:
                # Delete the friendship record
                friendship.delete()
                # Delete the reverse friendship record
                FriendUser.objects.filter(
                    friend_id=request.user.id, user=friend_id
                ).delete()

                return Response(
                    {"code": 200, "message": "Remove friend successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"code": 400, "message": "Invalid friend id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as err:
            return Response(
                {"message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_id = request.query_params.get("user_id")
            current_user = request.user
            block_user = User.objects.get(id=user_id)
            if user.id == user_id:
                return Response(
                    {
                        "code": 400,
                        "message": "You cannot block to yourself.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Check if the user is attempting to block or unblock the target user
            existing_block = BlockUser.objects.filter(
                user=current_user, blocked_user=block_user
            )

            if existing_block:
                # The user is already blocked, unblock them
                existing_block.delete()
                return Response(
                    {
                        "code": 200,
                        "status": 0,
                        "message": "User unblocked successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Block the user
                blocked_user = BlockUser(user=current_user, blocked_user=block_user)
                blocked_user.save()
                return Response(
                    {"code": 200, "status": 1, "message": "User blocked successfully"},
                    status=status.HTTP_200_OK,
                )

        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        block_user = BlockUser.objects.filter(user=user)
        serializer = BlockUserSerializer(block_user, many=True)
        return Response(
            {
                "code": 200,
                "message": "Blocked User Fetch Successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetFriendsByUser(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            # Get the IDs of blocked users
            blocked_users = BlockUser.objects.filter(user=user)
            blocked_user_ids = [blocked.blocked_user.id for blocked in blocked_users]
            # Get the friends of the user with chat room information
            friends = FriendUser.objects.filter(user=user, status=True)
            friend_ids = [friend.friend.id for friend in friends]
            chat_users = ChatRoomUser.objects.filter(user_id__in=friend_ids)
            chat_room_ids = [chat_user.chat_room_id for chat_user in chat_users]

            friend_data = UserProfile.objects.filter(user_id__in=friend_ids).exclude(
                user_id__in=blocked_user_ids
            )
            if friend_data:
                serializer = UserProfileSerializer(friend_data, many=True)

                return Response(
                    {"code": 200, "message": "Success", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"code": 200, "message": "No records found", "data": []},
                    status=status.HTTP_200_OK,
                )

        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class GetFriendInvitationsByUser(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            # Get friend invitations where status is 0 (pending) and the inviting user is not the current user
            friend_invitations = FriendUser.objects.filter(
                status=False,
                friend=user,
            )
            print(friend_invitations)
            serializer = FriendInvitationSerializer(friend_invitations, many=True)

            response_data = {
                "code": 200,
                "message": "Success",
                "data": serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as err:
            error_response = {"message": str(err)}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


class GetFriendSuggestionsByUser(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            # Get the IDs of blocked users
            blocked_users = BlockUser.objects.filter(user=user)
            blocked_user_ids = [blocked.blocked_user.id for blocked in blocked_users]

            # Get the IDs of existing friends
            existing_friends = FriendUser.objects.filter(user=user)
            friend_ids = [friend.friend.id for friend in existing_friends]

            # Get suggested friends by excluding blocked users and existing friends
            suggested_friends = (
                UserProfile.objects.exclude(user_id__in=blocked_user_ids)
                .exclude(user_id__in=friend_ids)
                .exclude(user__username=user)
            )

            # Limit the number of suggestions to 20
            suggested_friends = suggested_friends[:20]
            print("@@@@@@@@@@@@")
            serializer = FriendSuggestionSerializer(suggested_friends, many=True)

            response_data = {
                "code": 200,
                "message": "Success",
                "data": serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as err:
            error_response = {"message": str(err)}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
