import os
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from zhu_core.jwt import CustomRefreshToken
from ..users.models import User


@require_POST
def process_oauth(request):
    if 'code' not in request.POST:
        return HttpResponse(status=400)

    resp = requests.post('https://auth.vatsim.net/oauth/token/', data={
        'grant_type': 'authorization_code',
        'client_id': os.getenv('VATSIM_CONNECT_CLIENT_ID'),
        'client_secret': os.getenv('VATSIM_CONNECT_CLIENT_SECRET'),
        'redirect_uri': os.getenv('VATSIM_CONNECT_REDIRECT_URI'),
        'code': request.POST.get('code'),
    })

    if resp.status_code != 200:
        return HttpResponse(status=500)

    auth = resp.json()

    data = requests.get('https://auth.vatsim.net/api/user/', headers={
        'Authorization': 'Bearer ' + auth.get('access_token'),
        'Accept': 'application/json',
    }).json().get('data')

    user_query = User.objects.filter(cid=data.get('cid'))
    if not user_query.exists():
        user = User.objects.create_user(
            cid=data.get('cid'),
            email=data.get('personal').get('email'),
            first_name=data.get('personal').get('name_first'),
            last_name=data.get('personal').get('name_last'),
            rating=data.get('vatsim').get('rating').get('short'),
        )
    else:
        user = user_query.first()

    refresh = CustomRefreshToken.for_user(user)

    return JsonResponse({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    })
