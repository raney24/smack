from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from smack.models import *

def check_location(lon, lat):
	pass

class SmackEventForm(forms.ModelForm):
	class Meta:
		model = SmackEvent
		exclude = ('lon', 'lat')

class SmackPostForm(forms.ModelForm):
	# queryset = SmackEvent.objects.get(pk=1)
	# context_object_name = 'event'
	lon = forms.DecimalField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
	lat = forms.DecimalField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
	class Meta:
		model = SmackPost
		fields = ('post', 'lon', 'lat', 'event')
		# fields = ('__all__')

# class VoteForm(forms.ModelForm):
# 	class Meta:
# 		# exclude = ('voter', 'post')
# 		fields = ('__all__')

""" USER FORMS """
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput)
	class Meta:
		model = User
		fields = ('username', 'password')

# class PasswordChangeFormPrivate(PasswordChangeForm):
# 	def __init__(self, *args, **kwargs):
# 		super(PasswordChangeForm, self).__init__(*args, **kwargs)

# 	def clean_new_password2(self):
# 		password1 = self.cleaned_data.get('new_password1')
# 		password2 = self.cleaned_data.get('new_password2')
# 		if password1 and password2:
# 			if password1 != password2:
# 				raise forms.ValidationError(_("They don't match"))

# 		min_length = getattr(settings, "PASSWORD_MINIMUM_LENGTH", 4)
# 		if len(password1) < min_length:
# 			raise forms.ValidationError(_("Password is too short, minimum length is ") + "[%d]" % min_length)

# 		return password2




from smack.colleges import *
class SmackerForm(forms.ModelForm):
	college = forms.ChoiceField(widget=forms.Select, choices=COLLEGES)

	class Meta:
		model = Smacker
		# fields = UserCreationForm.Meta.fields + ('college', )
		fields = ('college', )



# class SmackerCreationForm(UserCreationForm):
# 	def __init__(self, *args, **kargs):
# 		super(SmackerCreationForm, self).__init__(*args, **kargs)
# 		del self.fields['username']

# 	class Meta:
# 		model = Smacker
# 		fields = ("email",)

# class SmackerUpdateForm(UserChangeForm):
# 	def __init__(self, *args, **kargs):
# 		super(SmackerUpdateForm, self).__init__(*args, **kargs)
# 		del self.fields['username']

# 	class Meta:
# 		model = Smacker
# 		fields = ("email",)