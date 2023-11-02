from rest_framework import serializers
from .models import FriendUser

class UserFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendUser
        fields = '__all__'

class FriendInvitationSerializer(serializers.ModelSerializer):
    friend_name = serializers.CharField(source='friend.name')
    friend_image = serializers.SerializerMethodField()

    class Meta:
        model = FriendUser
        fields = ('id', 'friend', 'friend__first_name', 'friend_image')

    def get_friend_image(self, obj):
        # Define how to get the friend's profile picture URL
        if obj.friend.profile_picture:
            return obj.friend.profile_pic.url
        return None
    

class FriendSuggestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    profile_picture = serializers.SerializerMethodField()
    
    def get_profile_picture(self, obj):
        # Define how to get the friend's profile picture URL
        if obj.profile_picture:
            return obj.user.profile_pic.url
        return None

    class Meta:
        fields = ('id', 'name', 'profile_picture')