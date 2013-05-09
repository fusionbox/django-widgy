from django.http import HttpResponse

def hello(request):
    return HttpResponse(
        '<!DOCTYPE html>'
        '<title>Demo url</title><p>Hello!'
    )
