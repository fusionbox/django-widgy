from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render

from widgy.contrib.cms.models import Callout


@staff_member_required
def callout_browse(request):
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'images_total': 0, 'select_total': 0 }
    callouts = Callout.objects.all()
    results_var['results_current'] = len(callouts)

    p = Paginator(callouts, 10)
    try:
        page_nr = request.GET.get('p', '1')
    except:
        page_nr = 1
    try:
        page = p.page(page_nr)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)

    return render(request, 'cms/callout/index.html', {
        'query': {},
        'page': page,
        'p': p,
        'results_var': results_var
    })
