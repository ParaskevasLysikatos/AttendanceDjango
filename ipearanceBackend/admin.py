from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # inherit admin from django encryption
# Register your models here.
from django.contrib.auth.models import User
#from .models import Users
from .models import Users,Devices,Departments,Roles,Members_team,Signatures,Relation_types,Industry,Staff_attendance,Staff_attendance_rearranged_report,Staff_department_info,Holidays,Staff_holidays,Event_log,LoggedIn #, Logotypo

# the admin panel of django, can de accessed by creating a superuser or from db in users table field is_superuser=true
#fields what can be edited
#list_display which fields are seen on table view


@admin.register(User, Users)
class UsersCustom(admin.ModelAdmin): # inherit special admin encryption and features
    fields = ('first_name','last_name','fathers_name','mothers_name','username','device_card_id','device_card_number','hrms_id','relation_type','phone', 'works_on_holidays','last_login','date_joined','email','is_active','is_superuser','is_staff','member_team_name')#no password, to change use the below commented class
    list_display = ('id','password','first_name','last_name','fathers_name','mothers_name','username','device_card_id','device_card_number','hrms_id','relation_type','phone', 'works_on_holidays','last_login','date_joined','email','is_active','is_superuser','is_staff','member_team_name')

#-----------------for change password in admin panel, the above is to change all fields
# @admin.register(User, Users)
# class UsersCustom(UserAdmin): # inherit special admin encryption and features
#     #fields = ('first_name','last_name','fathers_name','mothers_name','username','device_card_id','device_card_number','hrms_id','relation_type','phone', 'works_on_holidays','last_login','ip_address','date_joined','email','is_active','is_superuser','is_staff')
#     list_display = ('id','password','first_name','last_name','fathers_name','mothers_name','username','device_card_id','device_card_number','hrms_id','relation_type','phone', 'works_on_holidays','last_login','ip_address','date_joined','email','is_active','is_superuser','is_staff','member')

@admin.register(Devices)
class DevicesAdmin(admin.ModelAdmin):
    fields =('device_location','device_ip','device_port')
    list_display =('id','device_location','device_ip','device_port','device_created_date')

@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
    fields =('industry_id','parent_id','department_name')
    list_display=('id','industry_id','parent_id', 'department_name','department_created_date') 

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    fields=('role_name',)
    list_display=('id','role_name','role_created_date') 
    
@admin.register(Members_team)
class MembersTeamAdmin(admin.ModelAdmin):
    fields =('member_team_name','member_team_weight')
    list_display=('id','member_team_name','member_team_weight','member_team_created_date') 
    
@admin.register(Signatures)
class SignaturesAdmin(admin.ModelAdmin):
    fields=('signature_name',)
    list_display=('id','signature_name','signature_created_date')
    
@admin.register(Relation_types)
class Relation_typesAdmin(admin.ModelAdmin):
    fields=('relation_type_name',)
    list_display=('id','relation_type_name','relation_type_created_date')  

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    fields=('name','address','afm','logo','logoPath','general_work_range_from','general_work_range_to','hrms_connect','hrms_ip','hrms_port','hrms_service_name','hrms_username','hrms_password', 'hrms_schema','hrms_com_id')
    list_display=('id','name','address','afm','logo','logoPath','general_work_range_from','general_work_range_to','hrms_connect','hrms_ip','hrms_port','hrms_service_name','hrms_username','hrms_password', 'hrms_schema','hrms_com_id','industry_settings_created_date')

@admin.register(Staff_attendance)
class Staff_attendanceAdmin(admin.ModelAdmin):
    fields=('user_card_number','user_card_id','user_uid','username','device_name','attendance_dateTime','attendance_date','attendance_time')
    list_display=('id','user_card_number','user_card_id','user_uid','username','device_name','attendance_dateTime','attendance_date','attendance_time')
    
@admin.register(Staff_attendance_rearranged_report)
class Staff_attendance_rearranged_reportAdmin(admin.ModelAdmin):
    fields=('staff_card','username','attendance_time_in','device_name','department_name','attendance_time_out','attendance_time_in2','attendance_time_out2','day','should_work_hours','worked_hours_in_range','worked_hours','wrario','should_work_hours2','worked_hours_in_range2','worked_hours2','wrario2')
    list_display=('id','staff_card','username','device_name','department_name','attendance_time_in','attendance_time_out','attendance_time_in2','attendance_time_out2','day','should_work_hours','worked_hours_in_range','worked_hours','wrario','should_work_hours2','worked_hours_in_range2','worked_hours2','wrario2','attendance_rearranged_report_created_date') 
     

@admin.register(Staff_department_info)
class  Staff_department_infoAdmin(admin.ModelAdmin):
    fields=('department_id','staff_card','role','apply_from','apply_to','start_of_work','end_of_work','spasto','start_of_work2','end_of_work2','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
    list_display=('id','department_id','staff_card','role','apply_from','apply_to','start_of_work','end_of_work','spasto','start_of_work2','end_of_work2','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','staff_department_info_created_date')

@admin.register(Holidays)
class HolidaysAdmin(admin.ModelAdmin):
    fields=('date_from','date_to','description')
    list_display=('id','date_from','date_to','description','created_date')

@admin.register(Staff_holidays)
class Staff_holidaysAdmin(admin.ModelAdmin):
    fields=('staff_card','hrms_id','date_from','date_to','description')
    list_display=('id','staff_card','hrms_id','date_from','date_to','description','created_date')
    
@admin.register(Event_log)
class Event_logAdmin(admin.ModelAdmin):
    fields=('username','staff_card','function_event','ip_address','function_used_info')
    list_display=('id','username','staff_card','function_event','ip_address','function_used_info','created_date')


# @admin.register(Logotypo)
# class LogotypoAdmin(admin.ModelAdmin):
#     fields =('logotypo','industryname')
#     list_display =('id','logotypo','industryname')

@admin.register(LoggedIn)
class Event_logAdmin(admin.ModelAdmin):
    fields=('username','user_card','user_member','token')
    list_display=('id','username','user_card','user_member','token')



 
    