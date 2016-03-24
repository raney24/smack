from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from geopy.geocoders import Nominatim
import json
from django.http import HttpResponseRedirect

class SmackEvent(models.Model):
	name = models.CharField(max_length=75)
	city = models.CharField(max_length=75)
	state = models.CharField(max_length=75)
	lon = models.DecimalField(max_digits=11, decimal_places=6)
	lat = models.DecimalField(max_digits=11, decimal_places=6)

	def save(self, **kwargs):
		geolocator = Nominatim()
		location = geolocator.geocode(self.city)
		self.lon = location.longitude
		self.lat = location.latitude
		print self.lon, self.lat
		super(SmackEvent, self).save(**kwargs)

	def __unicode__(self):
		return self.name		

from django import forms

class SmackPost(models.Model):
	post = models.CharField(max_length=160)
	lon = models.DecimalField(max_digits=11, decimal_places=6)
	lat = models.DecimalField(max_digits=11, decimal_places=6)
	event = models.ForeignKey(SmackEvent, blank=True)
	user = models.ForeignKey(User, blank=True)
	voting_users = models.ManyToManyField('Smacker')
	vote_count = models.IntegerField(default=0) # create read only object

	objects = models.Manager()

	error_location = "Your location isn't valid"

	def save(self, **kwargs):
		diff_lon = abs(self.lon) - abs(self.event.lon)
		diff_lat = abs(self.lat) - abs(self.event.lat)
		print diff_lon, diff_lat

		if abs(diff_lon) < 10 and abs(diff_lat) < 10:
			super(SmackPost, self).save(**kwargs)
		else:
			raise forms.ValidationError("Invalid Location")	

	class Meta:
		ordering = ['-vote_count']

	def __unicode__(self):
		return self.post

# class Vote(models.Model):
# 	voter = models.ForeignKey(User)
# 	post = models.ForeignKey(SmackPost)

# 	def __unicode__(self):
# 		return "%s voted %s" % (self.voter.username, self.post)

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from smack.colleges import *

class Smacker(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	college = models.CharField(max_length=255, choices=COLLEGES, default=OTHER)

	def create_smacker(sender, instance, created, **kwargs):
		if created:
			Smacker.objects.create(user=instance)

	post_save.connect(create_smacker, sender=User)


	def post_votes(self):
		return self.smackpost_set.values_list('id', flat=True)













