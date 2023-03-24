from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from slack import WebClient

from common.utils import schedule_1v1, safeget, slack_users

import common.config as config
import os

@csrf_exempt
def schedule(request):
  try:
    if request.method == 'GET': return HttpResponse("welcome to 1v1 app")

    channel_id = request.POST.get('channel_id')
    user_id = request.POST.get('user_id')

    # logger
    print(f"User ran command: schedule_1v1s\nuser_id: {user_id}\nchannel_id: {channel_id}")

    slack_client = WebClient(os.environ.get('SLACK_BOT_TOKEN'))
    users_info = slack_users(slack_client)
    if not users_info: return HttpResponse("Failed to schedule")

    # logger
    print(f"email: {safeget(users_info, user_id, 'email')}")

    # check if user is allowed to execute command
    if safeget(users_info, user_id, 'email') not in config.ALLOWED_USERS:
      return HttpResponse("Not allowed to perform this action")

    schedule_1v1(slack_client, channel_id, users_info)

    return HttpResponse("1v1 have start searching :mag:")
  except Exception as e:
    return HttpResponse(e.message)