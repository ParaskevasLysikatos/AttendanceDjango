# the methods that need to be executed in specific time of day and transfer yesterday attendances to new table with calculations, the methods are changed to be testcase and cannot call other methods, they are executed in written order
from urllib import request
from django.contrib.auth.views import redirect_to_login
from zk import ZK, const
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.template import loader
import sys,os,re,cx_Oracle,locale,logging,urllib,pytz
from django.template.loader import render_to_string,get_template
from rest_framework import viewsets  
#import our logger to test things
from xhtml2pdf import pisa
#import our excel libraries, and for error
from django.core.files.storage import FileSystemStorage
from openpyxl import Workbook
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
sys.path.insert(1, os.path.abspath("./pyzk"))
from ipearanceBackend.forms import AddUserForm,EditUserForm
from django.contrib.auth.forms import SetPasswordForm
from datetime import datetime,timedelta,date,time
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import permission_required,login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.dateparse import parse_datetime,parse_date,parse_time,parse_duration
import dateutil.parser
from rest_framework.decorators import api_view
from io import BytesIO

from ipearanceBackend.models import Users,Devices,Departments,Industry,Staff_attendance,Staff_department_info,Staff_attendance_rearranged_report,Signatures,Holidays,Roles,Relation_types,Members_team,Staff_holidays,Event_log
from ipearanceBackend.serializers import UsersSerializer,DevicesSerializer,DepartmentsSerializer,RolesSerializer,IndustrySerializer,Staff_department_infoSerializer,SignaturesSerializer,MembersTeamSerializer,Relation_typesSerializer,Event_logSerializer,HolidaysSerializer,Staff_attendanceSerializer,Staff_attendance_rearranged_reportSerializer,Staff_holidaysSerializer
# from ipearanceBackend.models import Logotypo
# from ipearanceBackend.serializers import LogotypoSerializer
from rest_framework import generics
import os,re,struct,locale,cx_Oracle,logging
logger = logging.getLogger(__name__)
os.environ['PATH'] = 'C:\\instantclient_11_2'
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from ipware import get_client_ip
from django.test import TestCase
##

class SynchronizeAttendances(TestCase):
    if True:
        logger.error("sychronize attendances is running")
        dataSuccess=[]
        dataFail=[]
		yesterday=str(date.today()-timedelta(days=1))
        clocks=Devices.objects.all()
        for clock in clocks:
            #conn = None
            # create ZK instance
            zk = ZK(clock.device_ip, port=clock.device_port, timeout=5, password=0,
                    force_udp=False, ommit_ping=False)
            try:
                # connect to device
                conn = zk.connect()
                # disable device, this method ensures no activity on the device while the process is run
                conn.disable_device()
                users = conn.get_users()
                for user in users:
                    privilege = 'User'
                    if user.privilege == const.USER_ADMIN:
                        privilege = 'Admin'
                #print('+ UID #{}'.format(user.uid)) # normal id
                #print('  Name       : {}'.format(user.name))
                #print('  Privilege  : {}'.format(privilege))
                #print('  Password   : {}'.format(user.password))
                #print('  Group ID   : {}'.format(user.group_id))
                #print('  User  ID   : {}'.format(user.user_id)) # card id
                #print('  User  card   : {}'.format(user.card))#card number
                attendances = conn.get_attendance()
                fullatendances = []
                for attendance in attendances:
                    print(attendance)
                    attendancesplit = str(attendance).split()
                    print("------att----------")
                    for user in users:
                        print("------u----------")
                        print(user)
                        if(user.user_id == attendancesplit[1]):
                            
                        #print('{}'.format(user.name))
                            break
                #print(attendancesplit[0])
                #print(attendancesplit[1])
                #print(attendancesplit[2])
                #print(attendancesplit[3])
                #print(attendancesplit[4])
                #print(attendance)
				 #if attendancesplit[3]==yesterday:#  check machines only for one day(yesterday),run it after midnight
                    temp_date = parse_datetime(attendancesplit[3] + " " + attendancesplit[4])
                    try:
                        if Staff_attendance.objects.count()>0:
                            lastID=Staff_attendance.objects.order_by('id').last().id+1
                        else:
                            lastID=1
                        Staff_attendance.objects.create(
                            id=lastID,
                        attendance_date=parse_date(attendancesplit[3]),
                        attendance_time=parse_time(attendancesplit[4]),
                        attendance_dateTime=temp_date,
                        device_name=clock.device_location,
                        user_card_id=user.user_id,
                        username=user.name,
                        user_uid=user.uid,
                        user_card_number=user.card
                        )
                    except Exception as e:
                        print("Process terminate1 : {}".format(e))   
                conn.enable_device()
                conn.disconnect()
                #messages.success(request,clock.device_location+' έδωσε παρουσίες επιτυχώς')
                dataSuccess.append(clock.device_location)
            except Exception as e:
                print("Process terminate3 : {}".format(e))
                #messages.error(request,clock.device_location+' συσκευή δεν συνδέθηκε')
                dataFail.append(clock.device_location)
        #createAttendancesRearranged()#fill the reanrranged table 
        #deviceClear()
        logger.error("success all processes")           
        #return "success all processes"#JsonResponse({'messageSuccess':dataSuccess,'messageFail':dataFail},safe=False)
    

class createAttendancesRearranged(TestCase):
    #eventLogger(request,info="μέθοδος για δημιουργία παρουσιών σε πίνακα συγκετρωτικό έτρεξε")
    summaryTable=[]
    today = date.today()
    weekBeforeToday = today - timedelta(days = 3)#----how far in the past to look for attendaces to transfer
    queryTable={'staff_card':"",'device_name':"",'username':"",'department_name':"",'attendance_time_in':"",'attendance_time_out':"",'attendance_time_in2':"",'attendance_time_out2':"",'day':"",'should_work_hours':"",'worked_hours_in_range':"",'worked_hours':"",'wrario':"",'should_work_hours2':"",'worked_hours_in_range2':"",'worked_hours2':"",'wrario2':""}#wrario san ranges
    if Staff_attendance.objects.all().order_by('attendance_date')[0]: #check existance
        oldestDate=Staff_attendance.objects.all().order_by('attendance_date')[0].attendance_date
        latestDate=Staff_attendance.objects.all().order_by('-attendance_date')[0].attendance_date
        print(oldestDate)
        print(latestDate)
        for i in range((latestDate - weekBeforeToday).days):#+1 but we want leave last day
            #print((oldestDate+timedelta(days=i)).strftime("%Y-%m-%d"))
            if Staff_attendance.objects.filter(attendance_date=weekBeforeToday+timedelta(days=i)) is not None:# specific day, from begin
                one_record=Staff_attendance.objects.filter(attendance_date=weekBeforeToday+timedelta(days=i))#current record of day
                for one in one_record:
                    queryTable.clear()            
                    queryTable['day']=(weekBeforeToday+timedelta(days=i)).strftime("%Y-%m-%d")
                    queryTable['staff_card']=one.user_card_number
                    queryTable['username']=one.username
                    queryTable['device_name']=one.device_name
                    if Staff_department_info.objects.filter(staff_card=one.user_card_number).count()>0:#has dep,1 at moment
                        if Staff_department_info.objects.filter(staff_card=one.user_card_number,spasto=True):#has spasto
                            depStaff=Staff_department_info.objects.filter(staff_card=one.user_card_number).first()#1
                            queryTable['department_name']=Departments.objects.get(id=depStaff.department_id).department_name
                            s1=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work
                            s2=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work
                            s11=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work2
                            s22=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work2
                            
                            queryTable['should_work_hours']=str(timedelta(hours=s2.hour,minutes=s2.minute,seconds=s2.second)-timedelta(hours=s1.hour,minutes=s1.minute,seconds=s1.second))
                            queryTable['should_work_hours2']=str(timedelta(hours=s22.hour,minutes=s22.minute,seconds=s22.second)-timedelta(hours=s11.hour,minutes=s11.minute,seconds=s11.second))
                            
                            queryTable['wrario']=str(s1)+"-"+str(s2)
                            queryTable['wrario2']=str(s11)+"-"+str(s22)
                            att=Staff_attendance.objects.filter(attendance_date=weekBeforeToday+timedelta(days=i),user_card_number=one.user_card_number).order_by('id')
                        else:    
                            depStaff=Staff_department_info.objects.filter(staff_card=one.user_card_number).first()#1
                            queryTable['department_name']=Departments.objects.get(id=depStaff.department_id).department_name
                            s1=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work
                            s2=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work
                            queryTable['should_work_hours']=str(timedelta(hours=s2.hour,minutes=s2.minute,seconds=s2.second)-timedelta(hours=s1.hour,minutes=s1.minute,seconds=s1.second))
                            queryTable['wrario']=str(s1)+"-"+str(s2)
                            att=Staff_attendance.objects.filter(attendance_date=weekBeforeToday+timedelta(days=i),user_card_number=one.user_card_number).order_by('id')
                            
                        if Staff_attendance.objects.filter(attendance_date=weekBeforeToday+timedelta(days=i),user_card_number=one.user_card_number).count()>=1 and not Staff_department_info.objects.filter(staff_card=one.user_card_number,spasto=True) :#has dep ,oxi spasto
                            attLast=att.last()
                            # if att.count() % 2==1 : # monos arithmos gia afikseis
                            #     queryTable['attendance_time_in']=attLast.attendance_time
                            #     queryTable['attendance_time_out']=time(0,0,0)#panta gia mona prepei apoxwriseis
                            # else:
                            for counter in range(0,att.count(),2):
                            #for countAtt in att:
                                ii=1
                                try:
                                    if not att[counter].attendance_time==attLast.attendance_time:#not last and first time
                                        if ii % 2==1:
                                            queryTable['attendance_time_in']=att[counter].attendance_time#(att[att.count()-2]).attendance_time #pisw apo last h afiksi
                                            ii+=1
                                        if ii % 2==0 :
                                            queryTable['attendance_time_out']=att[counter+1].attendance_time# apoxwrisi 
                                            print(str(queryTable.get('attendance_time_in'))+"---"+str(queryTable.get('attendance_time_out')))    
                                            queryTable['worked_hours']=str(timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second)-timedelta(hours=queryTable.get('attendance_time_in').hour,minutes=queryTable.get('attendance_time_in').minute,seconds=queryTable.get('attendance_time_in').second))
                        
                                            ds1=timedelta(hours=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work.hour,minutes=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work.minute,seconds=0)
                                            ds2=timedelta(hours=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work.hour,minutes=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work.minute,seconds=0)
                                            print("ela1")
                                            if ds1>timedelta(hours=queryTable.get('attendance_time_in').hour,minutes=queryTable.get('attendance_time_in').minute,seconds=queryTable.get('attendance_time_in').second):
                                                rs1=ds1
                                            else:
                                                rs1=timedelta(hours=queryTable.get('attendance_time_in').hour,minutes=queryTable.get('attendance_time_in').minute,seconds=queryTable.get('attendance_time_in').second)
                                            print("ela2")
                                            if ds2<timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second):
                                                rs2=ds2
                                            else:
                                                rs2=timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second)
                                                print("ela3")
                                            if rs2-rs1<timedelta(0):
                                                queryTable['worked_hours_in_range']=time(0,0,0)
                                            else:
                                                queryTable['worked_hours_in_range']=str(rs2-rs1)
                                            print("ela4************************************")
                                
                                    else:#'ε΄΄λλειπες χτυπημα' με τμημα,oxi spasto
                                        queryTable['worked_hours_in_range']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                                        queryTable['worked_hours_in_range2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                                        queryTable['attendance_time_in']=att.last().attendance_time
                                        queryTable['attendance_time_out']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                                        queryTable['attendance_time_in2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                                        queryTable['attendance_time_out2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                                        queryTable['worked_hours']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                                        queryTable['worked_hours2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα' 
                                except Exception as e:
                                    print("Process terminate out of bound for att : {}".format(e))
                                try:
                                    if Staff_attendance_rearranged_report.objects.count()>0:
                                        lastID=Staff_attendance_rearranged_report.objects.order_by('id').last().id+1
                                    else:
                                        lastID=1
                                    Staff_attendance_rearranged_report.objects.create(
                                        id=lastID,
                                    staff_card =queryTable.get('staff_card'),
                                    username=queryTable.get('username'),
                                    device_name=queryTable.get('device_name'),
                                    department_name=queryTable.get('department_name'),
                                    attendance_time_in =queryTable.get('attendance_time_in'),
                                    attendance_time_out=queryTable.get('attendance_time_out'),
                                    attendance_time_in2 = queryTable.get('attendance_time_in2'),
                                    attendance_time_out2 =queryTable.get('attendance_time_out2'),
                                    day = parse_date(queryTable.get('day')),
                                    wrario=queryTable.get('wrario'),
                                    wrario2=queryTable.get('wrario2'),
                                    should_work_hours=queryTable.get('should_work_hours'),
                                    should_work_hours2=queryTable.get('should_work_hours2'),
                                    worked_hours_in_range=queryTable.get('worked_hours_in_range'),
                                    worked_hours_in_range2=queryTable.get('worked_hours_in_range2'),
                                    worked_hours =queryTable.get('worked_hours'),
                                    worked_hours2 =queryTable.get('worked_hours2')
                                    )
                                except Exception as e:
                                    print("Process terminate create row : {}".format(e))
                                summaryTable.append(queryTable.copy())
                                #queryTable.clear()
                           
                        elif Staff_department_info.objects.filter(staff_card=one.user_card_number,spasto=True):#has spasto, calulate
                            queryTable['attendance_time_in']=att.first().attendance_time#1
                            try:
                                queryTable['attendance_time_out']=att[1].attendance_time#2
                            except Exception as e:
                                print("no second hit spasto : {}".format(e))
                                queryTable['attendance_time_out']=time(0,0,0)#2
                            try:
                                queryTable['attendance_time_in2']=att[2].attendance_time#3
                            except Exception as e:
                                print("no third hit spasto : {}".format(e))
                                queryTable['attendance_time_in2']=time(0,0,0)#3
                            try:
                                queryTable['attendance_time_out2']=att[3].attendance_time#4
                            except Exception as e:
                                print("no fourth hit spasto : {}".format(e))
                                queryTable['attendance_time_out2']=time(0,0,0)#4
                            queryTable['worked_hours']=str(timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second)-timedelta(hours=att.first().attendance_time.hour,minutes=att.first().attendance_time.minute,seconds=att.first().attendance_time.second))
                            queryTable['worked_hours2']=str(timedelta(hours=queryTable.get('attendance_time_out2').hour,minutes=queryTable.get('attendance_time_out2').minute,seconds=queryTable.get('attendance_time_out2').second)-timedelta(hours=queryTable.get('attendance_time_in2').hour,minutes=queryTable.get('attendance_time_in2').minute,seconds=queryTable.get('attendance_time_in2').second))
                            
                            ds1=timedelta(hours=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work.hour,minutes=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work.minute,seconds=0)
                            ds2=timedelta(hours=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work.hour,minutes=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work.minute,seconds=0)
                            ds11=timedelta(hours=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work2.hour,minutes=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).start_of_work2.minute,seconds=0)
                            ds22=timedelta(hours=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work2.hour,minutes=Staff_department_info.objects.get(staff_card=one.user_card_number,department_id=depStaff.department_id).end_of_work2.minute,seconds=0)
                            
                            if ds1>timedelta(hours=att.first().attendance_time.hour,minutes=att.first().attendance_time.minute,seconds=att.first().attendance_time.second):
                                rs1=ds1
                            else:
                                rs1=timedelta(hours=att.first().attendance_time.hour,minutes=att.first().attendance_time.minute,seconds=att.first().attendance_time.second)
                            
                            if ds2<timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second):
                                rs2=ds2
                            else:
                                rs2=timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second)
                                
                            
                            if ds11>timedelta(hours=queryTable.get('attendance_time_in2').hour,minutes=queryTable.get('attendance_time_in2').minute,seconds=queryTable.get('attendance_time_in2').second):
                                rs11=ds11
                            else:
                                rs11=timedelta(hours=queryTable.get('attendance_time_in2').hour,minutes=queryTable.get('attendance_time_in2').minute,seconds=queryTable.get('attendance_time_in2').second)
                            
                            if ds22<timedelta(hours=queryTable.get('attendance_time_out2').hour,minutes=queryTable.get('attendance_time_out2').minute,seconds=queryTable.get('attendance_time_out2').second):
                                rs22=ds22
                            else:
                                rs22=timedelta(hours=queryTable.get('attendance_time_out2').hour,minutes=queryTable.get('attendance_time_out2').minute,seconds=queryTable.get('attendance_time_out2').second)
                                
                            if rs2-rs1<timedelta(0):
                                queryTable['worked_hours_in_range']=time(0,0,0)
                            else:
                                queryTable['worked_hours_in_range']=str(rs2-rs1)
                                
                            if rs22-rs11<timedelta(0):
                                queryTable['worked_hours_in_range2']=time(0,0,0)
                            else:
                                queryTable['worked_hours_in_range2']=str(rs22-rs11)
                            try:
                                if Staff_attendance_rearranged_report.objects.count()>0:
                                    lastID=Staff_attendance_rearranged_report.objects.order_by('id').last().id+1
                                else:
                                    lastID=1
                                Staff_attendance_rearranged_report.objects.create(
                                    id=lastID,
                                staff_card =queryTable.get('staff_card'),
                                username=queryTable.get('username'),
                                device_name=queryTable.get('device_name'),
                                department_name=queryTable.get('department_name'),
                                attendance_time_in =queryTable.get('attendance_time_in'),
                                attendance_time_out=queryTable.get('attendance_time_out'),
                                attendance_time_in2 = queryTable.get('attendance_time_in2'),
                                attendance_time_out2 =queryTable.get('attendance_time_out2'),
                                day = parse_date(queryTable.get('day')),
                                wrario=queryTable.get('wrario'),
                                wrario2=queryTable.get('wrario2'),
                                should_work_hours=queryTable.get('should_work_hours'),
                                should_work_hours2=queryTable.get('should_work_hours2'),
                                worked_hours_in_range=queryTable.get('worked_hours_in_range'),
                                worked_hours_in_range2=queryTable.get('worked_hours_in_range2'),
                                worked_hours =queryTable.get('worked_hours'),
                                worked_hours2 =queryTable.get('worked_hours2')
                                )
                            except Exception as e:
                                print("Process terminate create row : {}".format(e))
                            summaryTable.append(queryTable.copy())
                            queryTable.clear() 
                            #-----------------------spasto telos------------------------
                                  
                        # else:#'ε΄΄λλειπες χτυπημα' με τμημα,oxi spasto
                        #     queryTable['worked_hours_in_range']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                        #     queryTable['worked_hours_in_range2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                        #     queryTable['attendance_time_in']=att.last().attendance_time
                        #     queryTable['attendance_time_out']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                        #     queryTable['attendance_time_in2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                        #     queryTable['attendance_time_out2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                        #     queryTable['worked_hours']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'
                        #     queryTable['worked_hours2']=time(0,0,0)#'ε΄΄λλειπες χτυπημα'          
                    else:#"ΧΩΡΙΣ ΤΜΗΜΑ"
                        print("ela5-------------------------------")
                        queryTable['department_name']="ΧΩΡΙΣ ΤΜΗΜΑ"
                        queryTable['should_work_hours']=time(0,0,0)#'----'
                        queryTable['wrario']=time(0,0,0)#'----'
                        queryTable['worked_hours_in_range']=time(0,0,0)
                        att=Staff_attendance.objects.filter(attendance_date=weekBeforeToday+timedelta(days=i),user_card_number=one.user_card_number).order_by('attendance_dateTime')
                        attLast=att.last()
                        for counter in range(0,att.count(),2):
                        #for countAtt in att:
                            ii=1
                            try:
                                if not att[counter].attendance_time==attLast.attendance_time:
                                    if ii % 2==1:
                                        queryTable['attendance_time_in']=att[counter].attendance_time#(att[att.count()-2]).attendance_time #pisw apo last h afiksi
                                        ii+=1
                                    if ii % 2==0 :
                                        queryTable['attendance_time_out']=att[counter+1].attendance_time# apoxwrisi 
                                        queryTable['worked_hours']=str(timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second)-timedelta(hours=queryTable.get('attendance_time_in').hour,minutes=queryTable.get('attendance_time_in').minute,seconds=queryTable.get('attendance_time_in').second))
                                else:
                                    queryTable['attendance_time_in']=attLast.attendance_time
                                    queryTable['attendance_time_out']=time(0,0,0)#panta gia mona prepei apoxwriseis
                                    queryTable['worked_hours']=time(0,0,0)#'ελλιπές χτύπημα'
                            except Exception as e:
                                print("Process terminate out of bound for att,no dep : {}".format(e))
                            try:
                                if Staff_attendance_rearranged_report.objects.count()>0:
                                    lastID=Staff_attendance_rearranged_report.objects.order_by('id').last().id+1
                                else:
                                    lastID=1
                                Staff_attendance_rearranged_report.objects.create(
                                    id=lastID,
                                staff_card =queryTable.get('staff_card'),
                                username=queryTable.get('username'),
                                device_name=queryTable.get('device_name'),
                                department_name=queryTable.get('department_name'),
                                attendance_time_in =queryTable.get('attendance_time_in'),
                                attendance_time_out=queryTable.get('attendance_time_out'),
                                attendance_time_in2 = queryTable.get('attendance_time_in2'),
                                attendance_time_out2 =queryTable.get('attendance_time_out2'),
                                day = parse_date(queryTable.get('day')),
                                wrario=queryTable.get('wrario'),
                                wrario2=queryTable.get('wrario2'),
                                should_work_hours=queryTable.get('should_work_hours'),
                                should_work_hours2=queryTable.get('should_work_hours2'),
                                worked_hours_in_range=queryTable.get('worked_hours_in_range'),
                                worked_hours_in_range2=queryTable.get('worked_hours_in_range2'),
                                worked_hours =queryTable.get('worked_hours'),
                                worked_hours2 =queryTable.get('worked_hours2')
                                )
                            except Exception as e:
                                print("Process terminate create row : {}".format(e))
                            summaryTable.append(queryTable.copy())
                            #queryTable.clear()
                    
    #print(summaryTable)
    logger.error("sychronize attendances finished")
    
    
class deviceClear(TestCase):
    clocks=Devices.objects.all()
    for clock in clocks:
        conn = None
        # create ZK instance
        zk = ZK(clock.device_ip, port=clock.device_port, timeout=5, password=0,
                force_udp=False, ommit_ping=False)
        try:
            # connect to device
            conn = zk.connect()
            # disable device, this method ensures no activity on the device while the process is run
            conn.disable_device()
            conn.clear_attendance()#delete all attendances of the device
            newtime = datetime.today()
            conn.set_time(newtime)
            # re-enable device after all commands already executed
            conn.enable_device()
            conn.disconnect()
        except Exception as e:
            print("not connected: "+clock.device_location)
            
    logger.error("clear finished")
    
    #return "success devices clear and time"#JsonResponse({'messageSuccess':dataSuccess,'messageFail':dataFail},safe=False)