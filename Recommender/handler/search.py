#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from operator import itemgetter
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


# @require_http_methods(["POST"])
def search_product(request):
    # keywords = request.POST.get("keywords", '')
    keywords = request.POST.get("keywords")
    print("keywords:"+keywords)
    result = {}
    result['key'] = keywords
    return JsonResponse(result, safe=False)
    # return render(request, "student/index.html", {'username': user})
    #return HttpResponse(request)
