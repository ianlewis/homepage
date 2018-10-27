#:coding=utf8:

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_http_methods

from gargoyle.decorators import switch_is_active

from homepage.events.models import Event, Talk

class TalkList(ListView):
    model = Talk
    paginate_by = 10

talk_list = switch_is_active('talks')(
    require_http_methods(['GET', 'HEAD'])(TalkList.as_view()))

class TalkDetail(DetailView):
    model = Talk

talk_detail = switch_is_active('talks')(
    require_http_methods(['GET', 'HEAD'])(TalkDetail.as_view()))
