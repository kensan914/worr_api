import os
from rest_framework import serializers
from account.v4.serializers import UserSerializer
from chat.models import MessageV4, RoomV4
from account.models import Account
from fullfii.db.account import exists_std_images
from fullfii.lib.constants import BASE_URL


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomV4
        fields = (
            "id",
            "name",
            "image",
            "image_src",
            "owner",
            "owner_id",
            "participants",
            "left_members",
            "max_num_participants",
            "is_exclude_different_gender",
            "is_private",
            "created_at",
            "is_end",
            "is_active",
            "added_favorite_user_ids",
        )
        read_only_fields = ("id", "created_at", "is_end", "is_active", "image")

    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), write_only=True
    )  # post only
    image = serializers.SerializerMethodField(required=False)
    image_src = serializers.ImageField(
        source="image", write_only=True, required=False
    )  # post only
    participants = UserSerializer(many=True, required=False)
    left_members = UserSerializer(many=True, required=False)
    created_at = serializers.SerializerMethodField()
    added_favorite_user_ids = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            if exists_std_images(obj.image):
                image_url = obj.image.medium.url
            else:
                image_url = obj.image.url
        else:
            if exists_std_images(obj.default_image.image):
                image_url = obj.default_image.image.medium.url
            else:
                image_url = obj.default_image.image.url
        return os.path.join(
            BASE_URL, image_url if image_url[0] != "/" else image_url[1:]
        )

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y/%m/%d %H:%M:%S")

    def get_added_favorite_user_ids(self, obj):
        if "me" in self.context:
            favorite_user_relationship = (
                self.context["me"]
                .owner_favorite_user_relationship.all()
                .order_by("-created_at")
            )
            favorite_users_ids = favorite_user_relationship.values_list(
                "favorite_account", flat=True
            )
            # このルームに該当するfavorite usersをフィルター
            target_favorite_users_ids = list(
                filter(
                    lambda favorite_user_id: favorite_user_id == obj.owner.id
                    or favorite_user_id
                    in obj.participants.values_list("id", flat=True),
                    list(favorite_users_ids),
                )
            )

            # UUIDオブジェクトをstrに変換
            return list(
                map(
                    lambda favorite_user_id: str(favorite_user_id),
                    target_favorite_users_ids,
                )
            )
        else:  # 自身が直接関係しないルーム
            return []

    def create(self, validated_date):
        validated_date["owner"] = validated_date.get("owner_id", None)

        if validated_date["owner"] is None:
            raise serializers.ValidationError("the owner not found.")

        del validated_date["owner_id"]

        return RoomV4.objects.create(**validated_date)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageV4
        fields = ("id", "text", "sender_id", "time")

    sender_id = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    def get_sender_id(self, obj):
        return str(obj.sender.id)

    def get_time(self, obj):
        if obj.time:
            return obj.time.strftime("%Y/%m/%d %H:%M:%S")
