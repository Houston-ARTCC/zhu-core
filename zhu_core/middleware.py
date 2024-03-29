from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        If request is using a JWT token, sets the 'user'
        attribute of the request to the autenticated user.
        """
        try:
            auth = authentication.JWTAuthentication().authenticate(request)
            if auth:
                request.user = auth[0]
        except (AuthenticationFailed, InvalidToken):
            pass

        return self.get_response(request)
