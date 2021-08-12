from django.contrib import admin
from .models import *
from django.utils.html import format_html
import fullfii


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "format_gender",
        "job",
        "is_active",
        "format_is_ban",
        "num_of_owner",
        "num_of_participated",
        "level",
        "loggedin_at",
        "date_joined",
    )
    list_display_links = ("username",)
    search_fields = ("username",)
    date_hierarchy = "date_joined"
    list_filter = ("gender", "is_secret_gender", "job", "is_active", "is_ban")
    raw_id_fields = (
        "hidden_rooms",
        "blocked_rooms",
        "blocked_accounts",
        "favorite_users",
        "talked_accounts",
    )
    filter_horizontal = (
        "genre_of_worries",
        "blocked_accounts",
        "favorite_users",
        "talked_accounts",
        "hidden_rooms",
        "blocked_rooms",
    )

    def format_gender(self, obj):
        if obj.gender is not None and obj.is_secret_gender is not None:
            if obj.is_secret_gender:
                return "内緒"
            else:
                return Gender(obj.gender).label

    format_gender.short_description = "性別"
    format_gender.admin_order_field = "gender"

    def format_is_ban(self, obj):
        return not obj.is_ban

    format_is_ban.boolean = True
    format_is_ban.short_description = "良アカ (凍結されていない)"
    format_is_ban.admin_order_field = "is_ban"


@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ("format_picture", "user", "upload_date")
    list_display_links = ("format_picture",)
    search_fields = ("user__username",)
    date_hierarchy = "upload_date"
    raw_id_fields = ("user",)

    def format_picture(self, obj):
        if obj.picture:
            if fullfii.exists_std_images(obj.picture):
                img_src = obj.picture.thumbnail.url
            else:
                img_src = obj.picture.url
            return format_html(
                '<img src="{}" width="100" style="border-radius: 8px" />', img_src
            )

    format_picture.short_description = "画像"
    format_picture.empty_value_display = "No image"


@admin.register(GenreOfWorries)
class GenreOfWorriesAdmin(admin.ModelAdmin):
    list_display = ("label", "key", "value")
    list_display_links = ("label",)
    search_fields = ("label",)
