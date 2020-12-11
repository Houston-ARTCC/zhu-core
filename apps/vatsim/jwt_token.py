from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        token = cls()

        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['cid'] = user.cid

        return token
