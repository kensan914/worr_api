from django.utils import timezone
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from account.v4.serializers import (
    SignupSerializer,
    AuthUpdateSerializer,
    MeSerializer,
    PatchMeSerializer,
    ProfileImageSerializer,
    UserSerializer,
)
from account.models import Gender, ProfileImage, Account, Job, FavoriteUserRelationship
from chat.models import RoomV4
from fullfii.lib.constants import api_class


class SignupAPIView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        operation_summary="サインアップ",
        operation_id="signup_POST",
        tags=[api_class.API_CLS_ACCOUNT],
    )
    @transaction.atomic
    def post(self, request):
        """
        required req data ====> {'username', 'password'} + α(gender, job)
        response ====> {'me': {(account data)}, 'token': '(token)'}

        genre_of_worries等profile params系は、key, value, labelを持つobjectのリストを渡す。
        gender等text choices系は、key(value)のstringを渡す。(ex. "female")
        """
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            me = Account.objects.filter(id=serializer.data["id"]).first()
            if me is not None:
                email_serializer = AuthUpdateSerializer(
                    me, data={"email": "{}@fullfii.com".format(me.id)}, partial=True
                )
                if email_serializer.is_valid():
                    email_serializer.save()
                    # token付与
                    if me.check_password(request.data["password"]):
                        payload = jwt_payload_handler(me)
                        token = jwt_encode_handler(payload)
                        data = {
                            "me": MeSerializer(me).data,
                            "token": str(token),
                        }

                        # fullfii.on_signup_success(me)
                        return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


signup_api_view = SignupAPIView.as_view()


class ProfileParamsAPIView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get_profile_params(self, serializer, model):
        record_obj = {}
        for record in model.objects.all():
            record_data = serializer(record).data
            record_obj[record_data["key"]] = record_data
        return record_obj

    def get_text_choices(self, text_choices):
        text_choices_obj = {}

        tc = text_choices
        for name, value, label in zip(tc.names, tc.values, tc.labels):
            text_choices_obj[value] = {
                "key": value,
                "name": name,
                "label": label,
            }
        return text_choices_obj

    @swagger_auto_schema(
        operation_summary="プロフィールパラメータ取得",
        operation_id="profile_params_GET",
        tags=[api_class.API_CLS_ACCOUNT],
    )
    def get(self, request, *args, **kwargs):
        # profile params
        # genre_of_worries_obj = self.get_profile_params(
        #     GenreOfWorriesSerializer, GenreOfWorries)

        # text choices
        gender_obj = self.get_text_choices(Gender)
        job_obj = self.get_text_choices(Job)

        return Response(
            {
                # 'genre_of_worries': genre_of_worries_obj,
                "gender": gender_obj,
                "job": job_obj,
            },
            status.HTTP_200_OK,
        )


profile_params_api_view = ProfileParamsAPIView.as_view()


class MeAPIView(views.APIView):
    Serializer = MeSerializer
    PatchSerializer = PatchMeSerializer

    @swagger_auto_schema(
        operation_summary="ミー詳細取得",
        operation_id="me_GET",
        tags=[api_class.API_CLS_ME],
    )
    def get(self, request):
        # ログイン処理(loggedin_atの更新)
        request.user.loggedin_at = timezone.now()
        request.user.save()

        serializer = self.Serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="プロフィール（職業・公開設定）の変更",
        operation_id="me_PATCH",
        tags=[api_class.API_CLS_ME],
    )
    def patch(self, request, *args, **kwargs):
        # job filter
        if "job" in request.data and not request.data["job"] in Job.values:
            return Response(status=status.HTTP_409_CONFLICT)

        serializer = self.PatchSerializer(
            instance=request.user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                self.Serializer(request.user).data, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="アカウント削除",
        operation_id="me_DELETE",
        tags=[api_class.API_CLS_ME],
    )
    def delete(self, request):
        request.user.is_active = False
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


me_api_view = MeAPIView.as_view()


class ProfileImageAPIView(views.APIView):
    parser_classes = [MultiPartParser]
    Serializer = MeSerializer

    @swagger_auto_schema(
        operation_summary="プロフィール画像の登録",
        operation_id="profile_image_POST",
        tags=[api_class.API_CLS_ME],
    )
    def post(self, request, *args, **kwargs):
        request_data = {"picture": request.data["image"], "user": request.user.id}
        if ProfileImage.objects.filter(user=request.user).exists():
            profile_image_serializer = ProfileImageSerializer(
                instance=request.user.image, data=request_data
            )
        else:
            profile_image_serializer = ProfileImageSerializer(data=request_data)

        if profile_image_serializer.is_valid():
            profile_image_serializer.save()
            return Response(
                self.Serializer(request.user).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                profile_image_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


profile_image_api_view = ProfileImageAPIView.as_view()


class GenderAPIView(views.APIView):
    @swagger_auto_schema(
        operation_summary="性別の変更",
        operation_id="gender_PUT",
        tags=[api_class.API_CLS_ME],
    )
    def put(self, request, *args, **kwargs):
        expected_keys = ["female", "male", "secret"]
        if "key" in request.data and request.data["key"] in expected_keys:
            if request.data["key"] == "female" and request.user.gender != Gender.MALE:
                request.user.gender = Gender.FEMALE
                request.user.is_secret_gender = False
            elif request.data["key"] == "male" and request.user.gender != Gender.FEMALE:
                request.user.gender = Gender.MALE
                request.user.is_secret_gender = False
            elif request.data["key"] == "secret":
                request.user.is_secret_gender = True
            request.user.save()
            return Response(
                {
                    "me": MeSerializer(request.user).data,
                },
                status.HTTP_200_OK,
            )
        else:
            return Response(status=status.HTTP_409_CONFLICT)


gender_api_view = GenderAPIView.as_view()


class HiddenRoomsAPIView(views.APIView):
    @swagger_auto_schema(
        operation_summary="ルーム非表示",
        operation_id="hidden_rooms_PATCH",
        tags=[api_class.API_CLS_ME],
    )
    def patch(self, request, *args, **kwargs):
        """
        roomの非表示
        """
        if not "room_id" in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        room_id = request.data["room_id"]
        room = get_object_or_404(RoomV4, id=room_id)

        # 自身がオーナーのルームは非表示できない
        if str(request.user.id) == str(room.owner.id):
            return Response(status=status.HTTP_409_CONFLICT)

        request.user.hidden_rooms.add(room.id)
        request.user.save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="ルーム非表示の全取り消し",
        operation_id="hidden_rooms_DELETE",
        tags=[api_class.API_CLS_ME],
    )
    def delete(self, request, *args, **kwargs):
        """
        room非表示の全取り消し
        """
        request.user.hidden_rooms.clear()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


hidden_rooms_api_view = HiddenRoomsAPIView.as_view()


class BlockedRoomsAPIView(views.APIView):
    @swagger_auto_schema(
        operation_summary="ルームブロック",
        operation_id="blocked_rooms_PATCH",
        tags=[api_class.API_CLS_ME],
    )
    def patch(self, request, *args, **kwargs):
        """
        roomのブロック
        """
        if not "room_id" in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        room_id = request.data["room_id"]
        room = get_object_or_404(RoomV4, id=room_id)

        # 自身がオーナーのルームはブロックできない
        if str(request.user.id) == str(room.owner.id):
            return Response(status=status.HTTP_409_CONFLICT)

        request.user.blocked_rooms.add(room.id)
        request.user.save()
        return Response(status=status.HTTP_200_OK)


blocked_rooms_api_view = BlockedRoomsAPIView.as_view()


class BlockedAccountsAPIView(views.APIView):
    @swagger_auto_schema(
        operation_summary="アカウントブロック",
        operation_id="blocked_accounts_PATCH",
        tags=[api_class.API_CLS_ME],
    )
    def patch(self, request, *args, **kwargs):
        """"""

        if not "account_id" in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        account_id = request.data["account_id"]
        user = get_object_or_404(Account, id=account_id)

        request.user.blocked_accounts.add(user.id)
        request.user.save()
        return Response(status=status.HTTP_200_OK)


blocked_accounts_api_view = BlockedAccountsAPIView.as_view()


class FavoritesUsersAPIView(views.APIView):
    paginate_by = 10

    @swagger_auto_schema(
        operation_summary="また話したい人たちの取得",
        operation_id="favorites_users_GET",
        tags=[api_class.API_CLS_ME],
    )
    def get(self, request, *args, **kwargs):
        _page = self.request.GET.get("page")
        page = int(_page) if _page is not None and _page.isdecimal() else 1

        favorite_user_relationship = (
            request.user.owner_favorite_user_relationship.all().order_by("-created_at")
        )
        favorite_users_ids = favorite_user_relationship.values_list(
            "favorite_account", flat=True
        )

        # to create id_list will be faster
        id_list = list(
            favorite_users_ids[self.paginate_by * (page - 1) : self.paginate_by * page]
        )
        favorite_users = [Account.objects.get(id=pk) for pk in id_list]

        serializer = UserSerializer(favorite_users, many=True)
        return Response(
            {
                "favorite_users": serializer.data,
                "has_more": not (len(favorite_users) < self.paginate_by),
            },
            status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="また話したい人の登録",
        operation_id="favorites_users_PATCH",
        tags=[api_class.API_CLS_ME],
    )
    def patch(self, request, *args, **kwargs):
        if not "user_id" in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_id = request.data["user_id"]
        favorite_account = get_object_or_404(Account, id=user_id)

        if not FavoriteUserRelationship.objects.filter(
            owner=request.user, favorite_account=favorite_account
        ).exists():
            FavoriteUserRelationship.objects.create(
                owner=request.user, favorite_account=favorite_account
            )
        return Response(status=status.HTTP_200_OK)


favorites_users_api_view = FavoritesUsersAPIView.as_view()


class FavoritesUsersDetailAPIView(views.APIView):
    @swagger_auto_schema(
        operation_summary="また話したい人の登録解除",
        operation_id="favorites_users_detail_DELETE",
        tags=[api_class.API_CLS_ME],
    )
    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        favorite_account = get_object_or_404(Account, id=user_id)

        favorite_user_relationships = FavoriteUserRelationship.objects.filter(
            owner=request.user, favorite_account=favorite_account
        )
        if favorite_user_relationships.exists():
            favorite_user_relationship = favorite_user_relationships.first()
            favorite_user_relationship.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


favorites_users_detail_api_view = FavoritesUsersDetailAPIView.as_view()
