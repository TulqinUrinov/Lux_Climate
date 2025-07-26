from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .models import BotUser
from .utils import BotUserJWTAuthentication

from telegram_webapp_auth.auth import TelegramAuthenticator, generate_secret_key

BOT_TOKEN = config("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValidationError("Bot token not found")


class JWTtokenGenerator(APIView):
    """
    Generate JWT token using telegram mini app credentials.
    """

    permission_classes = []

    def post(self, request):
        init_data = request.data.get("init_data")
        # bot = request.data.get("bot").strip().upper() if request.data.get("bot") else None

        if not init_data:
            raise ValidationError("init_data is required")

        secret_key = generate_secret_key(BOT_TOKEN)

        authenticator = TelegramAuthenticator(secret_key)

        auth_data = authenticator.validate(init_data)
        user_id = auth_data.user.id
        bot_user = BotUser.objects.filter(chat_id=user_id).first()

        if not bot_user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # refresh = RefreshToken()
        #
        # refresh.payload['user'] = bot_user.id
        refresh = RefreshToken.for_user(bot_user.user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


class JWTtokenRefresh(APIView):
    """
    Refresh JWT token using refresh token.
    """

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token
            return Response(
                {"access": str(access), "refresh": str(refresh)},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class Me(APIView):
#     authentication_classes = [BotUserJWTAuthentication]
#     """
#     Get user information.
#     """
#
#     def get(self, request):
#         user = request.user
#         if not user:
#             return Response(
#                 {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
#             )
#
#         user_data = {
#             "id": user.id,
#             "name": user.full_name,
#             # "number": user.phone_number,
#             "chat_id": user.chat_id,
#         }
#         return Response(user_data, status=status.HTTP_200_OK)
