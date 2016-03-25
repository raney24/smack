"""talk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from smack.views import *
from django.contrib.auth.decorators import login_required, permission_required


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', SmackEventListView.as_view()),

    url(r'^events/$', SmackEventListView.as_view(), name='events'),
    url(r'^events/(?P<pk>\d+)/$', SmackEventDetailView.as_view()),
    url(r'^events/create/$', SmackEventCreateView.as_view(), name='create_events'),
    url(r'^events/delete/(?P<pk>\d+)$', SmackPostDeleteView.as_view(), name='delete_post'),

    url(r'^events/(?P<pk>\d+)/post/$', login_required(SmackPostCreateView.as_view()), name='create_posts'),

    url(r'^vote/(?P<pk>\d+)$', login_required(vote), name="like"),
    url(r'^delete_vote/(?P<pk>\d+)$', login_required(delete_vote), name="unlike"),


    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/v1/events/$', APISmackEventListView.as_view()),
    url(r'^api/v1/events/(?P<pk>\d+)/$', APISmackPostListView.as_view()),

    # url(r'^events/create/$', SmackEventPostView.as_view()), 
    url(r'^login/$', user_login, name="Login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', { 'next_page':"/events" }, name="Logout"),

    url(r'^register/$', register, name="Register"),
    url(r'^profile/edit/$', login_required(edit_profile, login_url="Login"), name="Edit Profile"),
    url(r'^profile/change_password/$', 'django.contrib.auth.views.password_change', 
        {'template_name': 'private/password_change_form.html'},
        name="ChangePassword"),
    url(r'^profile/edit/$', 'django.contrib.auth.views.password_change_done', name="password_change_done"),
    url(r'^profile/view_posts$', login_required(SmackerProfileDetailView.as_view()), name="UserProfile"),

    # url(r'^$', UserListView.as_view(), name='home'),
]

#REST URLS
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = format_suffix_patterns(urlpatterns)