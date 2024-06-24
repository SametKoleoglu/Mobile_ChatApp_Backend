from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "name", "thumbnail"]

    def get_name(self, obj):
        fname = obj.first_name.capitalize()
        lname = obj.last_name.capitalize()

        return f"{fname} {lname}"


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password"]
        extra_kwargs = {
            "password": {
                # Ensures that when serializing, this field will be excluded
                "write_only": True
            }
        }

    def create(self, validated_data):
        # Clean all values, set as lowecase
        username = validated_data["username"].lower()
        first_name = validated_data["first_name"].lower()
        last_name = validated_data["last_name"].lower()

        # create new user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        password = validated_data["password"]
        user.set_password(password)
        user.save()
        return user


class SearchSerializer(UserSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "name", "thumbnail", "status"]

    def get_status(self, obj):
        if obj.pending_them:
            return "pending-them"
        elif obj.pending_me:
            return "pending-me"
        elif obj.connected:
            return "connected"

        return "no-connection"


class RequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Connection
        fields = ["id", "sender", "receiver", "created"]


class FriendSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = ["id", "friend", "preview", "updated"]

    def get_friend(self, obj):
        # if I'm the sender
        if self.context["user"] == obj.sender:
            return UserSerializer(obj.receiver).data
        # If Im the receiver
        elif self.context["user"] == obj.receiver:
            return UserSerializer(obj.sender).data
        else:
            print("Error : No User found in friend serializer !")
            return obj.receiver.username

    def get_preview(self, obj):
        default = "new connection"
        if not hasattr(obj, "latest_text"):
            return "new connection"
        return obj.latest_text or default

    def get_updated(self, obj):
        if not hasattr(obj, "latest_created"):
            date = obj.updated
        else:
            date = obj.latest_created or obj.updated
        return date.isoformat()


class MessageSerializer(serializers.ModelSerializer):
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "is_me", "text", "created"]

    def get_is_me(self, obj):
        return self.context["user"] == obj.user
