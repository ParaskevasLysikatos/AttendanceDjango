#django forms is used only on bootstrap (frontend--viewsMain)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # to use the auth model of user in the form
User = get_user_model()# now on submit the auth user model will be used and django validators forms will ba applied
from ipearanceBackend.models import Relation_types,Members_team
from django.forms import ModelChoiceField

class AddUserForm(UserCreationForm): #the custom auth user form
    device_card_number = forms.IntegerField(label="CARD Number:",required=True)# extra field
    hrms_id=forms.IntegerField(required=False)
    
    fathers_name = forms.CharField(required=False,label="Πατρώνυμο:",initial='')
    mothers_name = forms.CharField(required=False,label="Μητρώνυμο:",initial='')
    
    works_on_holidays = forms.BooleanField(required=False,label="Εργάζεται στις αργίες:")
    
    member_team_name=forms.ModelChoiceField(queryset=Members_team.objects.distinct('member_team_name'),label="Μέλoς ομάδας",to_field_name='id',initial=1,required=True)
    phone = forms.IntegerField(required=False,label="Τηλέφωνο:",initial='')
    
    relation_type = forms.ModelChoiceField(queryset=Relation_types.objects.distinct('relation_type_name'),label="Σχέση εργασίας",to_field_name='id',initial=1,required=True)
    
    password1=forms.CharField(help_text='Ο κωδικός σας πρέπει να έχει τουλάχιστον 3 χαρακτήρες.',widget=forms.PasswordInput,required=True,initial='',label="Κωδικός:")
    
    password2=forms.CharField(help_text='Εισάγετε το ίδιο κωδικό όπως πρίν, για επιβεβαίωση.',widget=forms.PasswordInput,required=True,initial='',label="Κωδικός επιβεβαίωσης:")
    
    class Meta:#based on model for submit, which fields will appear
        model = User
        fields = ('username', 'first_name','last_name','email','hrms_id','fathers_name','mothers_name','device_card_number', 'member_team_name','phone','works_on_holidays','relation_type','password1', 'password2')
        
    def clean(self):# to adjust types automatically, also for extra messages to raise (optional)
        cleaned_data = super(AddUserForm, self).clean()

class EditUserForm(forms.ModelForm): #the custom edit user form
    hrms_id=forms.IntegerField(required=False,label="HRMS ID:",initial='')
    device_card_id = forms.IntegerField(label="CARD ID:",required=True)# extra field
    device_card_number = forms.IntegerField(label="CARD NUMBER:",required=True)
    
    username=forms.CharField()
    first_name=forms.CharField(label="Όνομα:",required=True)
    last_name=forms.CharField(label="Επώνυμο:",required=True)
    fathers_name = forms.CharField(required=False,label="Πατρώνυμο:",initial='')
    mothers_name = forms.CharField(required=False,label="Μητρώνυμο:",initial='')
    
    works_on_holidays = forms.BooleanField(required=False,label="Εργάζεται στις αργίες:")
    
    member_team_name=forms.ModelChoiceField(queryset=Members_team.objects.distinct('member_team_name'),label="Μέλoς ομάδας",to_field_name='id',required=True)
    phone = forms.IntegerField(required=False,label="Τηλέφωνο:",initial='')
    email=forms.EmailField(label="Email")
    
    password=forms.CharField(help_text='Σημπληρώστε μόνο για αλλαγή κωδικού',widget=forms.PasswordInput,required=False,initial='',label="Κωδικός:")
    
    relation_type = forms.ModelChoiceField(queryset=Relation_types.objects.distinct('relation_type_name'),label="Σχέση εργασίας",to_field_name='id',required=True)
    class Meta:#based on model for submit, which fields will appear
        model = User
        fields = ('hrms_id','device_card_number','device_card_id','username', 'first_name','last_name','fathers_name','mothers_name','works_on_holidays','relation_type','phone','email','password','member_team_name')
        
    def clean(self):# to adjust types automatically, also for extra messages to raise (optional)
        cleaned_data = super(EditUserForm, self).clean()