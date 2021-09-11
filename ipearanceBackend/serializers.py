# from rest-django documentation we took the model and create the serializers for data exchange with react-axios json format and auto complete methods in viewsAPI.py
from rest_framework import serializers
from ipearanceBackend.models import Users,Devices,Departments,Roles,Members_team,Signatures,Relation_types,Industry,Staff_attendance,Staff_attendance_rearranged_report,Staff_department_info,Holidays,Staff_holidays,Event_log
#from ipearanceBackend.models import Logotypo

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id','password','first_name','last_name','fathers_name','mothers_name','username','device_card_id','device_card_number','hrms_id','relation_type','phone', 'works_on_holidays','last_login','date_joined','email','is_active','is_superuser','is_staff','member_team_name')
        
class DevicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields=('id','device_location','device_ip','device_port','device_created_date')
        
class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields=('id','industry_id','parent_id', 'department_name','department_created_date') 

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields=('id','role_name','role_created_date')
        
class MembersTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Members_team
        fields=('id','member_team_name','member_team_weight','member_team_created_date') 

class SignaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signatures
        fields=('id','signature_name','signature_created_date')
        
class Relation_typesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation_types
        fields=('id','relation_type_name','relation_type_created_date')  

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields=('id','name','address','afm','logo','logoPath','general_work_range_from','general_work_range_to','hrms_connect','hrms_ip','hrms_port','hrms_service_name','hrms_username','hrms_password', 'hrms_schema','hrms_com_id','industry_settings_created_date')
        
class Staff_attendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff_attendance
        fields=('id','user_uid','user_card_number','user_card_id','username','device_name','attendance_dateTime','attendance_date','attendance_time')
        
class Staff_attendance_rearranged_reportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff_attendance_rearranged_report
        fields=('id','staff_card','username','device_name','department_name','attendance_time_in','attendance_time_out','attendance_time_in2','attendance_time_out2','day','wrario','should_work_hours','worked_hours_in_range','worked_hours','wrario2','should_work_hours2','worked_hours_in_range2','worked_hours2','attendance_rearranged_report_created_date')  

class Staff_department_infoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff_department_info
        fields=('id','department_id','staff_card','role','apply_from','apply_to','start_of_work','end_of_work','spasto','start_of_work2','end_of_work2','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','staff_department_info_created_date')
        
class HolidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holidays
        fields=('id','date_from','date_to','description','created_date')

class Staff_holidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff_holidays
        fields=('id','staff_card','hrms_id','date_from','date_to','description','created_date')
        
class Event_logSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event_log
        fields=('id','username','staff_card','function_event','ip_address','function_used_info','created_date') 
        
        
# class LogotypoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Logotypo
#         fields = ('id','Logotypo', 'industryname') 