from django.urls import path
from account.v4.views import (
    signup_api_view,
    profile_image_api_view,
    me_api_view,
    profile_params_api_view,
    gender_api_view,
    hidden_rooms_api_view,
    blocked_rooms_api_view,
    blocked_accounts_api_view,
    favorites_users_api_view,
    favorites_users_detail_api_view,
)
from chat.v4.views import (
    talk_info_api_view,
    rooms_api_view,
    rooms_detail_api_view,
    rooms_detail_images_api_view,
    rooms_detail_participants_api_view,
    rooms_detail_left_members_api_view,
    rooms_detail_closed_members_api_view,
    private_rooms_api_view,
)
from survey.views import survey_account_delete_api_view, survey_dissatisfaction_api_view

app_name = "api_v4"


urlpatterns = [
    ##########################
    ## 1. アカウント/account ##
    ##########################
    path("signup/", signup_api_view, name="signup_api"),
    path("profile-params/", profile_params_api_view, name="profile_params_api"),
    ################
    ## 2. ミー/me ##
    ################
    path("me/", me_api_view, name="me_api"),
    path("me/profile-image/", profile_image_api_view, name="profile_image_api"),
    path("me/talk-info/", talk_info_api_view, name="talk_info_api"),
    path("me/gender/", gender_api_view, name="gender_api"),
    path("me/hidden-rooms/", hidden_rooms_api_view, name="hidden_rooms_api"),
    path("me/blocked-rooms/", blocked_rooms_api_view, name="blocked_rooms_api"),
    path(
        "me/blocked-accounts/", blocked_accounts_api_view, name="blocked_accounts_api"
    ),
    path("me/favorites/users/", favorites_users_api_view, name="favorites_users_api"),
    path(
        "me/favorites/users/<uuid:user_id>/",
        favorites_users_detail_api_view,
        name="favorites_users_detail_api",
    ),
    ###################
    ## 3. ユーザ/user ##
    ###################
    ###################
    ## 4. ルーム/room ##
    ###################
    path("rooms/", rooms_api_view, name="rooms_api"),
    path("rooms/<uuid:room_id>/", rooms_detail_api_view, name="rooms_detail_api_view"),
    path(
        "rooms/<uuid:room_id>/images/",
        rooms_detail_images_api_view,
        name="rooms_detail_images_api",
    ),
    path(
        "rooms/<uuid:room_id>/participants/",
        rooms_detail_participants_api_view,
        name="rooms_detail_participants_api",
    ),
    path(
        "rooms/<uuid:room_id>/left-members/",
        rooms_detail_left_members_api_view,
        name="rooms_detail_left_members_api_view",
    ),
    path(
        "rooms/<uuid:room_id>/closed-members/",
        rooms_detail_closed_members_api_view,
        name="rooms_detail_closed_members_api",
    ),
    path("private-rooms/", private_rooms_api_view, name="private_rooms_api"),
    #######################
    ## 5. サーベイ/survey ##
    #######################
    path(
        "survey/account-delete/",
        survey_account_delete_api_view,
        name="survey_account_delete_api",
    ),
    path(
        "survey/dissatisfaction/",
        survey_dissatisfaction_api_view,
        name="survey_dissatisfaction_api",
    ),
]
