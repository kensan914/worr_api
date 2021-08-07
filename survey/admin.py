from survey.models import AccountDeleteSurvey, DissatisfactionSurvey
from django.contrib import admin


@admin.register(AccountDeleteSurvey)
class AccountDeleteSurveyAdmin(admin.ModelAdmin):
    list_display = ("respondent", "reason", "created_at")
    list_display_links = ("respondent",)
    search_fields = (
        "respondent__username",
        "reason",
    )
    date_hierarchy = "created_at"
    raw_id_fields = ("respondent",)


@admin.register(DissatisfactionSurvey)
class DissatisfactionSurveyAdmin(admin.ModelAdmin):
    list_display = ("respondent", "contents", "created_at")
    list_display_links = ("respondent",)
    search_fields = (
        "respondent__username",
        "contents",
    )
    date_hierarchy = "created_at"
    raw_id_fields = ("respondent",)
