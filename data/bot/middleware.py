import jwt
from django.conf import settings
from django.http import JsonResponse
from data.bot.models import BotUser
from data.user.models import User
from data.customer.models import Customer


class BotUserJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        print(f"[Middleware] Authorization header: {auth_header}")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = None

        print(f"[Middleware] JWT token: {token}")

        # request.bot_user = None
        # request.customer = None
        # request.user = None

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                bot_user_id = payload.get("bot_user_id")
                print(f"bot_user_id: {bot_user_id}")
                user_id = payload.get("user_id")
                print(f"user_id: {user_id}")
                customer_id = payload.get("customer_id")
                print(f"customer_id: {customer_id}")

                if bot_user_id:
                    request.bot_user = BotUser.objects.filter(id=bot_user_id).first()
                    print(f"bot_user: {request.bot_user}")

                if user_id:
                    # request.user = User.objects.filter(id=user_id).first()
                    request.admin = User.objects.filter(id=user_id).first()
                    print(f"admin: {request.admin}")

                if customer_id:
                    request.customer = Customer.objects.filter(id=customer_id).first()
                    print(f"customer: {request.customer}")

                request.role = (
                    "ADMIN"
                    if request.admin is not None
                    else ("CUSTOMER" if request.customer is not None else None)
                )

            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expired"}, status=401)
            except jwt.DecodeError:
                return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
