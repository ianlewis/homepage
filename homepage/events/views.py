#:coding=utf8:

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_http_methods

from homepage.events.models import Event, Talk

class TalkList(ListView):
    model = Talk
    paginate_by = 10

talk_list = require_http_methods(['GET', 'HEAD'])(TalkList.as_view())

class TalkDetail(DetailView):
    model = Talk

talk_detail = require_http_methods(['GET', 'HEAD'])(TalkDetail.as_view())
