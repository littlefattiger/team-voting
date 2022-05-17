import collections

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
import json

CURRENT_USER = {}
USER_CHANNEL_MAPPING = {}
USER_VOTED = {}


class VotingConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        self.accept()
        group = self.scope['url_route']['kwargs'].get("group")
        async_to_sync(self.channel_layer.group_add)(group, self.channel_name)

    def websocket_receive(self, message):
        text = message['text']
        print("got message -->", text)
        text_dict = json.loads(text)
        group = self.scope['url_route']['kwargs'].get("group")
        user = text_dict["user"]
        content_type = text_dict["type"]
        if content_type == "joinInfo":
            CURRENT_USER[user] = 1
            USER_CHANNEL_MAPPING[self.channel_name] = user
            info = {
                'msg_type': 1,
                "user": user,
                "alluser": CURRENT_USER,
            }
            async_to_sync(self.channel_layer.group_send)(group, {"type": "sync.info", 'message': info})
        if content_type == "quitInfo":
            if user in CURRENT_USER:
                del CURRENT_USER[user]
            del USER_CHANNEL_MAPPING[self.channel_name]
            info = {
                'msg_type': 2,
                "user": user,
                "alluser": CURRENT_USER,
            }
            async_to_sync(self.channel_layer.group_send)(group, {"type": "sync.info", 'message': info})
            self.close()
            raise StopConsumer
            return
        elif content_type == "voteInfo":
            USER_VOTED[user] = text_dict["voting"]
            if len(USER_VOTED) == len(CURRENT_USER):
                summary_info = collections.defaultdict(list)
                for k, v in USER_VOTED.items():
                    summary_info[v].append(k)
                info = {
                    'msg_type': 5,
                    "user": user,
                    "voted": USER_VOTED,
                    "summaryinfo": summary_info,
                }
                async_to_sync(self.channel_layer.group_send)(group, {"type": "sync.info", 'message': info})
            else:
                info = {
                    'msg_type': 3,
                    "user": user,
                    "voted": USER_VOTED
                }
                async_to_sync(self.channel_layer.group_send)(group, {"type": "sync.info", 'message': info})
        elif content_type == "resetInfo":
            info = {
                'msg_type': 4,
                "user": user,
            }
            USER_VOTED.clear()
            async_to_sync(self.channel_layer.group_send)(group, {"type": "sync.info", 'message': info})

    def sync_info(self, event):
        self.send(json.dumps(event['message']))

    def websocket_disconnect(self, message):
        user = USER_CHANNEL_MAPPING[self.channel_name]
        group = self.scope['url_route']['kwargs'].get("group")
        if user in CURRENT_USER:
            del CURRENT_USER[user]
        del USER_CHANNEL_MAPPING[self.channel_name]
        info = {
            'msg_type': 2,
            "user": user,
            "alluser": CURRENT_USER,
        }
        async_to_sync(self.channel_layer.group_send)(group, {"type": "sync.info", 'message': info})
        async_to_sync(self.channel_layer.group_discard)(group, self.channel_name)
        raise StopConsumer
