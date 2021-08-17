from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from account.v4.serializers import UserSerializer
from chat.models import RoomV4, MessageV4
from chat.v4.serializers import MessageSerializer, RoomSerializer
from config import settings
from fullfii.lib.constants import BASE_URL


class BaseView(View):
    html_path = "frontend/index.html"
    context = {"static_update": "?3.0.0", "debug": settings.env.bool("DEBUG")}


class TopView(BaseView):
    html_path = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.html_path, self.context)


topView = TopView.as_view()


class TermsOfServiceView(BaseView):
    html_path = "terms-of-service.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.html_path, self.context)


termsOfServiceView = TermsOfServiceView.as_view()


class PrivacyPolicyView(BaseView):
    html_path = "privacypolicy.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.html_path, self.context)


privacyPolicyView = PrivacyPolicyView.as_view()


class AdminMessagesView(BaseView):
    # permission_classes = (permissions.IsAdminUser,)
    html_path = "admin-messages.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            room_id = self.kwargs.get("room_id")
            room = get_object_or_404(RoomV4, pk=room_id)
            messages = MessageV4.objects.filter(room=room).order_by("time")

            return render(
                request,
                self.html_path,
                context={
                    **self.context,
                    "messages": [
                        {
                            "sender_data": UserSerializer(message.sender).data,
                            **MessageSerializer(message).data,
                        }
                        for message in messages
                    ],
                    "room_data": RoomSerializer(room).data,
                    "base_url": BASE_URL,
                },
            )
        else:
            return redirect("/")


admin_messages_view = AdminMessagesView.as_view()
