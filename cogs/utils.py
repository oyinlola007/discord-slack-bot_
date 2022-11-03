import re, requests

import cogs.config as config
import cogs.strings as strings
import cogs.db as db


def get_key_from_value(obj_value, obj_dict):
    for key, value in obj_dict.items():
        if value == obj_value:
            return key

    if obj_value == "the_horns":
        return "🤘"
    elif obj_value == "+1":
        return "👍"
    else:
        return obj_value

def replace_discord_id_with_slack_id(text):
    return re.sub(r'\<\@\d{18}\>',
                  lambda x: "<@" + strings.USERS_DICT[x.group(0).strip("<@").strip(">")] + ">",
                  text)

def replace_slack_id_with_discord_id(text):
    return re.sub(r'\<\@.*?\>',
                  lambda x: "<@" + get_key_from_value(x.group(0).strip("<@").strip(">"), strings.USERS_DICT) + ">",
                  text)

def post_message_to_slack(avatar_url, username, text):
    data = {
        'token': config.BOT_USER_OAUTH_TOKEN,
        'channel': config.SLACK_CHANNEL_ID,
        'icon_url': avatar_url,
        'username': username,
        'text': text
    }
    return requests.post(url='https://slack.com/api/chat.postMessage',
                         data=data)


def add_reaction_to_slack(emoji, slack_timestamp):
    data = {
        'token': config.BOT_USER_OAUTH_TOKEN,
        'channel': config.SLACK_CHANNEL_ID,
        'name': emoji,
        'timestamp': slack_timestamp
    }
    requests.post(url='https://slack.com/api/reactions.add',
                  data=data)

def get_messages_since_timestamp(default_ts):
    header = {
        'Authorization': 'Bearer ' + config.BOT_USER_OAUTH_TOKEN
    }

    data = {
        'channel': config.SLACK_CHANNEL_ID,
        'include_all_metadata': True,
        'oldest': db.get_last_timestamp(default_ts)
    }
    res = requests.get(url='https://slack.com/api/conversations.history',
                       params=data, headers=header)

    return res.json()["messages"]

def get_user_details(user_id):
    header = {
        'Authorization': 'Bearer ' + config.BOT_USER_OAUTH_TOKEN
    }

    payload = {'user': user_id}

    res = requests.get('https://slack.com/api/users.info',
                     params=payload, headers=header)

    return res.json()["user"]

def get_reactions_for_message(ts):
    header = {
        'Authorization': 'Bearer ' + config.BOT_USER_OAUTH_TOKEN
    }

    data = {
        'channel': config.SLACK_CHANNEL_ID,
        'full': False,
        'timestamp': ts
    }
    res = requests.get(url='https://slack.com/api/reactions.get',
                       params=data, headers=header)

    return res.json()["message"]["reactions"]