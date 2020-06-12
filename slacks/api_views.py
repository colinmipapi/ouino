import os
import json

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from slacks import blocks
from slacks.backends import (
    create_channel_members_dict,
)
from questions.models import Question

from slack import WebClient
import requests

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(SLACK_BOT_TOKEN)

'''
<QueryDict: {'payload': ['{"type":"block_actions","user":{"id":"U015B0PL1BN","username":"colinjmcfaul","name":"colinjmcfaul","team_id":"T0153DP2UNR"},"api_app_id":"A015HDULDKK","token":"a5b0ETDdz83wnLwxqYqUqvoH","container":{"type":"message","message_ts":"1591910755.000100","channel_id":"C014Q2ZS695","is_ephemeral":true},"trigger_id":"1172910493366.1173465096773.621177eb12eabea7aeefee22f64f297e","team":{"id":"T0153DP2UNR","domain":"yesnoworkspace"},"channel":{"id":"C014Q2ZS695","name":"project"},"response_url":"https:\\/\\/hooks.slack.com\\/actions\\/T0153DP2UNR\\/1185822901604\\/7hHKe6obk8Hrm4UjaCA9XrsR","actions":[{"type":"static_select","action_id":"urgency_select","block_id":"quY0","selected_option":{"text":{"type":"plain_text","text":"Urgent: in the next three hours","emoji":true},"value":"U"},"placeholder":{"type":"plain_text","text":"Urgency","emoji":true},"action_ts":"1591910942.744196"}]}']}>
'''


@csrf_exempt
@api_view(['POST', 'GET'])
def interactive_commands(request):

    data = json.loads(request.data['payload'])
    actions = data['actions'][0]
    action_id = actions['action_id']
    channel_id = data['channel']['id']
    if action_id == "urgency_select":
        value_list = actions['selected_option']['value'].split(",")
        question = Question.objects.get(public_id=value_list[0])
        question.status = value_list[1]
        question.responses = create_channel_members_dict(question.channel_id, question.created_by)
        question.save()
        block = blocks.question_block(question.question_text, value_list[1], question.public_id)
        response = requests.post(
            url=data['response_url'],
            json={
                "channel": channel_id,
                "blocks": block,
                "response_type": "in_channel",
                "replace_original": "true",
            })
        print(response)
    elif action_id == 'cancel_question':
        requests.post(
            url=data['response_url'],
            json={
                "delete_original": "true",
            })
    elif action_id == 'question_response_yes':
        question = Question.objects.get(public_id=actions['value'])
        slack_client.chat_postMessage(
            channel=question.created_by,
            blocks=blocks.question_response('yes', question.question_text, data['user']['username']),
            reply_broadcast=True
        )
        question.responses[data['user']['id']]['answer'] = 'yes'
        question.save()
    elif action_id == 'question_response_no':
        question = Question.objects.get(public_id=actions['value'])
        slack_client.chat_postMessage(
            channel=question.created_by,
            blocks=blocks.question_response('no', question.question_text, data['user']['username']),
            reply_broadcast=True
        )
        question.responses[data['user']['id']]['answer'] = 'no'
        question.save()
    elif action_id == 'new_yes_no_question':
        pass

    return Response(status=status.HTTP_200_OK)


'''
<QueryDict: {'token': ['a5b0ETDdz83wnLwxqYqUqvoH'], 'team_id': ['T0153DP2UNR'], 'team_domain': ['yesnoworkspace'], 'channel_id': ['C014Q2ZS695'], 'channel_name': ['project'], 'user_id': ['U015B0PL1BN'], 'user_name': ['colinjmcfaul'], 'command': ['/question'], 'text': ['Is this working? urgent'], 'response_url': ['https://hooks.slack.com/commands/T0153DP2UNR/1162352845527/fUKP2289tYXkM8Wd7XiMtzUI'], 'trigger_id': ['1200931719072.1173465096773.7593f9f11efcdb628b3d42e70fe88aa4']}>
'''


@csrf_exempt
@api_view(['POST', ])
def question(request):
    if request.data['command'] == '/question':
        user_question = "*%s*" % request.data['text']
        channel_id = request.data['channel_id']
        question = Question.objects.create(
            created_by=request.data['user_id'],
            question_text=user_question,
            channel_id=channel_id
        )
        data = {
            "channel": channel_id,
            "blocks": blocks.confirm_question_create_block(user_question, question.public_id)
        }

    else:
        print(request.data)
        data = {}

    return Response(data, status=status.HTTP_200_OK)
