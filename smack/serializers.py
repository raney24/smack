from rest_framework import serializers
from .models import *

class SmackEventSerializer(serializers.ModelSerializer):
	class Meta:
		model = SmackEvent
		fields = '__all__'

	lon = serializers.ReadOnlyField()
	lat = serializers.ReadOnlyField()
	name = serializers.ReadOnlyField()

class SmackPostSerializer(serializers.ModelSerializer):
	class Meta:
		model = SmackPost
		fields = '__all__'


"""
curl --data "post='hello'&lon=-84&lat=38&event=1" http://localhost:8080/api/v1/events/1/
"""

