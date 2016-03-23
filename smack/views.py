from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import UpdateView, CreateView, UpdateView, DeleteView, FormView
from talk.utils.helpers import post_only, get_only
from .models import *
from .forms import *
import json
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse

# Create your views here.

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class JSONFormMixin(object):
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response

class SmackEventListView(ListView):
	model = SmackEvent
	context_object_name = 'events'

class SmackEventDetailView(DetailView):
	model = SmackEvent
	context_object_name = 'event'
	# queryset = SmackPost.objects.order_by('vote_count')

	def get_context_data(self, **kwargs):
		context = super(SmackEventDetailView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			vote_tuple = Vote.objects.filter(voter = self.request.user).values_list('voter_id')
			list_vote_list = [list(elem) for elem in vote_tuple]
			list_vote = [item for sublist in list_vote_list for item in sublist]
			print list_vote
			# for vote in vote_list:

			context['vote_list'] = list_vote
			return context
		else:
			context['vote_list'] = None
	
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
	context_object_name = 'post_list'



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




class SmackVoteFormBaseView(FormView):
    form_class = VoteForm
    # def create_response(self, vdict=dict(), valid_form=True):
    #     response = HtftpResponse(json.dumps(vdict))
    #     response.status = 200 if valid_form else 500
    #     return response
    success_url = '/events'
    template_name = 'smack/smackevent_detail.html'

    def form_valid(self, form):
        post = get_object_or_404(SmackPost, pk=form.data["post"])
        user = self.request.user
        prev_votes = Vote.objects.filter(voter=user, post=post)
        has_voted = (len(prev_votes) > 0)

        ret = {"success": 1}
        if not has_voted:
            # add vote
            v = Vote.objects.create(voter=user, post=post)
            ret["voteobj"] = v.id
        else:
            # delete vote
            prev_votes[0].delete()
            ret["unvoted"] = 1
        # return self.create_response(ret, True)


class SmackVoteFormView(JSONFormMixin, SmackVoteFormBaseView):
    pass

class VoteView(View):
    model = Vote
    form_class = VoteForm
    success_url = '/events'

    def form_valid(self, form):
        post = SmackPost.objects.get(pk=self.request.pk)
        user = self.request.user

from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
def vote(request, pk):
    if request.method == 'POST':

        if request.user.is_authenticated:
            vote_form = VoteForm(request.POST)
            if vote_form.is_valid():
                user = Smacker.objects.get(user=request.user)
                post = SmackPost.objects.get(pk=pk)
                v = vote_form.save(commit=False)
                v.voter = user.user
                v.post = post
                # if post.

                post.vote_count = post.vote_count + 1

                if not Vote.objects.filter(voter = user.user, post = post).exists():
                    post.save()
                    v.save()
                    print "saving"
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
                return HttpResponse("Already Voted")
            # return HttpResponse(
            #     json.dumps(post.post),
            #     content_type="application/json"
            # )



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







