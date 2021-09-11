# custom made decorator that acts as a middleware in a your chosen method as decorator tag
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse

# here the method checks if the user is admin
def admin_required(function):
    def _function(request, *args, **kwargs):
        next = request.POST.get('next')
        if not (request.user.member_team_name).strip()=='Διαχειριστής':
            messages.info(request, 'Μονο ο Διαχειριστής έχει πρόσβαση')
            return redirect(next)
        return function(request, *args, **kwargs)
    return _function
