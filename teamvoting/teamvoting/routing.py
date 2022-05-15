from django.urls import re_path

from easyvoting import consumers

websocket_urlpatterns =[
    re_path(r'room/(?P<group>\w+)/$', consumers.VotingConsumer.as_asgi()),
]