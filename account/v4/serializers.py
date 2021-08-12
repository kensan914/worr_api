import os
from django.contrib.auth import password_validation as validators
from rest_framework import serializers
from account.models import Account, ProfileImage, Gender, Job
from fullfii.lib.constants import BASE_URL, USER_EMPTY_ICON_PATH
from fullfii.db.account import exists_std_images
from fullfii.lib.exp_calculator import get_current_level_info


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "username", "password", "gender", "job")

    password = serializers.CharField(write_only=True, min_length=8, max_length=30)


class SignupSerializer(AuthSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            "username",
            "password",
            "gender",
            "is_secret_gender",
            "job",
            "is_ban",
        )

    def validate_password(self, data):
        validators.validate_password(password=data, user=Account)
        return data

    def create(self, validated_data):
        # genderがFEMALEやMALE以外だった場合, is_secret_genderをTrueに
        if (
            "gender" in validated_data
            and validated_data["gender"] != Gender.FEMALE
            and validated_data["gender"] != Gender.MALE
        ):
            validated_data["is_secret_gender"] = True
        return Account.objects.create_user(**validated_data)


class AuthUpdateSerializer(AuthSerializer):
    class Meta:
        model = Account
        fields = ("id", "username", "password", "gender", "job", "email")

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        else:
            instance = super().update(instance, validated_data)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "gender",
            "is_secret_gender",
            "job",
            "introduction",
            "image",
            "num_of_owner",
            "num_of_participated",
            "is_private_profile",
        )

    name = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_name(self, obj):
        if obj.username:
            return obj.username
        else:
            return "名無し"

    def get_gender(self, obj):
        if obj.gender in Gender.values:
            g = Gender(obj.gender)
        else:
            g = Gender.NOTSET

        if g != Gender.NOTSET:
            return {"key": g.value, "name": g.name, "label": g.label}
        else:
            return {"key": g.value, "name": g.name, "label": f"性別内緒"}

    def get_job(self, obj):
        if obj.job in Job.values:
            j = Job(obj.job)
        else:
            j = Job.SECRET
        if j != Job.SECRET:
            return {"key": j.value, "name": j.name, "label": j.label}
        else:
            return {"key": j.value, "name": j.name, "label": f"職業内緒"}

    def get_image(self, obj):
        if ProfileImage.objects.filter(user=obj).exists():
            if exists_std_images(obj.image.picture):
                image_url = obj.image.picture.medium.url
            else:
                image_url = obj.image.picture.url
            return os.path.join(
                BASE_URL, image_url if image_url[0] != "/" else image_url[1:]
            )
        else:
            return os.path.join(BASE_URL, USER_EMPTY_ICON_PATH)


class MeSerializer(UserSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "gender",
            "is_secret_gender",
            "job",
            "introduction",
            "date_joined",
            "image",
            "me",
            "device_token",
            "is_active",
            "is_ban",
            "num_of_owner",
            "num_of_participated",
            "is_private_profile",
            "level_info",
            "limit_participate",
        )

    me = serializers.BooleanField(default=True, read_only=True)
    level_info = serializers.SerializerMethodField()

    def get_level_info(self, obj):
        (
            current_level,
            required_exp_next_level,
            exp_in_current_level,
        ) = get_current_level_info(obj.exp)
        return {
            "current_level": current_level,
            "required_exp_next_level": required_exp_next_level,
            "exp_in_current_level": exp_in_current_level,
            "total_exp": obj.exp,
        }


class PatchMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("name", "introduction", "device_token", "job", "is_private_profile")

    name = serializers.CharField(source="username")


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ("picture", "user")
