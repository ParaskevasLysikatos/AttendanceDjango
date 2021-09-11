#the structure of database, each model is database table
from django.db import models
from django.contrib.auth.models import AbstractUser # for user auth
from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location='/media/')
#from datetimeutc.fields import DateTimeUTCField
# Create your models here.

class Users(AbstractUser): # to be mix of django custom user, also has:[ is_superuser, id,is_staff]
    # is_active = models.BooleanField()  auth has it
    # first_name = models.CharField(max_length=100) auth has it
    # last_name = models.CharField(max_length=100) auth has it
    # password = models.CharField(max_length=100) auth has it
    #date_joined = models.DateTimeField(auto_now_add=True) auth has it as date_joined (created_on)
    #last_login = models.DateTimeField(null=True) auth has it
    username = models.CharField(max_length=100,unique=True,null=False,blank=False) #auth has it, but does not allow space
    email = models.EmailField(unique=True,null=True,blank=True,max_length=150) #auth has it,but was not unique
    device_card_id = models.IntegerField(null=True,blank=True,unique=True) 
    device_card_number = models.IntegerField(null=True,unique=True,blank=True)
    hrms_id = models. IntegerField(null=True,blank=True)#not all users have hrms
    relation_type = models.CharField(max_length=100, null = True,blank=True)
    #relation_type = models.ForeignKey(Relation_types,to_field='relation_type_name',on_delete=models.CASCADE,verbose_name='relation_type_name')
    fathers_name = models.CharField(max_length=100, null = True,blank=True)
    mothers_name = models.CharField(max_length=100, null = True,blank=True)
    phone = models.BigIntegerField(null = True,blank=True)
    works_on_holidays = models.BooleanField(default=False)
    member_team_name=models.CharField(max_length=100, null = True,blank=True)# for view restrictions
    class Meta:
        unique_together = ('first_name','last_name','fathers_name')
    def __str__(self):
        ret = self.username + ',' + self.first_name + "," + self.last_name+ ","+str(self.device_card_id)+","+str(self.device_card_number)+","+self.email+','+str(self.hrms_id) +','+str(self.is_active) +','+str(self.relation_type)+','+str(self.fathers_name)+','+str(self.mothers_name)+','+str(self.phone)+','+str(self.works_on_holidays)+','+str(self.member_team_name)
        return ret
        
class Devices(models.Model):
    device_location = models.CharField(max_length=100,unique=True,null = False,blank=False)
    device_ip = models.CharField(max_length=100,unique=True,null = False,blank=False)
    device_port = models.IntegerField(null = False,blank=False)
    device_created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        ret = self.device_location+','+str(self.device_ip)+','+str(self.device_port)
        return ret
        
class Departments(models.Model):
    industry_id = models.IntegerField(null = False,blank=False) # the industry is whole municipality, which everything goes under it
    parent_id = models.IntegerField(null = False,blank=False) # shows which department has the connection to under it
    department_name = models.CharField(max_length = 100,unique=True,null = False,blank=False)
    department_created_date = models.DateTimeField(auto_now_add = True)
    active=models.BooleanField(default=True)
    def __str__(self):
        ret = str(self.industry_id)+ "," + str(self.parent_id) + ',' + self.department_name + "," + str(self.id)
        return ret
        
class Roles(models.Model): # same as staff_roles
    role_name = models.CharField(max_length = 100,unique=True,null=False,blank=False)# same as Department field id above
    role_created_date = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        ret = str(self.id) + "," +self.role_name
        return ret
        
        
class Relation_types(models.Model): # same as groups, control the views
    relation_type_name = models.CharField(max_length = 100,unique=True,null=False,blank=False)# same as Department field id above
    relation_type_created_date = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        ret = self.relation_type_name #str(self.id) + "," + for user edit form
        return ret
  
            
class Members_team(models.Model): # same as groups, control the views
    member_team_name = models.CharField(max_length = 100,unique=True,null=False,blank=False)# same as Department field id above
    member_team_weight = models.IntegerField(null=False,blank=False,unique=True)
    member_team_created_date = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        ret = self.member_team_name #+","+str(self.member_team_weight) str(self.id) + "," + for user edit form
        return ret
        
class Signatures(models.Model): # same as groups, control the views
    signature_name = models.CharField(max_length = 100,unique=True,null=False,blank=False)# same as Department field id above
    signature_created_date = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        ret = str(self.id) + "," +self.signature_name
        return ret
        

        
class Industry(models.Model): # industry and industry settings from previous
    name=models.CharField(max_length=100,null=False,blank=False,unique=True)
    address=models.CharField(max_length=100,null=False,blank=False)
    afm=models.IntegerField(null=False,blank=False,unique=True)
    logo=models.ImageField(storage=fs,null=True,blank=True,max_length=200)
    logoPath=models.CharField(max_length=300,null=True,blank=True)
    general_work_range_from=models.TimeField(null=True,blank=True)
    general_work_range_to=models.TimeField(null=True,blank=True)
    hrms_connect=models.BooleanField(default=False)
    hrms_ip = models.CharField(max_length=100,null=True,blank=True)
    hrms_port = models.IntegerField(null=True,blank=True)
    hrms_service_name = models.CharField(max_length=100,null=True,blank=True)
    hrms_username = models.CharField(max_length=100,null=True,blank=True)
    hrms_password = models.CharField(max_length=100,null=True,blank=True)
    hrms_schema=models.CharField(max_length=100,null=True,blank=True)
    hrms_com_id=models.IntegerField(unique=True,null=True,blank=True)
    industry_settings_created_date = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        ret = str(self.id)  + "," +  str(self.hrms_ip)+ "," +str(self.hrms_port)+"," +str(self.hrms_com_id)+"," +str(self.hrms_service_name)+"," +str(self.hrms_username)+"," +str(self.hrms_password)+"," +str(self.hrms_connect)+","+str(self.name)  + "," +  str(self.address)+ "," +str(self.afm)+"," +str(self.logo)
        return ret

class Staff_attendance(models.Model):
    user_card_number=models.IntegerField(null=False,blank=False)#user.card in the library,device_card_number
    user_card_id = models.IntegerField(null=False,blank=False)#user.user_id in the library,device_card_id
    user_uid = models.IntegerField(null=False,blank=False)#user.uid in the library,id of user model
    username=models.CharField(max_length=100,null=False,blank=False)#user.name in the library,username
    device_name=models.CharField(max_length=100,null=False,blank=False)
    attendance_dateTime = models.DateTimeField(null=False,blank=False)
    attendance_date = models.DateField(null=False,blank=False)
    attendance_time = models.TimeField(null=False,blank=False)
    class Meta:
        unique_together = ('user_card_number','attendance_dateTime')
        unique_together = ('user_card_id','attendance_dateTime')
        unique_together = ('user_uid','attendance_dateTime')
    def __str__(self):
        ret = str(self.user_uid)  + "," + self.username+ "," +self.device_name+","+str(self.attendance_date)+","+str(self.attendance_time)+ "," + str(self.user_card_number)+ "," + str(self.user_card_id)
        return ret
        
class Staff_attendance_rearranged_report(models.Model):
    #staff_id = models.IntegerField(null=False,blank=False)#user_card_id,device_card_id
    staff_card = models.IntegerField(null=False,blank=False)#user.card_number,device_card_number
    #staff_uid = models.IntegerField(null=False,blank=False)#user_uid,id of user model
    username=models.CharField(max_length=100,null=False,blank=False)#user.name in the library,username
    device_name=models.CharField(max_length=100,null=False,blank=False)
    department_name=models.CharField(max_length=100,null=False,blank=False)
    attendance_time_in = models.TimeField(null=True)
    attendance_time_out = models.TimeField(null=True)
    attendance_time_in2 = models.TimeField(null=True)#spasto wrario
    attendance_time_out2 = models.TimeField(null=True)#spasto wrario
    day = models.DateField(null=False,blank=False)
    wrario=models.CharField(max_length=100,null=True,blank=True)#range to wrario 8:00-15:00
    should_work_hours = models.TimeField(null=True,blank=True)#subtract official end work -start work
    worked_hours_in_range = models.TimeField(null=True)# in official range the amount of worked hours
    worked_hours = models.TimeField(null=True)#subtract entry last of day - first of day, the real worked hours
    wrario2=models.CharField(max_length=100,null=True,blank=True)#range to wrario 8:00-15:00
    should_work_hours2 = models.TimeField(null=True,blank=True)#subtract official end work -start work
    worked_hours_in_range2 = models.TimeField(null=True)# in official range the amount of worked hours
    worked_hours2 = models.TimeField(null=True)#subtract entry last of day - first of day, the real worked hours
    attendance_rearranged_report_created_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('staff_card','day','attendance_time_in')
    def __str__(self):
        ret = str(self.staff_card)+","+ str(self.username)+","+str(self.attendance_time_in) + "," + str(self.attendance_time_out) + "," +str(self.attendance_time_in2) + ","+str(self.attendance_time_out2) + "," + str(self.day) + ','+str(self.wrario) + ","  + str(self.should_work_hours) + ',' + str(self.worked_hours_in_range)+ ',' + str(self.worked_hours)+ ','+str(self.wrario2) + ","  + str(self.should_work_hours2) + ',' + str(self.worked_hours_in_range2)+ ',' + str(self.worked_hours2)+","+str(self.department_name)
        return ret
      
class Staff_department_info(models.Model):# includes work_dates and ranges
    department_id = models.IntegerField(null=False,blank=False)# same as Department field id above
    #staff_id = models.IntegerField(null=False,blank=False)# same as Users field device_card_id
    staff_card=models.IntegerField(null=False,blank=False)# same as Users field device_card_number
    role = models.CharField(max_length=100,null=False,blank=False)
    apply_from = models.DateField(null=False,blank=False)#diarkeia ergasias
    apply_to = models.DateField(null=False,blank=False)#diarkeia ergasias
    start_of_work = models.TimeField(null=False,blank=False)#wrario
    end_of_work = models.TimeField(null=False,blank=False)#wrario
    spasto=models.BooleanField(default=False)
    start_of_work2 = models.TimeField(null=True,blank=True)#wrario2
    end_of_work2 = models.TimeField(null=True,blank=True)#wrario2
    Monday=models.BooleanField(default=True)
    Tuesday=models.BooleanField(default=True)
    Wednesday=models.BooleanField(default=True)
    Thursday=models.BooleanField(default=True)
    Friday=models.BooleanField(default=True)
    Saturday=models.BooleanField(default=False)
    Sunday=models.BooleanField(default=False)
    staff_department_info_created_date = models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together = ('staff_card','department_id')
    def __str__(self):
        ret = str(self.department_id) + ',' + self.role+ ',' + str(self.staff_card)+ "," +str(self.apply_from)+","+str(self.apply_to)+str(self.start_of_work)+","+str(self.end_of_work)+","+str(self.Monday)+","+str(self.Tuesday)+","+str(self.Wednesday)+","+str(self.Thursday)+","+str(self.Friday)+","+str(self.Saturday)+","+str(self.Sunday)
        return ret

class Holidays(models.Model):
    date_from = models.DateField(null=False,blank=False,unique=True)
    date_to = models.DateField(null=False,blank=False)
    description=models.CharField(max_length=100,null=False,blank=False)
    created_date=models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together = ('date_from','date_to')
    def __str__(self):
        ret=str(self.date_from)  + ","+str(self.date_to)  + ","+self.description
        return ret

class Staff_holidays(models.Model):
    #staff_id=models.IntegerField(null=False,blank=False)
    staff_card=models.IntegerField(null=False,blank=False)
    hrms_id=models.IntegerField(null=True,blank=True)
    first_name = models.CharField(max_length=100,null=False,blank=False)
    last_name = models.CharField(max_length=100,null=False,blank=False)
    date_from = models.DateTimeField(null=False,blank=False)
    date_to = models.DateTimeField(null=False,blank=False)
    description=models.CharField(max_length=100,null=False,blank=False)
    created_date=models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together = ('staff_card','date_from')
    def __str__(self):
        ret=str(self.date_from)  + ","+str(self.date_to)  + ","+self.description+ ","+str(self.staff_card)+ ","+str(self.hrms_id)
        return ret
    
class Event_log(models.Model):
    username=models.CharField(max_length=100,null=False,blank=False)
    staff_card=models.IntegerField(null=False,blank=False)
    ip_address = models.CharField(max_length=100,null = True,blank=True)
    function_event=models.CharField(max_length=100,null=False,blank=False)
    function_used_info=models.CharField(max_length=500,null=False,blank=False)
    created_date=models.DateTimeField(auto_now_add = True)
    def __str__(self):
        ret=str(self.username)  + ","+str(self.staff_card)  + ","+self.function_event+ ","+str(self.function_used_info)+ ","+str(self.created_date)  +","+str(self.ip_address)
        return ret
    
# def upload_to(instance, filename):
#     return 'logos/{filename}'.format(filename=filename)

# class Logotypo( models.Model):
#     logotypo = models.ImageField( upload_to = upload_to, default = "/icon.png")
#     industryname = models.ForeignKey(Industry, to_field="name", on_delete=models.SET_NULL, null=True)

class LoggedIn(models.Model):
    username = models.CharField(max_length=200,null=False,blank=False,unique=True)
    user_card = models.IntegerField(null=False,blank=False)
    user_member = models.IntegerField(null=False,blank=False)
    token = models.CharField(max_length=500,null=False,blank=False) 
    def __str__(self):
        ret=str(self.username)  + ","+str(self.user_card)  + ","+str(self.user_member)+ ","+str(self.token)
        return ret  
   


