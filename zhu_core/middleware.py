from rest_framework_simplejwt import authentication


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
            if auth.get_user():
                request.user = auth.get_user()
        except:
            pass

        return self.get_response(request)
