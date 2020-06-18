import os
import requests
import json
import hmac
import hashlib

from slack import WebClient

from slacks import blocks

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

slack_client = WebClient(SLACK_BOT_TOKEN)


def create_channel_members_dict(channel_id, created_by):

    member_dict = dict()

    response = slack_client.conversations_members(channel=channel_id)
    for member in response['members']:
        if member != created_by:
            url = "https://slack.com/api/users.info?token=%s&user=%s" %(SLACK_BOT_TOKEN, member)
            user_info = requests.get(
                url=url
            )
            user_info = json.loads(user_info.text)
            if user_info:
                if not user_info['user']['is_bot']:
                    member_dict[member] = {
                        'answer': None,
                        'username': user_info['user']['name']
                    }

    return member_dict


def question_response(data, question, answer):
    new_message = False
    if question.created_by != data['user']['id']:
        if not question.responses:
            question.responses = {
                data['user']['id']: {
                    'answer': answer,
                    'username': data['user']['username']
                }
            }
            new_message = True
        elif data['user']['id'] in question.responses:
            if question.responses[data['user']['id']]['answer'] is None:
                question.responses[data['user']['id']]['answer'] = answer
                new_message = True
        else:
            question.responses[data['user']['id']] = {
                'answer': answer,
                'username': data['user']['username']
            }
            new_message = True

        if new_message:
            if not question.response_message_ts:
                response = slack_client.chat_postMessage(
                    channel=question.created_by,
                    blocks=blocks.question_response(question),
                    reply_broadcast=True
                )
                question.response_message_ts = response['ts']
            else:
                slack_client.chat_update(
                    channel=question.channel_id,
                    ts=question.response_message_ts,
                    attachments=blocks.question_response(question),
                )
            question.save()
            return 'Thanks for responding!'
        else:
            return "You've already responded to this question"
    else:
        return "You can't answer your own question"


def response_reminder(channel_id, question):
    slack_client.chat_postMessage(
        channel=channel_id,
        blocks=blocks.response_reminder(question)
    )


def secret_signing_valid(request):
    slack_secret = request.META['HTTP_X_SLACK_SIGNATURE']
    timestamp = request.META['HTTP_X_SLACK_REQUEST_TIMESTAMP']
    sig_basestring = 'v0:' + timestamp + ':' + request.body.decode("utf-8")
    my_signature = 'v0=' + hmac.new(
        str.encode(SLACK_SIGNING_SECRET),
        sig_basestring,
        hashlib.sha256
    ).hexdigest()
    if my_signature == slack_secret:
        return True
    else:
        return False
