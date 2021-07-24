from drf_yasg.utils import swagger_auto_schema
from fullfii.lib.constants import api_class
from survey.serializers import AccountDeleteSurveySerializer
from rest_framework import views, permissions, status
from rest_framework.response import Response


class SurveyAccountDeleteAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="アカウント削除理由サーベイ登録",
        operation_id="survey_account_delete_POST",
        tags=[api_class.API_CLS_SURVEY],
    )
    def post(self, request, *args, **kwargs):
        """
        post data: { reason: "使い方がイマイチわからない", }
        """

        post_data = {"respondent": request.user.id, **request.data}
        account_delete_survey_serializer = AccountDeleteSurveySerializer(data=post_data)
        if account_delete_survey_serializer.is_valid():
            account_delete_survey_serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(
                data=account_delete_survey_serializer.errors,
                status=status.HTTP_404_NOT_FOUND,
            )


survey_account_delete_api_view = SurveyAccountDeleteAPIView.as_view()
