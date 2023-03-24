from slack.errors import SlackApiError
import time
import random
import json

def group_dm(slack_client, users, message):
  group_dm_id = safeget(slack_call(slack_client.conversations_open, {"users": users}), "channel", "id")
  if not group_dm_id: return False

  return post_message(slack_client, group_dm_id, message)

def post_message(slack_client, channel_id, message, opts={}):
  return safeget(slack_call(slack_client.chat_postMessage, {"channel": channel_id, "text": message, "parse": True}, **opts), "ok")

def group_random(user_list, group_size=2, strict=True):
  random.shuffle(user_list)
  groups = [user_list[i:i+group_size] for i in range(0, len(user_list), group_size)]
  
  if strict: 
    groups = list(filter(lambda group: len(group) == group_size, groups))

  return groups

def safeget(dct, *keys):
  if not dct: return None

  for key in keys:
    try:
      dct = dct[key]
    except KeyError:
      return None
  return dct

def schedule_1v1(slack_client, channel_id, users_info):
  channel_members = slack_channel_members(slack_client, channel_id)
  if not channel_members: return None

  channel_members_info = [safeget(users_info, user_id) for user_id in channel_members]
  
  # remove bot
  channel_members_info = list(filter(lambda user: not safeget(user, 'is_bot'), channel_members_info))
  
  # group members
  member_groups = group_random(channel_members_info)

  # hardcoded to send @aryamaan_jain member groups
  print(member_groups)
  post_message(slack_client, "U04U41MRT8S", f"Groups: ```{json.dumps(member_groups, indent=2)}```", opts={"max_retries": 5, "wait": 10})

  report = []

  for member_group in member_groups:
    users = list(map(lambda user: safeget(user, "id"), member_group))
    user_mention_list = ", ".join(list(map(lambda user: f"<@{user}>", users)))
    message = f"Hey {user_mention_list} :raised_hands:,\n"\
      f"We have successfully found a match for your 1v1 meet this weekend.\n"\
      f"So 1v1 app set meet-ups for everyone in <#{channel_id}> to meet every week.\n"\
      f"Now that you're here, schedule a time to meet! :coffee::computer:"

    success = group_dm(slack_client, users, message)
    report.append({"success": success, "member_group": member_group})

    time.sleep(1)

  # hardcoded to send @aryamaan_jain success report
  print(report)
  post_message(slack_client, "U04U41MRT8S", f"Success Report:\n```{json.dumps(report, indent=2)}```", opts={"max_retries": 5, "wait": 10})

  post_message(slack_client, channel_id, "1v1 have succesfully done his job :relieved:")

def serialize_user(user):
  return {
    "id": safeget(user, 'id'),
    "name": safeget(user, 'name'),
    "email": safeget(user, 'profile', 'email'),
    "is_bot": safeget(user, 'is_bot')
  }

def slack_call(method, args={}, max_retries=3, wait=3):
  for retry in range(max_retries):
    try:
      response = method(**args)
      return response
    except SlackApiError as e:
      print(f"Retry: {retry+1}\nResponse: {e}")

    time.sleep(wait)

  return None

def slack_channel_members(slack_client, channel):
  response = slack_call(slack_client.conversations_members, {"channel": channel})
  return safeget(response, 'members')

def slack_users(slack_client):
  users_list = slack_call(slack_client.users_list)
  if not users_list: return None

  serialized_users = {}
  for user in safeget(users_list, 'members'):
    serialized_users[safeget(user, 'id')] = serialize_user(user)

  return serialized_users
