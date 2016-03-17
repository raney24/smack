from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import UpdateView, CreateView, UpdateView, DeleteView
from talk.utils.helpers import post_only, get_only
from .models import *
from .forms import *

# Create your views here.

class SmackEventListView(ListView):
	model = SmackEvent
	context_object_name = 'events'

class SmackEventDetailView(DetailView):
	model = SmackEvent
	context_object_name = 'event'
	
	# def get_object(self, queryset=None):
	# 	event = super(SmackEventDetailView, self).get_object(queryset)
	# 	SmackEvent.objects.get_object(event=event)
	# 	return event

	# def get_context_data(self, **kwargs):
	# 	context = super(SmackEventDetailView, self).get_context_data(**kwargs)
	# 	context['event_list'] = SmackEvent.objects.all()
	# 	return context

class SmackEventCreateView(CreateView):
	model = SmackEvent
	form_class = SmackEventForm
	success_url = '/events'

class SmackPostListView(ListView):
	model = SmackPost
	context_object_name = 'posts'

class SmackPostCreateView(CreateView):
	model = SmackPost
	form_class = SmackPostForm
	success_url = '/events'

	def form_valid(self, form):
		f = form.save(commit=False)
		f.user = self.request.user
		f.save()
		return super(SmackPostCreateView, self).form_valid(form)

class SmackPostDeleteView(DeleteView):
    model = SmackPost
    success_url = '/profile/view_posts'


""" USER VIEWS """
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

def user_login(request):
    """
    Pretty straighforward user authentication using password and username
    supplied in the POST request.
    """

    if request.user.is_authenticated():
        messages.warning(request, "You are already logged in.")
        return render(request, 'registration/login.html')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return HttpResponseBadRequest()

        user = authenticate(username=username,
                            password=password)

        if user:
            if user.is_active:
                login(request, user)
                redirect_url = request.POST.get('next') or 'events'
                return redirect(redirect_url)
            else:
                return render(request, 'registration/login.html',
                              {'login_error': "Account disabled"})
        else:
            return render(request, 'registration/login.html',
                          {'login_error': "Wrong username or password."})

    return render(request, 'registration/login.html')


def register(request):
    """
    Handles user registration using UserForm from forms.py
    Creates new User and new RedditUser models if appropriate data
    has been supplied.

    If account has been created user is redirected to login page.
    """
    user_form = UserForm()
    if request.user.is_authenticated():
        messages.warning(request,
                        'You are already registered and logged in.')
        return render(request, '/events', {'form': user_form})

    if request.method == "POST":
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            smacker = Smacker()
            smacker.user = user
            # smacker.save()
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password'])
            login(request, user)
            return redirect('events')

    return render(request, 'registration/register.html', {'form': user_form})

@login_required
def edit_profile(request):
    user = Smacker.objects.get(user=request.user)

    if request.method == 'GET':
        profile_form = SmackerForm(instance=user)

    elif request.method == 'POST':
        profile_form = SmackerForm(request.POST, instance=user)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.save()
            messages.success(request, "Profile settings saved")
    else:
        raise Http404

    return render(request, 'private/edit_profile.html', {'form': profile_form})

class SmackerProfileDetailView(ListView):
	model = Smacker
	# slug_field = "id"
	template_name = "private/user_detail.html"

	# def get_object(self, queryset=None):
	# 	user = super(SmackerProfileDetailView, self).get_object(queryset)
	# 	user = Smacker.objects.get_or_create(user=self.request.user)
	# 	print user
	# 	return user

@post_only
def user_logout(request):
    """
    Log out user if one is logged in and redirect them to frontpage.
    """

    if request.user.is_authenticated():
        redirect_page = request.POST.get('current_page', '/')
        logout(request)
        messages.success(request, 'Logged out!')
        return redirect(redirect_page)
    return redirect('events')

""" REST API Views """
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class JSONResponse(HttpResponse):
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

class APISmackEventListView(generics.ListCreateAPIView):
	queryset = SmackEvent.objects.all()
	serializer_class = SmackEventSerializer

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(APISmackEventListView, self).dispatch(*args, **kwargs)

class APISmackEventDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = SmackEvent.objects.all()
	serializer_class = SmackEventSerializer

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(APISmackEventDetailView, self).dispatch(*args, **kwargs)

class APISmackPostListView(generics.ListCreateAPIView):
	queryset = SmackPost.objects.all()
	serializer_class = SmackPostSerializer

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(APISmackPostListView, self).dispatch(*args, **kwargs)







