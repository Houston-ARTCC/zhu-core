import os
import requests
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from ..users.models import User


class MyTokenObtainPairSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['code'] = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)

        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['cid'] = user.cid

        return token

    def validate(self, attrs):
        authenticate_kwargs = {
            'code': attrs['code']
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        user = self.process_oauth(attrs['code'])

        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data

    def process_oauth(self, code):
        resp = requests.post('https://auth.vatsim.net/oauth/token/', data={
            'grant_type': 'authorization_code',
            'client_id': os.getenv('VATSIM_CONNECT_CLIENT_ID'),
            'client_secret': os.getenv('VATSIM_CONNECT_CLIENT_SECRET'),
            'redirect_uri': os.getenv('VATSIM_CONNECT_REDIRECT_URI'),
            'code': code,
        })

        assert resp.status_code == 200, 'Error authenticating user.'

        auth = resp.json()

        data = requests.get('https://auth.vatsim.net/api/user/', headers={
            'Authorization': 'Bearer ' + auth.get('access_token'),
            'Accept': 'application/json',
        }).json().get('data')

        # Get user's home division. If they are in VATUSA get their home facility.
        division = 'VAT' + data.get('vatsim').get('division').get('id')
        if division == 'VATUSA':
            req = requests.get('https://api.vatusa.net/v2/user/' + data.get('cid'))
            if req.status_code == 200:
                division = req.json().get('facility')

        user_query = User.objects.filter(cid=data.get('cid'))
        if not user_query.exists():
            user = User.objects.create_user(
                cid=data.get('cid'),
                email=data.get('personal').get('email'),
                first_name=data.get('personal').get('name_first'),
                last_name=data.get('personal').get('name_last'),
                rating=data.get('vatsim').get('rating').get('short'),
                home_facility=division,
            )
        else:
            user = user_query.first()
            user.home_facility = division
            user.save()

        if division == os.getenv('FACILITY_IATA'):
            user.set_membership('HC')
        elif division in os.getenv('MAVP_FACILTIY_IATA').split(','):
            user.set_membership('MC')

        return user
