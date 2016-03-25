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
from django.db.models import Count

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

	def get_context_data(self, **kwargs):
		context = super(SmackEventDetailView, self).get_context_data(**kwargs)
		event_pk = kwargs['object'].pk
		context['post_list'] = SmackPost.objects.filter(
												event=event_pk).annotate(
															num_votes=Count(
																'voting_users')).order_by('-num_votes')
		return context

class SmackEventCreateView(CreateView):
	model = SmackEvent
	form_class = SmackEventForm
	success_url = '/events'

class SmackPostListView(ListView): # NOT EVER USED
	model = SmackPost
	context_object_name = 'post_list'

	def get_context_data(self, **kwargs):
		context = super(SmackPostListView, self).get_context_data(**kwargs)
		print "here"
		context['post_list'] = SmackPost.objects.annotate(num_votes=Count('voting_users')).order_by('num_votes')
		return context

class SmackPostCreateView(FormView):
	model = SmackPost
	form_class = SmackPostForm
	template_name = "smack/smackpost_form.html"
	success_url = '/events'

	def form_valid(self, form):
		print "in form"
		self.object = form.save(commit=False)
		self.object.user = self.request.user
		self.object.save()
		return super(SmackPostCreateView, self).form_valid(form)

class SmackPostDeleteView(DeleteView):
    model = SmackPost
    success_url = '/profile/view_posts'




# class SmackVoteFormBaseView(FormView):
#     form_class = VoteForm
#     # def create_response(self, vdict=dict(), valid_form=True):
#     #     response = HtftpResponse(json.dumps(vdict))
#     #     response.status = 200 if valid_form else 500
#     #     return response
#     success_url = '/events'
#     template_name = 'smack/smackevent_detail.html'

#     def form_valid(self, form):
#         post = get_object_or_404(SmackPost, pk=form.data["post"])
#         user = self.request.user
#         prev_votes = Vote.objects.filter(voter=user, post=post)
#         has_voted = (len(prev_votes) > 0)

#         ret = {"success": 1}
#         if not has_voted:
#             # add vote
#             v = Vote.objects.create(voter=user, post=post)
#             ret["voteobj"] = v.id
#         else:
#             # delete vote
#             prev_votes[0].delete()
#             ret["unvoted"] = 1
#         # return self.create_response(ret, True)


# class SmackVoteFormView(JSONFormMixin, SmackVoteFormBaseView):
#     pass


from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
def vote(request, pk):
    if request.method == 'POST':

        if request.user.is_authenticated:
            smacker = Smacker.objects.get(user=request.user)
            post = SmackPost.objects.get(pk=pk)            

            # check if user has voted
            if not post.voting_users.filter(user_id = smacker.user_id).exists():
                post.voting_users.add(smacker)
                post.save()
                print "saving"
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            return HttpResponse("Already Voted")

def delete_vote(request, pk):
	if request.method == 'POST':
		if request.user.is_authenticated:
			smacker = Smacker.objects.get(user=request.user)
			post = SmackPost.objects.get(pk=pk)

			if post.voting_users.filter(user_id = smacker.user_id).exists():
				post.voting_users.remove(smacker)
				post.save()
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

			return HttpResponse("You must like to unlike")


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







