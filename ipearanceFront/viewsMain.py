# all the methods except hrms of bootstrap front application,all the views are in templates folder
from urllib import request
from django.contrib.auth.views import redirect_to_login
from zk import ZK, const
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.template import loader
import sys,os,re,cx_Oracle,locale,logging,urllib,pytz,csv
from django.template.loader import render_to_string,get_template
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
from io import BytesIO
from django.contrib.staticfiles import finders
from ipearanceBackend.models import Users,Devices,Departments,Industry,Staff_attendance,Staff_department_info,Staff_attendance_rearranged_report,Signatures,Holidays,Roles,Relation_types,Members_team,Staff_holidays,Event_log
os.environ['PATH'] = 'C:\\instantclient_11_2'
logger = logging.getLogger(__name__)
from workalendar.europe import Greece
from django.db.models.functions import Lower,Upper
from .decorators import admin_required
from dateutil.relativedelta import relativedelta
from ipware import get_client_ip


def pagelogout(request):#log outs a user
    eventLogger(request,info="Χρήστης αποσυνδέθηκε")
    logout(request)
    messages.success(request, 'Έχετε αποσυνδεθεί')
    return redirect('pagelogin')

def pagelogin(request):
    if request.method == "GET": # if user just enters the login page, serve it 
        return render(request, 'login.html')
    else: # else open excel and take the login credentials and compare them with excel cells
        myU = request.POST.get('username')#take the credentials
        myPass = str(request.POST.get('password'))# for varchar password
        user = authenticate(request, username=myU, password=myPass)
        quser=Users.objects.filter(username=myU) # the query to examine if username exists
        logger.error(user)
        logger.error(quser)
        if user is not None:
            login(request,user)
            eventLogger(request,info="Χρήστης συνδέθηκε")
            messages.success(request, 'Έχετε συνδεθεί')
            return redirect('welcome')
        else:
            messages.error(request, 'λάθος στοιχεία χρήστη')
            if quser:# send extra message on failure if user exists
                messages.warning(request, 'Αυτό το username υπάρχει')
            return redirect('pagelogin')
        
@login_required()        
def welcome(request):
    users=Users.objects.count()
    departments=Departments.objects.count()
    eventLogger(request,info="Χρήστης μπήκε στην αρχική")
    return render(request, 'welcome.html',{'users':users,'departments':departments})
    
@login_required()        
def RecordAtt(request):
    if request.method == "POST" : 
        myDevice=request.POST.get('device_id')
        dev=Devices.objects.get(id=myDevice).device_location
        myUser=Users.objects.get(id=request.user.id)
        obj=Staff_attendance.objects.create(user_card_number=myUser.device_card_number,user_card_id=myUser.device_card_id,user_uid=myUser.id,username=myUser.username,device_name=dev,attendance_dateTime=datetime.now(),attendance_date=date.today(),attendance_time=datetime.now().strftime("%H:%M:%S"))
        messages.success(request, 'Παρουσία χρήστη καταγράφηκε: '+ myUser.username+" "+str(date.today())+"  "+str(datetime.now().strftime("%H:%M:%S"))+" "+dev)
        eventLogger(request,info="Χρήστης πάτησε καταγραφή παρουσίας με τιμές: "+str(obj))
        next = request.POST.get('next')  
        #return redirect('deviceSelect')
        return redirect(next)
    
@login_required()   
def eventLogger(request,info):
    client_ip, is_routable = get_client_ip(request)
    Event_log.objects.create(username=request.user.username,staff_card=request.user.device_card_number,function_event=request.path_info,function_used_info=info,ip_address=client_ip)

@admin_required
@login_required()    
def eventLogPage(request):
    if request.method == "GET" :
        if Event_log.objects.order_by('id'):
            myEvents=Event_log.objects.order_by('id')
            paginator = Paginator(myEvents, 10)
            page = request.GET.get('page', 1)
            try:
                events = paginator.page(page)
            except PageNotAnInteger:
                events = paginator.page(1)
            except EmptyPage:
                events = paginator.page(paginator.num_pages)
        else:
            events=''
        eventLogger(request,info="Χρήστης μπήκε στα συμβάντα")
        return render(request, 'EventsLog.html',{'Events':events})
    
    
@login_required()           
def NavGet(request): 
    if request.method == "GET" : 
        myDevice=list(Devices.objects.values())
        return JsonResponse(myDevice,safe=False)   

@admin_required            
@login_required()
def staffHolidays(request):
    if request.method == "GET" :
        users=Users.objects.order_by('id')
        if Staff_holidays.objects.order_by('id'):
            myStaffHolidays = Staff_holidays.objects.all()
            paginator = Paginator(myStaffHolidays, 6)
            page = request.GET.get('page', 1)
            try:
                staffholidays = paginator.page(page)
            except PageNotAnInteger:
                staffholidays = paginator.page(1)
            except EmptyPage:
                staffholidays = paginator.page(paginator.num_pages)
        else:
            myStaffHolidays=''
            paginator = Paginator(myStaffHolidays, 6)
            page = request.GET.get('page', 1)
            try:
                staffholidays = paginator.page(page)
            except PageNotAnInteger:
                staffholidays = paginator.page(1)
            except EmptyPage:
                staffholidays = paginator.page(paginator.num_pages)
        eventLogger(request,info="Χρήστης μπήκε άδειες προσωπικού")
        return render(request, 'Staff_holidays.html', {"StaffHolidays":staffholidays,"Users":users})
    else:
        userForHoliday = request.POST.get('userForHoliday')
        desc_holi_staff = request.POST.get('desc_holi_staff')
        startHoliday = request.POST.get('startHoliday')
        endHoliday = request.POST.get('endHoliday')
        new_startHoliday=dateutil.parser.parse(startHoliday, dayfirst = True,ignoretz=True)
        new_endHoliday=dateutil.parser.parse(endHoliday, dayfirst = True,ignoretz=True)
        if new_startHoliday>=new_endHoliday:
            messages.warning(request, 'αρχή ημερομηνίας μεγαλύτερη-ίση τελικής ημερομηνίας')
            return redirect('staffHolidays')
        if Staff_holidays.objects.filter(staff_card=userForHoliday):#check for holiday that already overrides user holiday
            for item in Staff_holidays.objects.filter(staff_card=userForHoliday):
                if (item.date_from + timedelta(hours=3))<=pytz.utc.localize(new_startHoliday) and pytz.utc.localize(new_startHoliday)<=(item.date_to + timedelta(hours=3)) or (item.date_from + timedelta(hours=3))<=pytz.utc.localize(new_endHoliday) and pytz.utc.localize(new_endHoliday)<=(item.date_to + timedelta(hours=3)):
                    messages.warning(request, 'χρήστης έχει άδεια που καλύπτει αυτην την άδεια')
                    return redirect('staffHolidays')         
        getUser=Users.objects.get(device_card_number=userForHoliday)
        sh=Staff_holidays(
        staff_card=userForHoliday,
        hrms_id=getUser.hrms_id,
        last_name=getUser.last_name,
        first_name=getUser.first_name,
        date_from=new_startHoliday,
        date_to=new_endHoliday,
        description=desc_holi_staff
        )
        sh.save()
        eventLogger(request,info="Χρήστης πρόσθεσε μία άδεια με τιμές: "+str(sh))
        messages.success(request, 'άδεια χρήστη προστέθηκε')
        return redirect('staffHolidays')
  
@admin_required    
@login_required()
def staffHolidayEdit(request):
    if request.method == "POST" :
        idStaffHol = request.POST.get('id')
        userForHoliday = request.POST.get('userForHoliday')
        desc_holi_staff = request.POST.get('desc')
        startHolidayE = request.POST.get('startHolidayEdit')
        endHolidayE = request.POST.get('endHolidayEdit')
        new_startHoliday=dateutil.parser.parse(startHolidayE, dayfirst = True,ignoretz=True)
        new_endHoliday=dateutil.parser.parse(endHolidayE, dayfirst = True,ignoretz=True)
        if new_startHoliday>=new_endHoliday:
            messages.warning(request, 'αρχή ημερομηνίας μεγαλύτερη-ίση τελικής ημερομηνίας')
            return redirect('staffHolidays')
        if Staff_holidays.objects.filter(staff_card=userForHoliday):#check for holiday that already overrides user holiday
            for item in Staff_holidays.objects.filter(staff_card=userForHoliday).exclude(id=idStaffHol):
                if (item.date_from + timedelta(hours=3))<=pytz.utc.localize(new_startHoliday) and pytz.utc.localize(new_startHoliday)<=(item.date_to + timedelta(hours=3)) or (item.date_from + timedelta(hours=3))<=pytz.utc.localize(new_endHoliday) and pytz.utc.localize(new_endHoliday)<=(item.date_to + timedelta(hours=3)):
                    messages.warning(request, 'χρήστης έχει άδεια που καλύπτει αυτην την άδεια')
                    return redirect('staffHolidays')         
        getUser=Users.objects.get(device_card_number=int(userForHoliday))
        old=Staff_holidays.objects.get(id=idStaffHol)
        sh=Staff_holidays.objects.filter(id=idStaffHol).update(
        date_from=new_startHoliday,
        date_to=new_endHoliday,
        description=desc_holi_staff
        )
        eventLogger(request,info="Χρήστης άλλαξε"+str(old)+" άδεια με τιμές: "+str(sh))
        messages.success(request, 'άδεια χρήστη ανανεώθηκε')
        return redirect('staffHolidays')


@admin_required        
@login_required()
def staffHolidaysDelete(request):
    if request.method == "POST" :
        staffHolidaysID = request.POST.get('id_staffHolidays')
        sh=Staff_holidays.objects.get(id=staffHolidaysID)
        if sh:
            sh.delete()
            messages.success(request, 'άδεια χρήστη διαγράφηκε')
            eventLogger(request,info="Χρήστης διέγραψε μία άδεια με τιμές: "+str(sh))
            return redirect('staffHolidays')
        else:
            messages.error(request, 'άδεια χρήστη δεν βρέθηκε')
            return redirect('staffHolidays')
            
       
saveSearch=[]
summaryDaysW=[]
summaryDepW=[]
myStartDateG=''
myEndDateG=''
depW=''
signatureW=''  
@login_required()
@admin_required 
def wrariaProsopikou(request):
    global saveSearch
    global myStartDateG 
    global myEndDateG
    global summaryDaysW
    global summaryDepW
    global contextPrintWrario
    global depW
    global signatureW
    if request.method == "GET" :
        if not saveSearch:
            saveSearch=''
        dep_list=Departments.objects.order_by('id')
        paginator = Paginator(saveSearch,8)
        page = request.GET.get('page', 1)
        try:
            saveSearchPagi = paginator.page(page)
        except PageNotAnInteger:
            saveSearchPagi = paginator.page(1)
        except EmptyPage:
            saveSearchPagi = paginator.page(paginator.num_pages)
        sumSignature=Signatures.objects.order_by('id')
        #get all input values for print
        eventLogger(request,info="Χρήστης μπήκε στα π/ε ωράρια προσωπικού")
        return render(request, 'wrariaProsopikou.html', {"Departments":dep_list,"WrariaStaff":saveSearchPagi,'signatures':sumSignature,'dep':depW})
    else:
        url=Industry.objects.first()
        dep_list=Departments.objects.order_by('id')
        queryWraria= {'date':"",'user_card':"",'last_name':"",'first_name':"",'wrario':"",'department':"",'relationType':""}
        signatureW=request.POST.get('signatures')
        summaryWraria=[]
        sumChild=[]
        summaryDepW=[]
        summaryDaysW=[]
        queryDay={'day':""}
        queryDep={'DepName':"",'DepParent':"",'DepID':""}
        dep_id = request.POST.get('dep_id')
        depW=Departments.objects.get(id=dep_id).department_name
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        if startDate=='':
            startDate=str(date.today())
        if endDate=='':
            endDate=str(date.today())
        if Departments.objects.get(id=dep_id).parent_id==0:#papous
            staff_dep_info_list=Staff_department_info.objects.all()
            for d in dep_list:#collect all
                sumChild.append(d.id)
        elif Departments.objects.get(id=dep_id).parent_id==Departments.objects.get(id=dep_id).industry_id:#mpampas
            sumChild.append(dep_id) # collect mpampas and childs
            for d in dep_list:
                if int(d.parent_id)==int(dep_id):
                    sumChild.append(d.id)  #child id
            staff_dep_info_list=Staff_department_info.objects.filter(department_id__in=sumChild)
        else:# is a child
            staff_dep_info_list=Staff_department_info.objects.filter(department_id=dep_id)
            sumChild.append(dep_id)
        for item in sumChild:# pass deps to summarydeps
            queryDep['DepName']=Departments.objects.get(id=item).department_name
            queryDep['DepParent']=Departments.objects.get(id=item).parent_id
            queryDep['DepID']=Departments.objects.get(id=item).id
            summaryDepW.append(queryDep.copy())
            queryDep.clear() 
        myStartDate = datetime.strptime(startDate, '%Y-%m-%d').strftime('%d/%m/%Y')
        myStartDateG=myStartDate
        myEndDate = datetime.strptime(endDate, '%Y-%m-%d').strftime('%d/%m/%Y')
        myEndDateG=myEndDate
        d2=datetime.strptime(myEndDate, '%d/%m/%Y').date()
        d1=datetime.strptime(myStartDate, '%d/%m/%Y').date()
        if d1>d2 :#check date,start<end
            messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
            return redirect('wrariaProsopikou')
        for i in range((d2 - d1).days + 1):#check every day in that range
            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
            queryDay['day']=(d1 + timedelta(days=i)).strftime('%d/%m/%Y')
            summaryDaysW.append(queryDay.copy())
            queryDay.clear()
            for staff in staff_dep_info_list:
                if staff.apply_from<=(d1 + timedelta(days=i)) and staff.apply_to>=(d1 + timedelta(days=i)):
                    queryWraria['date']=(d1 + timedelta(days=i)).strftime('%d/%m/%Y')
                    queryWraria['user_card']=Users.objects.get(device_card_number=staff.staff_card).device_card_number
                    queryWraria['last_name']=Users.objects.get(device_card_number=staff.staff_card).last_name
                    queryWraria['first_name']=Users.objects.get(device_card_number=staff.staff_card).first_name
                    queryWraria['department']=Departments.objects.get(id=staff.department_id).department_name
                    queryWraria['relationType']=Users.objects.get(device_card_number=staff.staff_card).relation_type
                    if not Users.objects.get(device_card_number=staff.staff_card).relation_type:
                        queryWraria['relationType']='----'
                    if staff.spasto:
                        wrario=str(staff.start_of_work)+" "+str(staff.end_of_work)+","+str(staff.start_of_work2)+" "+str(staff.end_of_work2)
                    else:
                        wrario=str(staff.start_of_work)+" "+str(staff.end_of_work)
                               
                    if (d1 + timedelta(days=i)).weekday()==0:#monday
                        if staff.Monday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"
                    if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                        if staff.Tuesday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"
                    if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                        if staff.Wednesday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"
                    if (d1 + timedelta(days=i)).weekday()==3:#thursday
                        if staff.Thursday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"
                    if (d1 + timedelta(days=i)).weekday()==4:#Friday
                        if staff.Friday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"
                    if (d1 + timedelta(days=i)).weekday()==5:#saturday
                        if staff.Saturday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"
                    if (d1 + timedelta(days=i)).weekday()==6:#sunday
                        if staff.Sunday:
                            queryWraria['wrario']=wrario
                        else:
                            queryWraria['wrario']="Δεν εργάζεται"      
                    summaryWraria.append(queryWraria.copy())
                    queryWraria.clear()             
        #print(summaryWraria)
        saveSearch=summaryWraria
        print(sumChild)
        print(summaryDepW)
        eventLogger(request,info="Χρήστης πάτησε αναζήτιση στη π/ε ωράρια προσωπικού")
        contextPrintWrario = {'WrariaStaff': saveSearch,'departments':dep_list,'date1':myStartDateG,'date2':myEndDateG,'SumDays':summaryDaysW,'signature':signatureW,'url':url,'SumDeps':summaryDepW,'dep':depW}
        return redirect('wrariaProsopikou') 
        #return render(request, 'wrariaProsopikou.html', {"Departments":dep_list,"WrariaStaff":saveSearch})
        
@admin_required            
@login_required()
def membersTeam(request):
    if request.method == "GET" :
        if Members_team.objects.order_by('id'):
            myMembersTeam = Members_team.objects.all()
        else:
            myMembersTeam=''
        eventLogger(request,info="Χρήστης μπήκε στο μέλη ομάδας")
        return render(request, 'MembersTeam.html', {"MembersTeam":myMembersTeam})
 
@admin_required            
@login_required()
def relationType(request):
    if request.method == "GET" :
        if Relation_types.objects.order_by('id'):
            myRelationType = Relation_types.objects.all()
        else:
            myRelationType=''
        eventLogger(request,info="Χρήστης μπήκε στη σχέση εργασίας")
        return render(request, 'RelationTypes.html', {"RelationTypes":myRelationType})
    else:
        myRelationType = request.POST.get('name_RelationType').strip()
        re=Relation_types(relation_type_name=myRelationType)
        re.save()
        messages.success(request, 'σχέση εργασίας προστέθηκε')
        eventLogger(request,info="Χρήστης πρόσθεσε μία σχέση εργασίας με τιμές: "+str(re))
        return redirect('relationType')
        
@login_required()
def relationTypeDelete(request):
    if request.method == "POST" :
        RelationTypeID = request.POST.get('id_relationType')
        re=Relation_types.objects.get(id=RelationTypeID)
        if re :
            re.delete()
            eventLogger(request,info="Χρήστης διέγραψε μία σχέση εργασίας με τιμές: "+str(re))
            messages.success(request, 'σχέση εργασίας διαγράφηκε')
            return redirect('relationType')
        else:
            messages.error(request, 'σχέση εργασίας δεν βρέθηκε')
            return redirect('relationType')

@admin_required            
@login_required()
def role(request):
    if request.method == "GET" :
        if Roles.objects.order_by('id'):
            myRole = Roles.objects.all()
        else:
            myRole=''
        eventLogger(request,info="Χρήστης μπήκε στους ρόλους")
        return render(request, 'Roles.html', {"Roles":myRole})
    else:
        myRole = request.POST.get('name_role')
        r=Roles(role_name=myRole)
        r.save()
        eventLogger(request,info="Χρήστης πρόσθεσε ρόλο με τιμές: "+str(r))
        messages.success(request, 'ρόλος προστέθηκε')
        return redirect('role')
   
@admin_required        
@login_required()
def roleDelete(request):
    if request.method == "POST" :
        roleID = request.POST.get('id_role')
        r=Roles.objects.get(id=roleID)
        if r :
            r.delete()
            eventLogger(request,info="Χρήστης διέγραψε ρόλο με τιμές: "+str(r))
            messages.success(request, 'ρόλος διαγράφηκε')
            return redirect('role')
        else:
            messages.error(request, 'ρόλος δεν βρέθηκε')
            return redirect('role')
        
            
@admin_required     
@login_required()
def Signature(request):
    if request.method == "GET" :
        if Signatures.objects.order_by('id'):
            mySignatures = Signatures.objects.all()
        else:
            mySignatures=''
        eventLogger(request,info="Χρήστης μπήκε στις υπογραφές")
        return render(request, 'Signatures.html', {"Signatures":mySignatures})
    else:
        mySignature = request.POST.get('name_sign')
        s=Signatures(signature_name=mySignature)
        s.save()
        eventLogger(request,info="Χρήστης πρόσθεσε υπογραφή με τιμές: "+str(s))
        messages.success(request, 'υπογραφή προστέθηκε')
        return redirect('Signature')
   
@admin_required        
@login_required()
def SignatureDelete(request):
    if request.method == "POST" :
        signID = request.POST.get('id_sign')
        s=Signatures.objects.get(id=signID)
        if s :
            s.delete()
            messages.success(request, 'υπογραφή διαγράφηκε')
            eventLogger(request,info="Χρήστης διέγραψε υπογραφή με τιμές: "+str(s))
            return redirect('Signature')
        else:
            messages.error(request, 'υπογραφή δεν βρέθηκε')
            return redirect('Signature')
   
@admin_required            
@login_required()
def holiday(request):
    if request.method == "GET" :
        if Holidays.objects.order_by('id'):
            myHolidays = Holidays.objects.all()
            paginator = Paginator(myHolidays, 10)
            page = request.GET.get('page', 1)
            try:
                holidays = paginator.page(page)
            except PageNotAnInteger:
                holidays = paginator.page(1)
            except EmptyPage:
                holidays = paginator.page(paginator.num_pages)
        else:
            myHolidays=''
            paginator = Paginator(myHolidays, 10)
            page = request.GET.get('page', 1)
            try:
                holidays = paginator.page(page)
            except PageNotAnInteger:
                holidays = paginator.page(1)
            except EmptyPage:
                holidays = paginator.page(paginator.num_pages)
        eventLogger(request,info="Χρήστης μπήκε στις αργίες")
        return render(request, 'holidays.html', {"Holidays":holidays})
    else:
        h_desc = request.POST.get('holi_desc')
        h_datef = request.POST.get('holi_datef')
        h_datet = request.POST.get('holi_datet')
        if parse_date(h_datef)>parse_date(h_datet):
            messages.error(request, 'αργία από μεγαλύτερη από αργία μέχρι')
            return redirect('holiday')
        h=Holidays(description=h_desc,date_from=h_datef,date_to=h_datet)
        h.save()
        eventLogger(request,info="Χρήστης πρόσθεσε αργία με τιμές: "+str(h))
        messages.success(request, 'αργία προστέθηκε')
        return redirect('holiday')
  
@admin_required        
@login_required()
def holidayDelete(request):
    if request.method == "POST" :
        holidayID = request.POST.get('id_holi')
        h=Holidays.objects.get(id=holidayID)
        if h :
            h.delete()
            eventLogger(request,info="Χρήστης διέγραψε αργία με τιμές: "+str(h))
            messages.success(request, 'αργία διαγράφηκε')
            return redirect('holiday')
        else:
            messages.error(request, 'αργία δεν βρέθηκε')
            return redirect('holiday')

@admin_required
@login_required()
def holidayCurrentYear(request):
    if request.method == "POST" :
        holidayDict={'New year':"Πρωτοχρονιά",'Epiphany':"Θεοφάνεια",'Clean Monday':"Καθαρά Δευτέρα",'Annunciation':"Η 25η Μαρτίου",'Independence Day':"Η 25η Μαρτίου",'Good Friday':"Μεγάλη Παρασκευή",'Labour Day':"Εργατική Πρωτομαγιά",'Easter Sunday':"Κυριακή του Πάσχα",'Easter Monday':"Δευτέρα του Πάσχα",'Pentecost':"Πεντηκοστή",'Whit Monday':"Αγίου Πνεύματος",'Assumption of Mary to Heaven':"Κοίμηση Θεοτόκου",'Ohi Day':"Το Όχι",'Christmas Day':"Χριστούγεννα",'Glorifying Mother of God':"Σύναξη της Θεοτόκου"}
        cal=Greece()
        currentYear = datetime.now().year
        print(cal.holidays(currentYear))
        for item in cal.holidays(currentYear):
            print(item[0])
            print(holidayDict.get(item[1]))
            try:
                h=Holidays(description=holidayDict.get(item[1]),date_from=item[0],date_to=item[0])
                h.save()
            except Exception as e:
                print("Process terminate holiday : {}".format(e))
        eventLogger(request,info="Χρήστης πάτησε προσθήκη αργιών αυτόματα για τρέχον έτος")
        return redirect('holiday')
  
@admin_required
@login_required()    
def holidayNextYear(request):
    if request.method == "POST" :
        holidayDict={'New year':"Πρωτοχρονιά",'Epiphany':"Θεοφάνεια",'Clean Monday':"Καθαρά Δευτέρα",'Annunciation':"Η 25η Μαρτίου",'Independence Day':"Η 25η Μαρτίου",'Good Friday':"Μεγάλη Παρασκευή",'Labour Day':"Εργατική Πρωτομαγιά",'Easter Sunday':"Κυριακή του Πάσχα",'Easter Monday':"Δευτέρα του Πάσχα",'Pentecost':"Πεντηκοστή",'Whit Monday':"Αγίου Πνεύματος",'Assumption of Mary to Heaven':"Κοίμηση Θεοτόκου",'Ohi Day':"Το Όχι",'Christmas Day':"Χριστούγεννα",'Glorifying Mother of God':"Σύναξη της Θεοτόκου"}
        cal=Greece()
        nextYear = (datetime.now()+relativedelta(years=+1)).year
        print(cal.holidays(nextYear))
        for item in cal.holidays(nextYear):
            print(item[0])
            print(holidayDict.get(item[1]))
            try:
                h=Holidays(description=holidayDict.get(item[1]),date_from=item[0],date_to=item[0])
                h.save()
            except Exception as e:
                print("Process terminate holiday : {}".format(e))
        eventLogger(request,info="Χρήστης πάτησε προσθήκη αργιών αυτόματα για επόμενο έτος")
        return redirect('holiday')


@admin_required        
@login_required()
def OrganizationChart(request):
    if request.method == "GET" :
        departments_list=Departments.objects.order_by('id')
        departments_listWC=Departments.objects.filter(parent_id__range=(0,1))
        queryTest= {'DepPapous':"",'DepMpampas':"",'DepChild':"",'DepID':"",'DepPID':""}
        summaryTest=[]
        for dep in departments_list: 
            if int(dep.parent_id)==0 :    #check if it is papous
                queryTest['DepPapous']=dep.department_name
                queryTest['DepID']=dep.id
                queryTest['DepPID']=dep.parent_id
                summaryTest.append(queryTest.copy())
                queryTest.clear()
            elif int(dep.parent_id)==int(dep.industry_id):  #check if it is mpampas
                queryTest['DepMpampas']=dep.department_name
                queryTest['DepID']=dep.id
                queryTest['DepPID']=dep.parent_id
                summaryTest.append(queryTest.copy())
                queryTest.clear()
                if Departments.objects.filter(parent_id=dep.id).exclude(id=dep.id):#check mpampas if has childs
                    for i in Departments.objects.filter(parent_id=dep.id).exclude(id=dep.id):
                        queryTest['DepChild']=i.department_name
                        queryTest['DepID']=i.id
                        queryTest['DepPID']=i.parent_id
                        summaryTest.append(queryTest.copy())
                        queryTest.clear()
            # else:# it is a child
            #     queryTest['DepChild']=dep.department_name
            #     queryTest['DepID']=dep.id
            #     queryTest['DepPID']=dep.parent_id
            # summaryTest.append(queryTest.copy())
            # queryTest.clear()
        departments_listDel=Departments.objects.exclude(parent_id=0)#check all except dimos-industry
        queryDel= {'DepToDel':"",'DepID':"",'DepPID':""}
        summaryDel=[]
        for dep in departments_listDel:#organize department del list
            if int(dep.parent_id)==int(dep.industry_id): #check if it is mpampas
                if Departments.objects.filter(parent_id=dep.id).exclude(id=dep.id):# check if has a child
                    pass
                else:
                    queryDel['DepToDel']=dep.department_name
                    queryDel['DepID']=dep.id
                    queryDel['DepPID']=dep.parent_id
                    summaryDel.append(queryDel.copy())
                    queryDel.clear()
            else:#is a child
                queryDel['DepToDel']=dep.department_name
                queryDel['DepID']=dep.id
                queryDel['DepPID']=dep.parent_id
                summaryDel.append(queryDel.copy())
                queryDel.clear()
        eventLogger(request,info="Χρήστης μπήκε οργανόγραμμα")
        return render(request, 'OrganizationChart.html', {"DepartmentsTest":summaryTest,'Departments':departments_list,'DepartmentsWC':departments_listWC,'DepartmentsDel':summaryDel})
    else:
        myOrgAdd = request.POST.get('orgAdd_dep')
        myOrgMpampas = request.POST.get('orgAdd_mpampas')
        lastID= Departments.objects.last().id
        if Departments.objects.filter(department_name=myOrgAdd):
            messages.error(request, 'όνομα τμήματος υπάρχει')
            return redirect('OrganizationChart')
        d=Departments(id=lastID+1,department_name=myOrgAdd,industry_id=1,parent_id=int(myOrgMpampas))
        d.save()
        eventLogger(request,info="Χρήστης πρόσθεσε τμήμα με τιμές: "+str(d))
        messages.success(request, 'τμήμα προστέθηκε')
        return redirect('OrganizationChart')

@admin_required        
@login_required()
def OrganizationChartMove(request):
    if request.method == "POST" :
        myOrgmoveF = request.POST.get('orgMoveF')
        myOrgmoveT = request.POST.get('orgMoveT')
        if Departments.objects.get(id=myOrgmoveF).parent_id==0:
            messages.error(request, 'αυτό το τμήμα δεν μπορεί να μετακινηθεί (φορέας)')
            return redirect('OrganizationChart')
        d=Departments.objects.filter(id=myOrgmoveF).update(parent_id=myOrgmoveT)
        Departments.objects.filter(id=myOrgmoveF).update(parent_id=myOrgmoveT)
        eventLogger(request,info="Χρήστης μετακίνησε τμήμα με τιμές: "+str(d))
        messages.success(request, 'τμήμα μετακινήθηκε')
        return redirect('OrganizationChart')
 
@admin_required        
@login_required()
def OrganizationChartDel(request):
    if request.method == "POST" :
        myOrgDel = request.POST.get('orgDel')
        if Departments.objects.get(id=myOrgDel).parent_id==0:
            messages.error(request, 'αυτό το τμήμα δεν μπορεί να διαγραφεί (φορέας)')
            return redirect('OrganizationChart')
        d=Departments.objects.get(id=myOrgDel).delete()
        eventLogger(request,info="Χρήστης διέγραψε τμήμα με τιμές: "+str(d))
        messages.success(request, 'τμήμα διαγράφηκε')
        return redirect('OrganizationChart')                

@admin_required            
@login_required()
def deviceSelect(request):
    if request.method == "GET" :
        if Devices.objects.all():
            myDevice = Devices.objects.all()
            paginator = Paginator(myDevice, 5)
            page = request.GET.get('page', 1)
            try:
                device = paginator.page(page)
            except PageNotAnInteger:
                device = paginator.page(1)
            except EmptyPage:
                device = paginator.page(paginator.num_pages)
        else:
            device=''
        eventLogger(request,info="Χρήστης μπήκε συσκευές")
        return render(request, 'deviceSelect.html', {"myDevice":device})
  
@admin_required        
@login_required()
def deviceAdd(request):
    if request.method == "POST" :
        myIP = request.POST.get('IP')
        myNameDevice = request.POST.get('nameDevice')
        port=request.POST.get('port')
        myRegex=re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",myIP)
        if myRegex :
            d=Devices(
            device_location=myNameDevice,
            device_ip=myIP,
            device_port=port
             )
            d.save()
            eventLogger(request,info="Χρήστης πρόσθεσε συσκευή με τιμές: "+str(d))
            messages.success(request, 'συσκευή προστέθηκε')
            return redirect('deviceSelect')
        else:
            messages.error(request, 'δεν είναι σωστό φορματ τις IP')
            return redirect('deviceSelect')

@admin_required            
@login_required()
def deviceDelete(request):
    if request.method == "POST" :
        myID = request.POST.get('idDevice')
        d=Devices.objects.get(id=myID)
        if d :
            d.delete()
            eventLogger(request,info="Χρήστης διέγραψε συσκευή με τιμές: "+str(d))
            messages.success(request, 'συσκευή διαγράφηκε')
            return redirect('deviceSelect')
        else:
            messages.error(request, 'δεν βρέθηκε συσκευή')
            return redirect('deviceSelect')
        
        
@admin_required            
@login_required()
def deviceClear(request):
    global fullatendances_DeviceData 
    global usersDv
    if request.method == "POST" :
        myID = request.POST.get('idDevice')
        d=Devices.objects.get(id=myID)
        if d :
            fullatendances_DeviceData.clear()
            usersDv.clear()
            SynchronizeAttendancesClear(request)#save the attendances
            conn = None
            # create ZK instance
            zk = ZK(d.device_ip, port=d.device_port, timeout=5,
                    password=0, force_udp=False, ommit_ping=False)
            try:
                # connect to device
                conn = zk.connect()
                # disable device, this method ensures no activity on the device while the process is run
                conn.disable_device()
                conn.clear_attendance()#delete all attendances of the device
                # re-enable device after all commands already executed
                conn.enable_device()
                conn.disconnect()
                eventLogger(request,info="Χρήστης διέγραψε παρουσίες συσκευής " +str(d.device_location))
                return redirect('deviceSelect')
            except Exception as e:
                print("Process terminate no connection : {}".format(e))
        else:
            messages.error(request, 'δεν βρέθηκε συσκευή')
            return redirect('deviceSelect')


def setTime(request,clockIP,clockPort):
    conn = None
    # create ZK instance
    zk = ZK(clockIP, port=clockPort, timeout=5,
            password=0, force_udp=False, ommit_ping=False)
    try:
        # connect to device
        conn = zk.connect()
        # disable device, this method ensures no activity on the device while the process is run
        conn.disable_device()
        newtime = datetime.today()
        conn.set_time(newtime)
        # re-enable device after all commands already executed
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        print("Process terminate : {}".format(e))
        
@login_required()        
def CheckDevices(request):
    clocks=Devices.objects.all()
    for clock in clocks:
        #conn = None
        # create ZK instance
        zk = ZK(clock.device_ip, port=clock.device_port, timeout=5, password=0,
                force_udp=False, ommit_ping=False)
        try:
            #thevariable
            zk.connect()
        except Exception as e:
            print("not connected: "+clock.device_location)
            messages.error(request,clock.device_location+' συσκευή δεν συνδέθηκε')
        else:
            print("connected: "+clock.device_location)
            setTime(request,clock.device_ip,clock.device_port)
            messages.success(request,clock.device_location+' συσκευή συνδέθηκε')
    eventLogger(request,info="Χρήστης πάτησε έλεγχος συσκευών")
    return redirect('deviceSelect')


@login_required()            
def SynchronizeAttendancesClear(request):
    logger.error("sychronize attendances clear is running")
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
                temp_date = parse_datetime(attendancesplit[3] + " " + attendancesplit[4])
                try:
                    Staff_attendance.objects.create(
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
            messages.success(request,clock.device_location+' έδωσε παρουσίες επιτυχώς')
        except Exception as e:
            print("Process terminate3 : {}".format(e))
            messages.error(request,clock.device_location+' συσκευή δεν συνδέθηκε')
    eventLogger(request,info="Χρήστης πάτησε συγχρονισμό για καθαρισμό παρουσιών")            
    #return clock.device_location+' συσκευή δεν συνδέθηκε'



@login_required()            
def SynchronizeAttendances(request):
    if request.method == "POST" :
        logger.error("sychronize attendances is running")
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
                    temp_date = parse_datetime(attendancesplit[3] + " " + attendancesplit[4])
                    try:
                        Staff_attendance.objects.create(
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
                messages.success(request,clock.device_location+' έδωσε παρουσίες επιτυχώς')
            except Exception as e:
                print("Process terminate3 : {}".format(e))
                messages.error(request,clock.device_location+' συσκευή δεν συνδέθηκε')
        createAttendancesRearranged(request)#fill the reanrranged table
        eventLogger(request,info="Χρήστης πάτησε συγχρονισμό παρουσιών")            
        return redirect('welcome')

@login_required()        
def SynchronizeAttendancesOfToday(request):
    if request.method == "POST" or request.method=="GET" :
        logger.error("sychronize attendances of today is running")
        today=str(date.today())
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
                    if attendancesplit[3]==today:
                        temp_date = parse_datetime(attendancesplit[3] + " " + attendancesplit[4])
                        try:
                            Staff_attendance.objects.create(
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
                messages.success(request,clock.device_location+' έδωσε παρουσίες επιτυχώς για σήμερα')
            except Exception as e:
                print("Process terminate2 : {}".format(e))
                messages.error(request,clock.device_location+' συσκευή δεν συνδέθηκε')            
        return "synchronize Attendances Of Today success"


fullatendances_DeviceData=[] 
usersDv=[]
@admin_required
@login_required()
def deviceData(request): # use of global attributes, because of  if statements, if they fail the attributes will be null
    global clock
    global conn
    global users
    global fullatendances_DeviceData
    global ver
    global face_ver
    global plat
    global firm_v
    global pin_wid
    global ffo
    global ser_num
    global dev_name
    global get_time
    global myIP_DeviceData
    global myNameDevice_DeviceData
    if request.method == "POST" :
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        myIP = request.POST.get('IP')
        myNameDevice = request.POST.get('nameDevice')
        if myIP is not None and myNameDevice is not None:
            myIP_DeviceData=myIP
            myNameDevice_DeviceData=myNameDevice
        clock = myIP_DeviceData
        port=Devices.objects.get(device_ip=clock).device_port
        conn = None
        # create ZK instance
        zk = ZK(clock, port=port, timeout=5, password=0,
                force_udp=False, ommit_ping=False)
        try:
            # connect to device
            conn = zk.connect()
            # disable device, this method ensures no activity on the device while the process is run
            conn.disable_device()
            # another commands will be here!
           # conn.set_user(uid=141, name='Egw 2', privilege='user', password='12345678', group_id='', user_id='821', card=0)
            # Example: Get All Users
            users = conn.get_users()
            global usersDv
            usersDv=users
            zktime = conn.get_time()
            ver = conn.get_fp_version()
            face_ver = conn.get_face_version()
            plat = conn.get_platform()
            firm_v = conn.get_firmware_version()
            net_par = conn.get_network_params()
            get_mac = conn.get_mac()
            pin_wid = conn.get_pin_width()
            ffo = conn.get_face_fun_on()
            ser_num = conn.get_serialnumber()
            dev_name = conn.get_device_name()
            get_time = conn.get_time()

            for user in users:
                privilege = 'User'
                print("-----------------")
                #print(user)
                #print(user.card)
                if user.privilege == const.USER_ADMIN:
                    privilege = 'Admin'
                print('+ UID #{}'.format(user.uid))#user normal id
                print('  Name       : {}'.format(user.name))
                print('  Privilege  : {}'.format(privilege))
                print('  Password   : {}'.format(user.password))
                print('  Group ID   : {}'.format(user.group_id))
                print('  User  ID   : {}'.format(user.user_id))#card id
                print('  User  card   : {}'.format(user.card))#card number

            attendances = conn.get_attendance()
            attendances = conn.get_attendance()
            fullatendancesSum = []
            for attendance in attendances:
                # print(attendance)
                attendancesplit = str(attendance).split()
                print("-----------------")
                print(attendance)  
                for user in users:
                    if(user.user_id == attendancesplit[1]):
                        
                        #print('{}'.format(user.name))
                        break
                print(attendancesplit[0])
                print(attendancesplit[1])
                print(attendancesplit[2])
                print(attendancesplit[3])
                print(attendancesplit[4])
                #print(attendance)
                #temp_date = parse_datetime(attendancesplit[3] + " " + attendancesplit[4]).strftime('%A %d %B %Y--%H:%M:%S')
                temp_date = parse_datetime(attendancesplit[3] + " " + attendancesplit[4]).strftime('%d/%m/%Y--%H:%M:%S')
                fullatendancesSum.append(
                    user.name+" (card id):"+str(user.user_id)+",(card number): "+str(user.card)+ " , Ημερομηνία: " + temp_date)
            # Test Voice: Say Thank You
            # conn.test_voice()
            # re-enable device after all commands already executed
            print(fullatendancesSum)
            conn.enable_device()
            conn.disconnect()
        except Exception as e:
            print("Process terminate3 : {}".format(e))
            messages.error(request,myNameDevice_DeviceData+'  συσκευή δεν συνδέθηκε')
            return redirect('deviceSelect')
                
        if fullatendancesSum:
            fullatendances_DeviceData=fullatendancesSum
        #attendance_list = Staff_attendance.objects.filter(device_name=myNameDevice_DeviceData).order_by('attendance_date')
        paginator = Paginator(fullatendances_DeviceData, 12)
        page = request.GET.get('pageA', 1)
        try:
            fullatendances = paginator.page(page)
        except PageNotAnInteger:
            fullatendances = paginator.page(1)
        except EmptyPage:
            fullatendances = paginator.page(paginator.num_pages)
        
        #myUsers_list = Users.objects.all().order_by('id')
        myUsers_list=users#device users
        paginator2 = Paginator(myUsers_list, 12)
        page = request.GET.get('pageU', 1)
        try:
            myUsers = paginator2.page(page)
        except PageNotAnInteger:
            myUsers = paginator2.page(1)
        except EmptyPage:
            myUsers = paginator2.page(paginator2.num_pages)
            
        context = {'version': ver, 'os_version': face_ver, 'platform': plat, 'firm_version': firm_v, 'pin_width': pin_wid, 'face_function': ffo,

                   'serial_num': ser_num, 'dev_name': dev_name, 'get_time': get_time, 'fullatendances': fullatendances, 'nameDevice': myNameDevice_DeviceData,'myUsers':myUsers}

        eventLogger(request,info="Χρήστης μπήκε στην επεξεργασία συσκευής")
        return render(request, 'deviceData.html', context)   
    else:
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        paginator = Paginator(fullatendances_DeviceData, 12)
        page = request.GET.get('pageA', 1)
        try:
            fullatendances = paginator.page(page)
        except PageNotAnInteger:
            fullatendances = paginator.page(1)
        except EmptyPage:
            fullatendances = paginator.page(paginator.num_pages)
            
        myUsers_list = users#device users
        paginator2 = Paginator(myUsers_list, 12)
        page = request.GET.get('pageU', 1)
        try:
            myUsers = paginator2.page(page)
        except PageNotAnInteger:
            myUsers = paginator2.page(1)
        except EmptyPage:
            myUsers = paginator2.page(paginator2.num_pages)
           
        context = {'version': ver, 'os_version': face_ver, 'platform': plat, 'firm_version': firm_v, 'pin_width': pin_wid, 'face_function': ffo,
                   'serial_num': ser_num, 'dev_name': dev_name, 'get_time': get_time, 'fullatendances': fullatendances, 'nameDevice': myNameDevice_DeviceData,'myUsers':myUsers}
   
        return render(request, 'deviceData.html', context)
 
depInfo=[]     
@login_required()
@admin_required
def departments(request):
    if Industry.objects.first():
        general_work_rangeF=Industry.objects.first().general_work_range_from
        general_work_rangeT=Industry.objects.first().general_work_range_to
    else:
        general_work_rangeS=''
        general_work_rangeE=''
    myUsers_list = Users.objects.all().order_by('id')
    departments_list=Departments.objects.all().order_by('id')
    staff_dep_list=Staff_department_info.objects.all()
    today=str(date.today())
    rolesDb=Roles.objects.all()
    queryDict= {'department': "",'last_name': "", 'first_name': "", 'role': "", 'staff_card': "",'DepID':"",'DepPID':"",'staff_dep_id':"",'fathers_name':""}  
    queryTest= {'DepPapous':"",'DepMpampas':"",'DepChild':"",'DepID':"",'DepPID':""}
    summaryTest=[]
    for dep in departments_list: 
        if int(dep.parent_id)==0 :    #check if it is papous
            queryTest['DepPapous']=dep.department_name
            queryTest['DepID']=dep.id
            queryTest['DepPID']=dep.parent_id
            summaryTest.append(queryTest.copy())
            queryTest.clear()
        elif int(dep.parent_id)==int(dep.industry_id):  #check if it is mpampas
            queryTest['DepMpampas']=dep.department_name
            queryTest['DepID']=dep.id
            queryTest['DepPID']=dep.parent_id
            summaryTest.append(queryTest.copy())
            queryTest.clear()
            if Departments.objects.filter(parent_id=dep.id).exclude(id=dep.id):#check mpampas if has childs
                for i in Departments.objects.filter(parent_id=dep.id).exclude(id=dep.id):
                    queryTest['DepChild']=i.department_name
                    queryTest['DepID']=i.id
                    queryTest['DepPID']=i.parent_id
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
    summaryQueryDict=[]
    for d in departments_list:
        queryDict['department']=d.department_name
        for staff in staff_dep_list:
            if  staff.department_id == d.id:
                for u in myUsers_list:
                    if staff.staff_card == u.device_card_number:
                        queryDict['last_name']=u.last_name
                        queryDict['first_name']=u.first_name
                        queryDict['fathers_name']=u.fathers_name
                        queryDict['role']=staff.role
                        queryDict['staff_card']=staff.staff_card
                        queryDict['DepID']=d.id
                        queryDict['DepPID']=d.parent_id
                        queryDict['staff_dep_id']=staff.id#staff_dep_info id
                        summaryQueryDict.append(queryDict.copy())
                        queryDict.clear()

    print(summaryQueryDict)
    global depInfo
    depInfo=summaryQueryDict
    eventLogger(request,info="Χρήστης μπήκε τμήματα και ωράρια προσωπικού")
    return render(request, 'departments.html',{'users':myUsers_list,'departments':departments_list,'theList':summaryQueryDict,'Test':summaryTest,'myDate':today,'generalWRF':general_work_rangeF,'generalWRT':general_work_rangeT,'Roles':rolesDb})
    
@login_required()
@admin_required
def staffAdd(request):
    if request.method == "POST" :
        depID = request.POST.get('dep_id')
        user_card_number = request.POST.get('user_device_card_number')
        myRole = request.POST.get('role')
        
        applyF = request.POST.get('applyF')
        if applyF=='':
            applyF=str(date.today())
        applyT = request.POST.get('applyT')
        if applyT=='':
            applyT=str(date.today()+timedelta(days=20000))#50 years
        startW = request.POST.get('startW')
        endW = request.POST.get('endW')
        
        if request.POST.get('monday'):
            monday = request.POST.get('monday')
        else:
            monday=0
        
        if request.POST.get('tuesday'):
            tuesday = request.POST.get('tuesday')
        else:
            tuesday=0
        
        if request.POST.get('wednesday'):
            wednesday = request.POST.get('wednesday')
        else:
            wednesday=0
        
        if request.POST.get('thursday'):
            thursday = request.POST.get('thursday')
        else:
            thursday=0
        
        if request.POST.get('friday'):
            friday = request.POST.get('friday')
        else:
            friday=0
        
        if request.POST.get('saturday'):
            saturday = request.POST.get('saturday')
        else:
            saturday=0
        
        if request.POST.get('sunday'):
            sunday = request.POST.get('sunday')
        else:
            sunday=0
        
        if request.POST.get('spasto'):
            spasto = request.POST.get('spasto')
            startW2 = request.POST.get('startW2')
            endW2 = request.POST.get('endW2')
        else:
            spasto=0
            startW2=None
            endW2=None 
        staff_current_user=Staff_department_info.objects.filter(staff_card=user_card_number)   
        staff_dep_current_user=Staff_department_info.objects.filter(department_id=int(depID),staff_card=user_card_number)
        count=Staff_department_info.objects.filter(staff_card=user_card_number).count()#records of this user card
            #check user card in specific dep, check records found(max 2),check spasto
        for item in staff_current_user: 
            if  item.apply_from<=parse_date(applyF) and parse_date(applyF)<=item.apply_to or item.apply_from<=parse_date(applyT) and  parse_date(applyT)<=item.apply_to:
                messages.warning(request, 'χρήστης ανήκει ήδη σε 1 τμήμα, μέγιστο είναι 1 σε μοναδικό διάστημα')
                return redirect('departments')  
        if staff_dep_current_user:
            messages.warning(request, 'χρήστης ανήκει ήδη σε αυτό το τμήμα')
            return redirect('departments')
        if parse_date(applyF)>=parse_date(applyT):
            messages.warning(request, '(ισχύει από) είναι μεγαλύτερο ή ίσο απο (ισχύει εώς)')
            return redirect('departments')
        if parse_time(startW)>=parse_time(endW):
            messages.warning(request, '(έναρξη) είναι μεγαλύτερη ή ίση  απο (λήξη εώς)')
            return redirect('departments')
        if startW2 is not None and endW2 is not None:
            if parse_time(startW2)>=parse_time(endW2):
                messages.warning(request, '(έναρξη 2) είναι μεγαλύτερη ή ίση απο (λήξη εώς 2)')
                return redirect('departments')
            if parse_time(startW)>=parse_time(startW2):
                messages.warning(request, '(έναρξη) είναι μεγαλύτερη ή ίση απο (έναρξη 2)')
                return redirect('departments')
            if parse_time(endW)>=parse_time(endW2):
                messages.warning(request, '(λήξη εώς) είναι μεγαλύτερη ή ίση απο (λήξη εώς 2)')
                return redirect('departments')
            if parse_time(endW)>parse_time(startW2):
                messages.warning(request, '(λήξη εώς) είναι μεγαλύτερη απο (έναρξη εώς 2)')
                return redirect('departments')
        idforTable=int(Staff_department_info.objects.last().id)+1
        mySD=Staff_department_info(
        id=idforTable,
        department_id =int(depID),
        staff_card=user_card_number,
        role = Roles.objects.get(id=myRole).role_name,
        apply_from = parse_date(applyF),
        apply_to = parse_date(applyT),
        start_of_work = startW,
        end_of_work = endW,
        spasto=spasto,
        start_of_work2 = startW2,
        end_of_work2 = endW2,
        Monday=monday,
        Tuesday=tuesday,
        Wednesday=wednesday,
        Thursday=thursday,
        Friday=friday,
        Saturday=saturday,
        Sunday=sunday
        )
        mySD.save()
        eventLogger(request,info="Χρήστης πρόσθεσε χρήστη σε τμήμα με τιμές: "+str(mySD))
        messages.success(request, 'χρήστης προστέθηκε σε τμήμα')
    return redirect('departments')

@login_required()
@admin_required
def staffDelete(request):
    if request.method == "POST" :
        stID = request.POST.get('staff_dep_id')
        sd=Staff_department_info.objects.get(id=int(stID))
        sd.delete()
        eventLogger(request,info="Χρήστης  χρήστη σε τμήμα με τιμές: "+str(sd))
        messages.info(request, 'χρήστης σε τμήμα διαγράφικε')
    return redirect('departments')
 
@login_required()
@admin_required
def staffGet(request,id): #return the object as string from ajax get request
    staffD=Staff_department_info.objects.get(id=id)
    queryDict= {'department': "",'dep_id':"",'last_name': "",'user_card_number':'', 'first_name': "",'fathers_name':"", 'email': "",'role':'','startW':"",'endW':"",'applyF':"",'applyT':"",'monday':"",'tuesday':"",'wednesday':"",'thursday':"",'friday':"",'saturday':"",'sunday':"",'work_date_id':"",'spasto':"",'startW2':"",'endW2':"",'applyF_f':"",'applyT_f':''}
    getDepName=Departments.objects.get(id=staffD.department_id).department_name
    queryDict['department']=getDepName
    getRole=staffD.role
    queryDict['role']=getRole
    userInfo=Users.objects.get(device_card_number=staffD.staff_card)
    queryDict['last_name']=userInfo.last_name
    queryDict['first_name']=userInfo.first_name
    queryDict['fathers_name']=userInfo.fathers_name
    queryDict['email']=userInfo.email
    queryDict['dep_id']=staffD.department_id
    queryDict['user_card_number']=staffD.staff_card
    
    getWorkDateID=Staff_department_info.objects.get(department_id=staffD.department_id,staff_card=staffD.staff_card).id
    queryDict['work_date_id']=getWorkDateID
    
    queryDict['applyF']=Staff_department_info.objects.get(id=int(getWorkDateID)).apply_from.strftime("%Y-%m-%d")
    queryDict['applyT']=Staff_department_info.objects.get(id=int(getWorkDateID)).apply_to.strftime("%Y-%m-%d")
    queryDict['applyF_f']=Staff_department_info.objects.get(id=int(getWorkDateID)).apply_from.strftime("%d/%m/%Y")
    queryDict['applyT_f']=Staff_department_info.objects.get(id=int(getWorkDateID)).apply_to.strftime("%d/%m/%Y")
    
    queryDict['startW']=Staff_department_info.objects.get(id=int(getWorkDateID)).start_of_work.strftime("%H:%M")
    queryDict['endW']=Staff_department_info.objects.get(id=int(getWorkDateID)).end_of_work.strftime("%H:%M")
    
    queryDict['spasto']=Staff_department_info.objects.get(id=int(getWorkDateID)).spasto
    queryDict['startW2']=Staff_department_info.objects.get(id=int(getWorkDateID)).start_of_work2
    queryDict['endW2']=Staff_department_info.objects.get(id=int(getWorkDateID)).end_of_work2
    
    queryDict['monday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Monday
    queryDict['tuesday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Tuesday
    queryDict['wednesday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Wednesday
    queryDict['thursday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Thursday
    queryDict['friday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Friday
    queryDict['saturday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Saturday
    queryDict['sunday']=Staff_department_info.objects.get(id=int(getWorkDateID)).Sunday
    
    logger.error(queryDict)
    return JsonResponse(queryDict)
    
    
@login_required()
@admin_required
def staffEdit(request):
    if request.method == "POST" :
        depID = request.POST.get('dep_id')
        user_card_number = request.POST.get('user_card_number')
        myRole = request.POST.get('role')
        staffD_id=request.POST.get('staff_dep_id')

        applyF = request.POST.get('applyF')
        applyT = request.POST.get('applyT')
        
        startW = request.POST.get('startW')
        endW = request.POST.get('endW')
        
        if request.POST.get('monday'):
            monday = request.POST.get('monday')
        else:
            monday=0
        
        if request.POST.get('tuesday'):
            tuesday = request.POST.get('tuesday')
        else:
            tuesday=0
        
        if request.POST.get('wednesday'):
            wednesday = request.POST.get('wednesday')
        else:
            wednesday=0
        
        if request.POST.get('thursday'):
            thursday = request.POST.get('thursday')
        else:
            thursday=0
        
        if request.POST.get('friday'):
            friday = request.POST.get('friday')
        else:
            friday=0
        
        if request.POST.get('saturday'):
            saturday = request.POST.get('saturday')
        else:
            saturday=0
        
        if request.POST.get('sunday'):
            sunday = request.POST.get('sunday')
        else:
            sunday=0
            
        if request.POST.get('spasto'):
            spasto = request.POST.get('spasto')
            startW2 = request.POST.get('startW2')
            endW2 = request.POST.get('endW2')
        else:
            spasto=0
            startW2=None
            endW2=None  
        count=Staff_department_info.objects.filter(staff_card=user_card_number).count()
        staff_dep_list=Staff_department_info.objects.filter(staff_card=user_card_number).exclude(id=staffD_id)
        for item in staff_dep_list:
            #check user card in specific dep, check records found(max 2),check spasto
            staff=Staff_department_info.objects.filter(staff_card=item.staff_card).first()
            if item.apply_from<=parse_date(applyF) and parse_date(applyF)<=item.apply_to or item.apply_from<=parse_date(applyT) and  parse_date(applyT)<=item.apply_to:
                messages.warning(request, 'χρήστης ανήκει ήδη σε 1 τμήμα, μέγιστο είναι 1 σε μοναδικό διάστημα')
                return redirect('departments')   
            if item.department_id==int(depID) and item.staff_card==user_card_number:
                messages.warning(request, 'χρήστης ανήκει ήδη σε αυτό το τμήμα')
                return redirect('departments')
            if Staff_department_info.objects.filter(staff_card=item.staff_card).count()>1 and item.spasto:
                messages.warning(request, 'χρήστης έχει σπαστό ωράριο, δεν μπορεί να ανήκει σε δεύτερο τμήμα')
                return redirect('departments')
            if parse_date(applyF)>=parse_date(applyT):
                messages.warning(request, '(ισχύει από) είναι μεγαλύτερο ή ίσο απο (ισχύει εώς)')
                return redirect('departments')
            if parse_time(startW)>=parse_time(endW):
                messages.warning(request, '(έναρξη) είναι μεγαλύτερη ή ίση απο (λήξη εώς)')
                return redirect('departments')
            
            if startW2 is not None and endW2 is not None:
                if parse_time(startW2)>=parse_time(endW2):
                    messages.warning(request, '(έναρξη 2) είναι μεγαλύτερη ή ίση απο (λήξη εώς 2)')
                    return redirect('departments')
                if parse_time(startW)>=parse_time(startW2):
                    messages.warning(request, '(έναρξη) είναι μεγαλύτερη ή ίση απο (έναρξη 2)')
                    return redirect('departments')
                if parse_time(endW)>=parse_time(endW2):
                    messages.warning(request, '(λήξη εώς) είναι μεγαλύτερη ή ίση απο (λήξη εώς 2)')
                    return redirect('departments')
                if parse_time(endW)>parse_time(startW2):
                    messages.warning(request, '(λήξη εώς) είναι μεγαλύτερη απο (έναρξη εώς 2)')
                    return redirect('departments')
                
        s=Staff_department_info.objects.filter(id=int(staffD_id)).update(
        department_id=depID,
        staff_card=user_card_number,
        role=Roles.objects.get(role_name=myRole).role_name,
        apply_from = parse_date(applyF),
        apply_to = parse_date(applyT),
        start_of_work = startW,
        end_of_work = endW,
        spasto=spasto,
        start_of_work2 = startW2,
        end_of_work2 = endW2,
        Monday=monday,
        Tuesday=tuesday,
        Wednesday=wednesday,
        Thursday=thursday,
        Friday=friday,
        Saturday=saturday,
        Sunday=sunday
        )
        eventLogger(request,info="Χρήστης επεξεργάστηκε χρήστη σε τμήμα με τιμές: "+str(s))
        messages.success(request, 'επεξεργασία τμήματος-χρήστη επιτυχής')
        return redirect('departments')

@login_required()
@admin_required
def usersSearch(request):
    url_parameter = str(request.GET.get("q"))
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchUsersUsername-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        u=Users.objects.all()
        #mySearch = Users.objects.filter(username__contains=url_parameter)
        for item in u:
            if Users.objects.annotate(username_lower=Lower('username')).filter(username_lower__contains=url_parameter.lower()) :
                mySearch = Users.objects.annotate(username_lower=Lower('username')).filter(username_lower__contains=url_parameter.lower())
            elif Users.objects.annotate(last_name_lower=Lower('last_name')).filter(last_name_lower__contains=url_parameter.lower()) :
                mySearch = Users.objects.annotate(last_name_lower=Lower('last_name')).filter(last_name_lower__contains=url_parameter.lower())
            elif  Users.objects.annotate(first_name_lower=Lower('first_name')).filter(first_name_lower__contains=url_parameter.lower()): 
                mySearch =Users.objects.annotate(first_name_lower=Lower('first_name')).filter(first_name_lower__contains=url_parameter.lower())
            else:
                mySearch=None  
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchUsersUsername-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
 
 
@login_required()
@admin_required
def wrariaProsopikouSearch(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchWrariaProsopikou-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        for item in saveSearch:
            if url_parameter.lower() in item.get('last_name').lower() or url_parameter.lower() in item.get('first_name').lower():
                mySearch.append(item)
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchWrariaProsopikou-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    
def depInfoSearch(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchDepInfo-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        for item in depInfo:
            if url_parameter.lower() in item.get('last_name').lower() or url_parameter.lower() in item.get('first_name').lower():
                mySearch.append(item)
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchDepInfo-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    
     

def searchCurrDep(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchCurrDep-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        #print(saveCurrSearch)
        for item in saveCurrSearch:
            #print(item)
            if url_parameter.lower() in item.get('DepSearch').lower():
                mySearch.append(item)
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchCurrDep-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults,'fullattendaces': summaryQueryDictSearch,'departments':summaryTestSearch},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)



def searchCurrID(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchCurrCard-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        print(summaryQueryDictSearch)
        for item in summaryQueryDictSearch:
            print(item)
            if int(url_parameter) == item.get('user_card'):
                mySearch.append(item)
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchCurrCard-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults,'fullattendaces': summaryQueryDictSearch,'departments':summaryTestSearch},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    
    

def searchCurrLF(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchCurrLF-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        #print(saveCurrSearch)
        for item in summaryQueryDictSearch:
            print(item)
            if url_parameter.lower() in item.get('last_name').lower()+item.get('first_name').lower() or url_parameter.lower() in item.get('first_name').lower()+item.get('last_name').lower() :
                mySearch.append(item)
        print('----')
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchCurrLF-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
        
     
def searchDevU(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchDeviceDUsers-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        #print(usersDv)
        for item in usersDv:
            #print(item)
            if url_parameter.lower() in item.name.lower()+str(item.user_id):
                mySearch.append(item)
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchDeviceDUsers-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)


    
def searchDevAtt(request):
    mySearch=[]
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchDeviceDAtt-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        #print(fullatendances_DeviceData)
        for item in reversed(fullatendances_DeviceData):
            print(item)
            if url_parameter.lower() in item.lower():
                mySearch.append(item)
        print(mySearch)   
        if mySearch:  
            noResults=False
        html = render_to_string(
            template_name="searchDeviceDAtt-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)

     

def holidaySearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    mySearch=None
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchHoliday-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Holidays.objects.annotate(description_lower=Lower('description')).filter(description_lower__contains=url_parameter.lower())
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchHoliday-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    


def eventSearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchEvent-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        if Event_log.objects.annotate(function_event_lower=Lower('function_event')).filter(function_event_lower__contains=url_parameter.lower()):
            mySearch = Event_log.objects.annotate(function_event_lower=Lower('function_event')).filter(function_event_lower__contains=url_parameter.lower())
        elif Event_log.objects.annotate(function_used_info_lower=Lower('function_used_info')).filter(function_used_info_lower__contains=url_parameter.lower()):
            mySearch=Event_log.objects.annotate(function_used_info_lower=Lower('function_used_info')).filter(function_used_info_lower__contains=url_parameter.lower())
        else:
            mySearch=None
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchEvent-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    

def eventDateSearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    mySearch=None
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchEventDate-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Event_log.objects.filter(created_date__contains=url_parameter)
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchEventDate-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)

    

def holidayDateSearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    mySearch=None
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchHolidayDate-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Holidays.objects.filter(date_from=url_parameter)
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchHolidayDate-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
        
        

def staffHolidaysSearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchStaffHolidays-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Staff_holidays.objects.annotate(last_name_lower=Lower('last_name')).filter(last_name_lower__contains=url_parameter.lower())
        if mySearch:  
            noResults=False
        elif not mySearch:
            mySearch = Staff_holidays.objects.annotate(first_name_lower=Lower('first_name')).filter(first_name_lower__contains=url_parameter.lower())
        else:
            mySearch=None
            if mySearch:
                noResults=False
        html = render_to_string(
            template_name="searchStaffHolidays-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
               
        

def signatureSearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    mySearch=None
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchSignature-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Signatures.objects.annotate(signature_name_lower=Lower('signature_name')).filter(signature_name_lower__contains=url_parameter.lower())
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchSignature-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
        

def devicesSearch(request):
    url_parameter = request.GET.get("q")
    noResults=True
    mySearch=None
    if len(url_parameter)==0:#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchDevicesLocation-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Devices.objects.annotate(device_location_lower=Lower('device_location')).filter(device_location_lower__contains=url_parameter.lower())
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchDevicesLocation-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
        

def usersSearchNumID(request):
    url_parameter = request.GET.get("q")
    noResults=True
    mySearch=None
    if len(url_parameter)==0 :#no user input
        mySearch=''
        noResults=False
        html = render_to_string(
            template_name="searchUsersCard-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)
    else:# user inputs
        mySearch = Users.objects.filter(device_card_number__contains=int(url_parameter))
        if mySearch:# record found
            noResults=False
        html = render_to_string(
            template_name="searchUsersCard-partial.html", 
            context={"mySearch": mySearch,"noResults":noResults},request=request
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict,safe=False)

@admin_required
@login_required()
def users(request):# we load all users from excel file and load them as row list inside a excel list 
    if "GET" == request.method:
        myM=Members_team.objects.values('id','member_team_name')
        myR=Relation_types.objects.values('id','relation_type_name')
        listM=[]
        listR=[]
        for m in myM:
            listM.append(m)
        for r in myR:
            listR.append(r)
        if Users.objects.all().order_by('id'):
            myUsers_list = Users.objects.all().order_by('id')
            paginator = Paginator(myUsers_list, 12)
            page = request.GET.get('page', 1)
            try:
                myUsers = paginator.page(page)
            except PageNotAnInteger:
                myUsers = paginator.page(1)
            except EmptyPage:
                myUsers = paginator.page(paginator.num_pages)
        else:
            myUsers=''
        formA=AddUserForm()
        formE = EditUserForm()
        eventLogger(request,info="Χρήστης μπήκε στο προσωπικό")
        return render(request, 'users.html', {'myUsers':myUsers,'form':formA,'formE':formE,'Members':listM,'RelationT':listR})

@admin_required    
@login_required()  
def userGet(request,id): #return the object as string from ajax get request
    myUser=Users.objects.get(id=id)
    return HttpResponse(myUser)

@admin_required
@login_required()  
def AttRRGet(request,id): #return the object as string from ajax get request
    myAttRR=Staff_attendance_rearranged_report.objects.get(id=id)
    return HttpResponse(myAttRR)

@admin_required
@login_required()  
def AttRRNoGet(request,id): #return the object as string from ajax get request
    myAttNoRR=Users.objects.get(device_card_number=id)
    return HttpResponse(myAttNoRR)

@admin_required
@login_required()  
def roleGet(request,id): #return the object as string from ajax get request
    myRole=Roles.objects.get(id=id)
    return HttpResponse(myRole)

@admin_required
@login_required()  
def holidayGet(request,id): #return the object as string from ajax get request
    myholiday=Holidays.objects.get(id=id)
    return HttpResponse(myholiday)

@admin_required
@login_required()  
def staffHolidayGet(request,id): #return the object as string from ajax get request
    myStaffHoliday=Staff_holidays.objects.get(id=id)
    return HttpResponse(myStaffHoliday)

@admin_required
@login_required()  
def relationTGet(request,id): #return the object as string from ajax get request
    myRelationT=Relation_types.objects.get(id=id)
    return HttpResponse(myRelationT)
    
@admin_required      
@login_required()
def userAdd(request): #we add a new user at the last new row of excel file and serve the updated excel file
    if request.method == 'POST':
        u=Users.objects.last('id').id  #get the plain id
        u2=Users.objects.last('id').device_card_id   #get from id the device_card_id
        logger.error(u2)
        form = AddUserForm(request.POST)
        if form.is_valid():
            obj=Users()
            obj=form.save(commit=False)
            obj.id=u+1                      #fill the data like id and device_card_id based on the last one
            obj.device_card_id=u2+1
            logger.error(obj)
            obj.save()
            eventLogger(request,info="Χρήστης πρόσθεσε χρήστη με τιμές: "+str(obj))
            messages.success(request,"χρήστης "+obj.username+" δημιουργήθηκε")
            return redirect('users')
        else:
            messages.error(request, form.errors)
            logger.error('err1')
            return redirect('users')
    logger.error('err2')
    return redirect('users')


@admin_required
@login_required()
def roleEdit(request):# update excel user based on id
    if request.method == 'POST':
        myId=request.POST.get('id') # get id from hidden field from jquery function, on ajax get
        obj=Roles.objects.get(id=myId).role_name
        name_role=request.POST.get('name_role')
        if len(name_role)>0:
            r=Roles.objects.filter(id=myId).update(role_name=name_role)
            #update role in staff_info
            Staff_department_info.objects.filter(role=obj).update(role=name_role)
        else:
            messages.warning(request,"ρόλος κενός, δεν ανανεώθηκε")
            return redirect('role')
    eventLogger(request,info="Χρήστης ανανέωσε ρόλο με τιμές: "+str(r))
    messages.success(request,"ρόλος ανανεώθηκε")
    return redirect('role')

@admin_required
@login_required()
def holidayEdit(request):# update excel user based on id
    if request.method == 'POST':
        myId=request.POST.get('id') # get id from hidden field from jquery function, on ajax get
        obj=Holidays.objects.get(id=myId)
        description=request.POST.get('name_holiday')
        date_f=request.POST.get('from')
        date_t=request.POST.get('to')
        if len(description)>0:
            h=Holidays.objects.filter(id=myId).update(description=description,date_from=parse_date(date_f),date_to=parse_date(date_t))
        else:
            messages.warning(request,"αργία κενή, δεν ανανεώθηκε")
            return redirect('holiday')
    eventLogger(request,info="Χρήστης ανανέωσε αργία με τιμές: "+str(h))
    messages.success(request,"αργία ανανεώθηκε")
    return redirect('holiday')

@admin_required
@login_required()
def relationTEdit(request):# update excel user based on id
    if request.method == 'POST':
        myId=request.POST.get('id') # get id from hidden field from jquery function, on ajax get
        obj=Relation_types.objects.get(id=myId)
        name_RelationType=request.POST.get('name_RelationType')
        if len(name_RelationType)>0:
            old=Relation_types.objects.get(id=myId).relation_type_name
            r=Relation_types.objects.filter(id=myId).update(relation_type_name=name_RelationType)
            Users.objects.filter(relation_type=old).update(relation_type=name_RelationType)
        else:
            messages.warning(request,"σχέση εργασίας κενό, δεν ανανεώθηκε")
            return redirect('relationType')
    eventLogger(request,info="Χρήστης ανανέωσε σχέση εργασίας με τιμές: "+str(r))
    messages.success(request,"σχέση εργασίας ανανεώθηκε")
    return redirect('relationType')

@admin_required
@login_required()
def userEdit(request):# update excel user based on id
    if request.method == 'POST':
        myId=request.POST.get('id') # get id from hidden field from jquery function, on ajax get
        obj=Users.objects.get(id=myId)
        oldCardID=obj.device_card_id
        oldCardNum=obj.device_card_number
        oldUID=obj.id
        oldUsername=obj.username
        oldlast_name=obj.last_name
        oldfirst_name=obj.first_name
        oldhrms=obj.hrms_id
        form = EditUserForm(request.POST,instance=obj) # to perform edit from form, we need the instance from obj to overide it
        #logger.error(Users.objects.get(id=1).password)
        if form.is_valid():
            if len(request.POST.get('password'))>0:     # if user gives password, we will save it sa new one
                obj.set_password(request.POST.get('password'))
                obj.save()
                #update user info across db
                Staff_department_info.objects.filter(staff_card=oldCardNum).update(staff_card=obj.device_card_number)
                Staff_holidays.objects.filter(staff_card=oldCardNum,hrms_id=oldhrms,first_name=oldfirst_name,last_name=oldlast_name).update(staff_card=obj.device_card_number,hrms_id=obj.hrms_id,first_name=obj.first_name,last_name=obj.last_name)
                Staff_attendance.objects.filter(user_card_number=oldCardNum,username=oldUsername).update(user_card_number=obj.device_card_number,username=obj.username)
                Staff_attendance_rearranged_report.objects.filter(username=oldUsername,staff_card=oldCardNum).update(username=obj.username,staff_card=obj.device_card_number)
                eventLogger(request,info="Χρήστης ανανέωσε στοιχεία προσωπικού και κωδικό")
                messages.success(request,"χρήστης "+obj.username+" ανανεώθηκε με τιμές: "+str(obj))
                return redirect('users')
            else:
                oldpass=Users.objects.get(id=myId).password # else we save again the old one
                obj.password=oldpass
                obj.save()
                print(obj.username)
                #update user info across db
                Staff_department_info.objects.filter(staff_card=oldCardNum).update(staff_card=obj.device_card_number)
                Staff_holidays.objects.filter(staff_card=oldCardNum,hrms_id=oldhrms,first_name=oldfirst_name,last_name=oldlast_name).update(staff_card=obj.device_card_number,hrms_id=obj.hrms_id,first_name=obj.first_name,last_name=obj.last_name)
                Staff_attendance.objects.filter(user_card_number=oldCardNum,user_card_id=oldCardID,user_uid=oldUID,username=oldUsername).update(user_card_number=obj.device_card_number,user_card_id=obj.device_card_id,user_uid=obj.id,username=obj.username)
                Staff_attendance_rearranged_report.objects.filter(username=oldUsername,staff_card=oldCardNum).update(username=obj.username,staff_card=obj.device_card_number)
                messages.success(request,"χρήστης "+obj.username+" ανανεώθηκε")
                eventLogger(request,info="Χρήστης ανανέωσε στοιχεία προσωπικού με τιμές: "+str(obj))
                return redirect('users')       
        else:
            messages.error(request, form.errors)
            logger.error('err1')
            return redirect('users')
    logger.error('err2')
    return redirect('users')
 
@admin_required   
@login_required()
def userDelete(request):
    if request.method == "POST" :
        myID = request.POST.get('idDel')
        u=Users.objects.get(id=myID)
        u.delete()
        messages.info(request,"διαγραφή χρήστη έγινε επιτυχώς")
        eventLogger(request,info="Χρήστης διέγραψε χρήστη με τιμές: "+str(u))
    return redirect('users')


saveCurrSearch=''
summaryQueryDictSearch=''
summaryTestSearch=''    
@login_required()
def currentAttendance(request):
    global summaryQueryDictSearch
    global summaryTestSearch
    global saveCurrSearch
    if "GET" == request.method or "POST"==request.method:
        today=str(date.today())
        global summaryQueryDict
        myDate = request.POST.get('myDate')
        myDateClean=''
        if myDate =='' or myDate==None:
            myDateClean=date.today()
            myDate=date.today()
            myDate = myDate.strftime("%Y-%m-%d")
        myDate2 = datetime.strptime(myDate, '%Y-%m-%d').strftime('%d/%m/%Y')
        oraDate=datetime.strptime(myDate, '%Y-%m-%d').strftime('%d/%b/%Y')
        if myDateClean==date.today():
            eventLogger(request,info="Χρήστης μπήκε τρέχουσα κατάσταση για σήμερα")
            SynchronizeAttendancesOfToday(request)
            return currentAttendanceOfToday(request)
        try:#prepare to categorize all dep
            print("db--querries")
            dbUsers=Users.objects.order_by('id')
            departments_list=Departments.objects.all().order_by('id')
            queryTest= {'DepPapous':"",'DepMpampas':"",'DepChild':"",'DepNone':"",'DepID':"",'DepPID':"",'DepSearch':""}
            summaryTest=[]
            print("membersDep")
            print(DepForMembers(request))
            for dep in DepForMembers(request):#departments_list: 
                if dep['parent_id']==0 :    #check if it is papous
                    queryTest['DepPapous']=dep['department_name']
                    queryTest['DepSearch']=dep['department_name']
                    queryTest['DepID']=dep['id']
                    queryTest['DepPID']=dep['parent_id']
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
                elif dep['parent_id']==dep['industry_id']:  #check if it is mpampas
                    queryTest['DepMpampas']=dep['department_name']
                    queryTest['DepSearch']=dep['department_name']
                    queryTest['DepID']=dep['id']
                    queryTest['DepPID']=dep['parent_id']
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
                    for i in range(0,Departments.objects.filter(parent_id=dep['id']).count(),1):#check mpampas if has childs
                        queryTest['DepChild']=Departments.objects.filter(parent_id=dep['id'])[i].department_name
                        queryTest['DepSearch']=Departments.objects.filter(parent_id=dep['id'])[i].department_name
                        queryTest['DepID']=Departments.objects.filter(parent_id=dep['id'])[i].id
                        queryTest['DepPID']=Departments.objects.filter(parent_id=dep['id'])[i].parent_id
                        summaryTest.append(queryTest.copy())
                        queryTest.clear()
                elif dep['id']==Departments.objects.count()+1 : 
                    queryTest['DepChild']=dep['department_name']
                    queryTest['DepSearch']=dep['department_name']
                    queryTest['DepID']=dep['id']
                    queryTest['DepPID']=dep['parent_id']
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
            # queryTest['DepNone']="ΧΩΡΙΣ ΤΜΗΜΑ"
            # queryTest['DepSearch']="ΧΩΡΙΣ ΤΜΗΜΑ"
            # queryTest['DepID']=Departments.objects.last().id+1
            # queryTest['DepPID']=None
            # summaryTest.append(queryTest.copy())
            # queryTest.clear()
            flagHrms=False
            queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"","fathers_name":'',
            'Fattendance_time': "", 'Lattendance_time': "",'department':'','DepID':"",'Hrms':""} 
            try:#hrms connection check
                if parse_date(myDate).weekday()==5 or parse_date(myDate).weekday()==6:
                    messages.warning(request,"Weekend selected")
                if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                    myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                    comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                    #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                    conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                    c = conn.cursor()
                    flagHrms=True
                else:
                    flagHrms=False
                    messages.warning(request,"Hrms δεν συνδέθηκε")
            except cx_Oracle.DatabaseError as e: 
                print("error save one hrms connections", e)
            summaryQueryDict=[]
            print("membersUser")
            print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                try:#hrms get data
                    if flagHrms:
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE('"""+oraDate+"""', 'DD MON YYYY')  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id""") 
                        for row in c:
                            print(row[12])
                            queryDict['Hrms']=row[12]
                    else:
                        print('hrms not connected')
                        queryDict['Hrms']='----'
                          
                except Exception as e:
                    print("Process terminate 1 : {}".format(e))
                #checκ holidays and adeies
                for item in Holidays.objects.all():
                    if item.date_from<=parse_date(myDate)<=item.date_to: # is holiday and user not work on holidays
                        print('holiday1')
                        if not dbu['works_on_holidays']:
                            print('holiday2')
                            queryDict['Hrms']=item.description
                            
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine(parse_date(myDate),datetime.min.time()))<=item.date_to:# user has adeia
                        print('holiday3')
                        queryDict['Hrms']=item.description
                if Staff_department_info.objects.filter(staff_card=dbu['user_card']):#belongs to dep
                    staff=Staff_department_info.objects.filter(staff_card=dbu['user_card']).first()
                    if  staff.apply_to >= parse_date(myDate) and staff.apply_from <= parse_date(myDate): #show dep if only on duty range of time
                        dep = Departments.objects.get(id=staff.department_id).department_name
                        # if staff.apply_to < parse_date(myDate):#has expired
                        #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                        # if staff.apply_from > parse_date(myDate):#has not started
                        #     queryDict['Hrms']='δεν άρχισε ακόμα'
                        #check if user works that day of the week
                        if parse_date(myDate).weekday()==0:#monday
                            if staff.Monday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==1:#tuesday
                            if staff.Tuesday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==2:#wednesday
                            if staff.Wednesday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==3:#thursday
                            if staff.Thursday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==4:#Friday
                            if staff.Friday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==5:#saturday
                            if staff.Saturday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==6:#sunday
                            if staff.Sunday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    
                    queryDict['first_name']=dbu['first_name']
                    queryDict['last_name']=dbu['last_name']
                    queryDict['fathers_name']=dbu['fathers_name']
                    queryDict['department'] = dep
                    queryDict['DepID'] = staff.department_id
                    queryDict['Role'] = staff.role
                    queryDict['user_card']=dbu['user_card']
                else:#has no dep
                    queryDict['department'] ='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDict['DepID'] = Departments.objects.last().id+1
                    queryDict['first_name']=dbu['first_name']
                    queryDict['last_name']=dbu['last_name']
                    queryDict['fathers_name']=dbu['fathers_name']
                    queryDict['Role']='--'
                    queryDict['user_card']=dbu['user_card']
                print('???ela1')
                try:#find att
                    qcheck=Staff_attendance_rearranged_report.objects.filter(day=myDate,staff_card=dbu['user_card'])[0] 
                    try:#check normal hit and then other 2 hits
                        staffS=Staff_department_info.objects.filter(staff_card=dbu['user_card'],spasto=True).first()
                        if staffS.spasto: # to break if not
                            print('spasto')
                            q1=Staff_attendance_rearranged_report.objects.filter(day=myDate,staff_card=dbu['user_card']).first()
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" "+'σπαστό'
                            queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" "+'σπαστό'
                            summaryQueryDict.append(queryDict.copy())#for double print
                            queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" "+'σπαστό'
                            queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name+" "+'σπαστό'
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                    except Exception as e:
                        print("spasto fails : {}".format(e))
                            #find att without spasto, normal
                        q1=Staff_attendance_rearranged_report.objects.filter(day=myDate,staff_card=dbu['user_card']).order_by('id')
                        for attR in q1:
                            queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                            if attR.attendance_time_out==time(0,0,0):#check ελλιπές χτύπημα
                                queryDict['Lattendance_time']='----'
                            else:  
                                queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                            summaryQueryDict.append(queryDict.copy())
                        queryDict.clear()         
                except Exception as e:
                    print("Process terminate 3 : {}".format(e))
                    #no attendance
                    queryDict['Fattendance_time']='----'
                    queryDict['Lattendance_time']='----'  
                    summaryQueryDict.append(queryDict.copy())
                    queryDict.clear()  
            print("-------------")
            #print(summaryQueryDict)
        except Exception as e:
            print("Process terminate 2 : {}".format(e))
        saveCurrSearch=summaryTest
        summaryQueryDictSearch=summaryQueryDict
        summaryTestSearch=summaryTest
        eventLogger(request,info="Χρήστης μπήκε τρέρουσα κατάσταση για άλλη ημέρα")
        return render(request, 'currentAttendance.html', {'fullattendaces': summaryQueryDict, 'date': myDate2,'myDateMax': today,'departments':summaryTest})

@login_required()
def currentAttendanceOfToday(request):
    global summaryQueryDictSearch
    global summaryTestSearch
    global saveCurrSearch
    summaryQueryDict=[]
    if "GET" == request.method or "POST"==request.method:
        today=str(date.today())
        myDate=date.today()
        myDate = myDate.strftime("%Y-%m-%d")
        myDate2 = datetime.strptime(myDate, '%Y-%m-%d').strftime('%d/%m/%Y')
        oraDate=datetime.strptime(myDate, '%Y-%m-%d').strftime('%d/%b/%Y')
        print("db--querries")
        try: #prepare to categorize all dep
            dbUsers=Users.objects.order_by('id')
            departments_list=Departments.objects.all().order_by('id')
            queryTest= {'DepPapous':"",'DepMpampas':"",'DepChild':"",'DepNone':"",'DepID':"",'DepPID':""}
            summaryTest=[]
            print("membersDep")
            print(DepForMembers(request))
            for dep in DepForMembers(request):#departments_list: 
                if dep['parent_id']==0 :    #check if it is papous
                    queryTest['DepPapous']=dep['department_name']
                    queryTest['DepSearch']=dep['department_name']
                    queryTest['DepID']=dep['id']
                    queryTest['DepPID']=dep['parent_id']
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
                elif dep['parent_id']==dep['industry_id']:  #check if it is mpampas
                    queryTest['DepMpampas']=dep['department_name']
                    queryTest['DepSearch']=dep['department_name']
                    queryTest['DepID']=dep['id']
                    queryTest['DepPID']=dep['parent_id']
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
                    for i in range(0,Departments.objects.filter(parent_id=dep['id']).count(),1):#check mpampas if has childs
                        queryTest['DepChild']=Departments.objects.filter(parent_id=dep['id'])[i].department_name
                        queryTest['DepSearch']=Departments.objects.filter(parent_id=dep['id'])[i].department_name
                        queryTest['DepID']=Departments.objects.filter(parent_id=dep['id'])[i].id
                        queryTest['DepPID']=Departments.objects.filter(parent_id=dep['id'])[i].parent_id
                        summaryTest.append(queryTest.copy())
                        queryTest.clear()
                elif  dep['id']==Departments.objects.count()+1 : 
                    queryTest['DepChild']=dep['department_name']
                    queryTest['DepSearch']=dep['department_name']
                    queryTest['DepID']=dep['id']
                    queryTest['DepPID']=dep['parent_id']
                    summaryTest.append(queryTest.copy())
                    queryTest.clear()
                
            # queryTest['DepNone']="ΧΩΡΙΣ ΤΜΗΜΑ"
            # queryTest['DepSearch']="ΧΩΡΙΣ ΤΜΗΜΑ"
            # queryTest['DepID']=Departments.objects.last().id+1
            # queryTest['DepPID']=''
            # summaryTest.append(queryTest.copy())
            # queryTest.clear()
            flagHrms=False
            #summaryQueryDict=[]
            queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"", "fathers_name":'',
            'Fattendance_time': "", 'Lattendance_time': "",'department':"",'DepID':"",'Hrms':""}
            try:#hrms connection check
                if parse_date(myDate).weekday()==5 or parse_date(myDate).weekday()==6:
                    messages.warning(request,"Weekend selected")
                if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                    myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                    comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                    #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                    conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                    c = conn.cursor()
                    flagHrms=True
                else:
                    flagHrms=False
                    messages.warning(request,"Hrms δεν συνδέθηκε")
            except cx_Oracle.DatabaseError as e: 
                print("error save one hrms connections", e)
            print("membersUser")
            print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                try:#hrms get data
                    if flagHrms:
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+"""and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE('"""+oraDate+"""','DD MON YYYY') and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id""") 
                        for row in c:
                            print(row[12])
                            queryDict['Hrms']=row[12]
                    else:
                        print('hrms not connected')
                        queryDict['Hrms']='----'
                     
                except Exception as e:
                    print("Process terminate 1 : {}".format(e))
                #checκ holidays and adeies
                for item in Holidays.objects.all():
                    if item.date_from<=parse_date(myDate)<=item.date_to: # is holiday and user not work on holidays
                        #print('holiday1')
                        if not dbu['works_on_holidays']:
                            #print('holiday2')
                            queryDict['Hrms']=item.description
                            
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine(parse_date(myDate),datetime.min.time()))<=item.date_to:# user has adeia
                        #print('holiday3')
                        queryDict['Hrms']=item.description
                if Staff_department_info.objects.filter(staff_card=dbu['user_card']):#belongs to dep
                    staff=Staff_department_info.objects.filter(staff_card=dbu['user_card']).first()
                    if  staff.apply_to >= parse_date(myDate) and staff.apply_from <= parse_date(myDate): #show dep if only on duty range of time
                        dep = Departments.objects.get(id=staff.department_id).department_name
                        # if staff.apply_to < parse_date(myDate):#has expired
                        #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                        # if staff.apply_from > parse_date(myDate):#has not started
                        #     queryDict['Hrms']='δεν άρχισε ακόμα'
                        #check if user works that day of the week
                        #check if user works that day of the week
                        if parse_date(myDate).weekday()==0:#monday
                            if staff.Monday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==1:#tuesday
                            if staff.Tuesday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==2:#wednesday
                            if staff.Wednesday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==3:#thursday
                            if staff.Thursday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==4:#Friday
                            if staff.Friday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==5:#saturday
                            if staff.Saturday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                        if parse_date(myDate).weekday()==6:#sunday
                            if staff.Sunday:
                                pass
                            else:
                                pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                             
                    queryDict['first_name']=dbu['first_name']
                    queryDict['last_name']=dbu['last_name']
                    queryDict['fathers_name']=dbu['fathers_name']
                    queryDict['department'] = dep
                    queryDict['DepID'] = staff.department_id
                    queryDict['Role'] = staff.role
                    queryDict['user_card']=dbu['user_card']
                else:#has no dep
                    queryDict['department'] ='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDict['DepID'] = Departments.objects.last().id+1
                    queryDict['first_name']=dbu['first_name']
                    queryDict['last_name']=dbu['last_name']
                    queryDict['fathers_name']=dbu['fathers_name']
                    queryDict['Role']='--'
                    queryDict['user_card']=dbu['user_card']
                print('???ela1')
                try:#find att
                    qCheck=Staff_attendance.objects.filter(attendance_date=myDate,user_card_number=dbu['user_card'])[0]
                    # try: #spasto 
                    #     staffS=Staff_department_info.objects.filter(staff_card=dbu['user_card'],spasto=True).first()
                    #     if staffS.spasto: #spasto
                    #         print('spasto')
                    #         try:#check hits if one 1
                    #             q1=Staff_attendance.objects.filter(attendance_date=myDate,user_card_number=dbu['user_card'])
                    #             q1First=q1.first()
                    #             queryDict['user_card']=q1First.user_card_number
                    #             queryDict['Fattendance_time']=str(q1First.attendance_time)+", "+q1First.device_name+" "+'σπαστό'
                    #         except Exception as e:
                    #             print("spasto if one hit fails : {}".format(e))
                    #             queryDict['user_card']=dbu['user_card']
                    #             queryDict['Fattendance_time']='----'+" "+'σπαστό'
                    #             queryDict['Lattendance_time']='----'+" "+'σπαστό'
                    #             summaryQueryDict.append(queryDict.copy())#for double print
                    #             queryDict.clear()
                    #         try:# second 2 hit spasto
                    #             print("spasto1")
                    #             q1[1]
                    #             queryDict['Lattendance_time']=str(q1[1].attendance_time)+", "+q1[1].device_name+" "+'σπαστό'
                    #             summaryQueryDict.append(queryDict.copy())
                    #         except Exception as e:
                    #             print("q1[1] fails : {}".format(e))
                    #             queryDict['Lattendance_time']='----'+" "+'σπαστό'
                    #             summaryQueryDict.append(queryDict.copy())
                    #             queryDict.clear()  
                    #         try:# third 3 hit spasto
                    #             print("spasto2")
                    #             q1[2]
                    #             #summaryQueryDict.append(queryDict.copy())#for double print
                    #             queryDict['Fattendance_time']=str(q1[2].attendance_time)+", "+q1[2].device_name+" "+'σπαστό'
                    #         except Exception as e:
                    #             print("q1[2] fails : {}".format(e))
                    #             #summaryQueryDict.append(queryDict.copy())#for double print
                    #             queryDict['Fattendance_time']='----'+" "+'σπαστό'
                    #             queryDict['Lattendance_time']='----'+" "+'σπαστό'
                    #             summaryQueryDict.append(queryDict.copy())
                    #             queryDict.clear()  
                    #         try:# fourth 4 hit spasto
                    #             print("spasto3")
                    #             q1[3]
                    #             queryDict['Lattendance_time']=str(q1[3].attendance_time)+", "+q1[3].device_name+" "+'σπαστό'
                    #             summaryQueryDict.append(queryDict.copy())
                    #             queryDict.clear()  
                    #         except Exception as e:
                    #             print("q1[3] fails : {}".format(e))
                    #             queryDict['Lattendance_time']='----'+" "+'σπαστό'
                    #             summaryQueryDict.append(queryDict.copy())
                    #             queryDict.clear()                 
                    # except Exception as e:  # without spasto
                    #     print("spasto whole fails : {}".format(e))
                    #if Staff_department_info.objects.filter(staff_card=dbu['user_card']):#normal
                    q1=Staff_attendance.objects.filter(attendance_date=myDate , user_card_number=dbu['user_card']).order_by('id')
                    q1Last=q1.last()
                    i=1
                    for att in q1:
                        if att.attendance_time==q1Last.attendance_time and q1.count() % 2==1:  #q1.count() % 2==1: # monos arithmos gia afikseis, kai last
                            queryDict['Fattendance_time']=str(q1Last.attendance_time)+", "+q1Last.device_name
                            queryDict['Lattendance_time']='----'#panta gia mona prepei apoxwriseis
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()  
                        elif  i % 2==1:#zygos arithmos apwxwrisi--str((q1[q1.count()-2]).attendance_time)+", "+(q1[q1.count()-2]).device_name
                            queryDict['Fattendance_time']=str(att.attendance_time)+", "+(att).device_name #pisw apo last h afiksi
                            i+=1
                        elif i % 2==0:
                            queryDict['Lattendance_time']=str(att.attendance_time)+", "+att.device_name# apoxwrisi 
                            i+=1 
                            summaryQueryDict.append(queryDict.copy())    
                except Exception as e:
                    print("Process terminate 3 : {}".format(e))
                    #no attendance
                    queryDict['Fattendance_time']='----'
                    queryDict['Lattendance_time']='----'  
                    summaryQueryDict.append(queryDict.copy())
                queryDict.clear()  
            print("-------------")
            #print(summaryQueryDict)
        except Exception as e:
            print("Process terminate 2 today: {}".format(e))
        saveCurrSearch=summaryTest
        summaryQueryDictSearch=summaryQueryDict
        summaryTestSearch=summaryTest
        print(summaryQueryDict)
        print(summaryTest)
        return render(request, 'currentAttendance.html', {'fullattendaces': summaryQueryDict, 'date': myDate2,'myDateMax': today,'departments':summaryTest})

@admin_required        
@login_required()
def industry(request):
    if "GET" == request.method:
        if Industry.objects.first() :
            indData=Industry.objects.first()
        else: 
            indData={}
        eventLogger(request,info="Χρήστης μπήκε στη επεξεργασία φορέα")
        return render(request, 'industry.html',{'industry':indData})
    else:
        name = request.POST.get('nameI')
        afm = request.POST.get('afmI')
        address = request.POST.get('addressI')
        general_w_r_f=request.POST.get('general_work_r_f')
        general_w_r_t=request.POST.get('general_work_r_t')
        if parse_time(general_w_r_f)>=parse_time(general_w_r_t):
            messages.warning(request,"Έναρξη γενικού ωραρίου μεγαλύτερη ή ίση της λήξης")
            return redirect('industry')
        ind=Industry.objects.update_or_create(
        afm=int(afm), #is unique , use to get the instace if exist for update
        defaults={
                'afm': int(afm),   # values for update
              'address':address,
              'name':name,
              'general_work_range_to':general_w_r_t,
              'general_work_range_from':general_w_r_f
              }, )
        eventLogger(request,info="Χρήστης έσωσε νέα στοιχεία φορέα με τιμές: "+str(ind))
        messages.success(request,"Νέα στοιχεία Φορέα ανανεώθηκαν")    
        indData=Industry.objects.first()
        return render(request, 'industry.html',{'industry':indData})

@admin_required    
@login_required()
def industryLogo(request):
    if "POST" == request.method:        
        myfile = request.FILES['theLogo']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        first=Industry.objects.first().id
        myIndustry=Industry.objects.filter(id=first).update(logo=fs.url(filename),logoPath=request.build_absolute_uri(filename))
        messages.success(request,"εικόνα ανανεώθηκε")
        eventLogger(request,info="Χρήστης ανανέωσε εικόνα φορέα με τιμές: "+str(myIndustry))
        # try:
        # except MultiValueDictKeyError:
        #     myfile=False 
    if Industry.objects.first():
        indData=Industry.objects.first()
        return render(request, 'industry.html',{'industry':indData})
    else: 
        indData={}
        return render(request, 'industry.html',{'industry':indData})
    


def DepForMembers(request):
    sumDepFM=[]
    queryDep={'department_name':"",'parent_id':"",'id':"",'industry_id':""}#organize the deps
    if (request.user.member_team_name).strip()=="Διαχειριστής" or (request.user.member_team_name).strip()=='1' :
        print('Διαχειριστής')
        for i in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            queryDep['department_name']=i.department_name
            queryDep['parent_id']=i.parent_id
            queryDep['id']=i.id
            queryDep['industry_id']=i.industry_id
            sumDepFM.append(queryDep.copy())
            queryDep.clear()
            #diaxiristis has the xwris tmima
        queryDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        queryDep['parent_id']="None"
        queryDep['id']=Departments.objects.count()+1
        queryDep['industry_id']="None"
        sumDepFM.append(queryDep.copy())
        queryDep.clear()
        return sumDepFM
    elif (request.user.member_team_name).strip()=="Δήμαρχος" or (request.user.member_team_name).strip()=='2':
        print('Δήμαρχος')
        for i in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            queryDep['department_name']=i.department_name
            queryDep['parent_id']=i.parent_id
            queryDep['id']=i.id
            queryDep['industry_id']=i.industry_id
            sumDepFM.append(queryDep.copy())
            queryDep.clear()
            #diaxiristis has the xwris tmima
        queryDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        queryDep['parent_id']="None"
        queryDep['id']=Departments.objects.count()+1
        queryDep['industry_id']="None"
        sumDepFM.append(queryDep.copy())
        queryDep.clear()
        return sumDepFM
    elif (request.user.member_team_name).strip()=="Διευθυντής" or (request.user.member_team_name).strip()=='3':
        print('Διευθυντής')
        staffDep=Staff_department_info.objects.filter(staff_card=request.user.device_card_number).last().department_id
        for i in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            if i.parent_id==staffDep or i.id==staffDep:#mpampas
                queryDep['department_name']=i.department_name
                queryDep['parent_id']=i.parent_id
                queryDep['id']=i.id
                queryDep['industry_id']=i.industry_id
                sumDepFM.append(queryDep.copy())
                queryDep.clear()    
        return sumDepFM
    elif (request.user.member_team_name).strip()=="Προϊστάμενος" or (request.user.member_team_name).strip()=='4':
        print('Προϊστάμενος')
        staffDep=Staff_department_info.objects.filter(staff_card=request.user.device_card_number).last().department_id
        for i in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            if i.id==staffDep:#child
                queryDep['department_name']=i.department_name
                queryDep['parent_id']=i.parent_id
                queryDep['id']=i.id
                queryDep['industry_id']=i.industry_id
                sumDepFM.append(queryDep.copy())
                queryDep.clear()    
        return sumDepFM
    elif (request.user.member_team_name).strip()=="Υπάλληλος" or (request.user.member_team_name).strip()=='5':
        staffDep=Staff_department_info.objects.filter(staff_card=request.user.device_card_number).last().department_id
        for i in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            if i.id==staffDep:#child
                queryDep['department_name']=i.department_name
                queryDep['parent_id']=i.parent_id
                queryDep['id']=i.id
                queryDep['industry_id']=i.industry_id
                sumDepFM.append(queryDep.copy())
                queryDep.clear()    
        return sumDepFM
    
    

def UsersForMembers(request):
    sumUserFM=[]
    queryUser={'id':"",'last_name':"",'first_name':"",'user_card':"",'fathers_name':"",'works_on_holidays':"",'hrms_id':""}#organize the deps
    if (request.user.member_team_name).strip()=="Διαχειριστής" or (request.user.member_team_name).strip()=='1':
        print('Διαχειριστής')
        for i in Users.objects.order_by('last_name'):#aquire deps list,diaxeiristis has all
            queryUser['id']=i.id
            queryUser['last_name']=i.last_name
            queryUser['first_name']=i.first_name
            queryUser['user_card']=i.device_card_number
            queryUser['fathers_name']=i.fathers_name
            queryUser['works_on_holidays']=i.works_on_holidays
            queryUser['hrms_id']=i.hrms_id
            sumUserFM.append(queryUser.copy())
            queryUser.clear()
        return sumUserFM
    elif (request.user.member_team_name).strip()=="Δήμαρχος" or (request.user.member_team_name).strip()=='2':
        print('Δήμαρχος')
        for i in Users.objects.order_by('last_name'):#aquire deps list,diaxeiristis has all
            queryUser['id']=i.id
            queryUser['last_name']=i.last_name
            queryUser['first_name']=i.first_name
            queryUser['user_card']=i.device_card_number
            queryUser['fathers_name']=i.fathers_name
            queryUser['works_on_holidays']=i.works_on_holidays
            queryUser['hrms_id']=i.hrms_id
            sumUserFM.append(queryUser.copy())
            queryUser.clear()
        return sumUserFM
    elif (request.user.member_team_name).strip()=="Διευθυντής" or (request.user.member_team_name).strip()=='3':
        print('Διευθυντής')
        staffDep=Staff_department_info.objects.filter(staff_card=request.user.device_card_number).last().department_id
        for j in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            if j.parent_id==staffDep or j.id==staffDep :#mpampas
                for i in Users.objects.order_by('last_name'):#aquire deps list,Διευθυντής has one large dep
                    if Staff_department_info.objects.filter(department_id=j.id,staff_card=i.device_card_number).last():
                        queryUser['id']=i.id
                        queryUser['last_name']=i.last_name
                        queryUser['first_name']=i.first_name
                        queryUser['user_card']=i.device_card_number
                        queryUser['fathers_name']=i.fathers_name
                        queryUser['works_on_holidays']=i.works_on_holidays
                        queryUser['hrms_id']=i.hrms_id
                        sumUserFM.append(queryUser.copy())
                        queryUser.clear()
        return sumUserFM
    elif (request.user.member_team_name).strip()=="Προϊστάμενος" or (request.user.member_team_name).strip()=='4':
        print('Προϊστάμενος')
        staffDep=Staff_department_info.objects.filter(staff_card=request.user.device_card_number).last().department_id
        for j in Departments.objects.order_by('id'):#aquire deps list,diaxeiristis has all
            if j.id==staffDep :#mpampas
                for i in Users.objects.order_by('last_name'):#aquire deps list,Διευθυντής has one large dep
                    if Staff_department_info.objects.filter(department_id=j.id,staff_card=i.device_card_number).last():
                        queryUser['id']=i.id
                        queryUser['last_name']=i.last_name
                        queryUser['first_name']=i.first_name
                        queryUser['user_card']=i.device_card_number
                        queryUser['fathers_name']=i.fathers_name
                        queryUser['works_on_holidays']=i.works_on_holidays
                        queryUser['hrms_id']=i.hrms_id
                        sumUserFM.append(queryUser.copy())
                        queryUser.clear()
        return sumUserFM
    elif (request.user.member_team_name).strip()=="Υπάλληλος" or (request.user.member_team_name).strip()=='5':
        print('Υπάλληλος')
        queryUser['id']=request.user.id
        queryUser['last_name']=request.user.last_name
        queryUser['first_name']=request.user.first_name
        queryUser['user_card']=request.user.device_card_number
        queryUser['fathers_name']=request.user.fathers_name
        queryUser['works_on_holidays']=request.user.works_on_holidays
        queryUser['hrms_id']=request.user.hrms_id
        sumUserFM.append(queryUser.copy())
        queryUser.clear()
        return sumUserFM   
     


@login_required()
def printAttendance(request):
    if "GET" == request.method:
        yesterday=str(date.today()-timedelta(days=1))
        departments_list=Departments.objects.all().order_by('id')
        queryShowDep={"id":'',"department_name":''}
        global summaryShowDep
        summaryShowDep=[]
        print("membersDep")
        print(DepForMembers(request))
        try:
            for dep in DepForMembers(request):#departments_list: 
                queryShowDep['department_name']=dep['department_name']
                queryShowDep['id']=dep['id']
                summaryShowDep.append(queryShowDep.copy())
                queryShowDep.clear()  
        except Exception as e:
            print('dep loop not found due to deletions')      
        # queryShowDep['id']=Departments.objects.count()+1
        # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        # summaryShowDep.append(queryShowDep.copy())
        # queryShowDep.clear()
        global sumSignature
        sumSignature=Signatures.objects.order_by('id')
        eventLogger(request,info="Χρήστης μπήκε στην εκτύπωση παρουσιών")
        return render(request, 'printAttendance.html', {'myDateMax': yesterday,'departments':summaryShowDep,'signatures':sumSignature})
    else:#when post method, real print is called
        choicePrint=request.POST.get('choicePrint')
        signature=request.POST.get('signatures')#get all input values for print
        yesterday=str(date.today()-timedelta(days=1))
        global url
        global daysCounter
        daysCounter=0
        url=Industry.objects.first()
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        departments_list=Departments.objects.all().order_by('id')
        myDateS = request.POST.get('startMyDate')
        myDateE = request.POST.get('endMyDate')
        myDepID = request.POST.get('dep_id')
        try:#get dep
            dep=Departments.objects.get(id=myDepID).department_name
            theDep=Departments.objects.get(id=myDepID).id
        except Exception as e:
            dep='ΧΩΡΙΣ ΤΜΗΜΑ'
            theDep=Departments.objects.count()+1
        if myDateS =='':#get dates
            myDateS=date.today()-timedelta(days=1)
            myDateS = myDateS.strftime("%Y-%m-%d")
        myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
        if myDateE =='':
            myDateE=date.today()-timedelta(days=1)
            myDateE = myDateE.strftime("%Y-%m-%d")
        myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
        dbUsers=Users.objects.order_by('id')
        d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
        d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
        if d1>d2 :#check date,start<end
            messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
            return redirect('printAttendance')
        summaryDep=[]
        queryDep={'DepName':"",'DepParent':"",'DepID':""}#organize the deps
        if Staff_department_info.objects.filter(department_id=theDep).exclude(department_id=1): #take chosen dep,also child
            queryDep['DepName']=dep
            queryDep['DepParent']=Departments.objects.get(id=theDep).parent_id
            queryDep['DepID']=theDep
            summaryDep.append(queryDep.copy())
            queryDep.clear()
        for i in Departments.objects.all():#aquire deps list,dimos has all,mpampas 1-6
            try:
                if theDep==1:#dimos all
                    if Staff_department_info.objects.filter(department_id=i.id):
                        queryDep['DepName']=Departments.objects.get(id=i.id).department_name
                        queryDep['DepParent']=Departments.objects.get(id=i.id).parent_id
                        queryDep['DepID']=Departments.objects.get(id=i.id).id
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                    if i.id==Departments.objects.last().id:
                         #without(last loop,append to dimos deps),dimos has the xwris tmima
                        queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                        queryDep['DepParent']="None"
                        queryDep['DepID']=Departments.objects.count()+1
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                elif Departments.objects.get(id=i.id).parent_id==theDep and Staff_department_info.objects.filter(department_id=i.id) :#mpampas
                    queryDep['DepName']=Departments.objects.get(id=i.id).department_name
                    queryDep['DepParent']=Departments.objects.get(id=i.id).parent_id
                    queryDep['DepID']=Departments.objects.get(id=i.id).id
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
                elif theDep==Departments.objects.count()+1 and dep=='ΧΩΡΙΣ ΤΜΗΜΑ':#without
                    queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDep['DepParent']="None"
                    queryDep['DepID']=theDep
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
            except Exception as e:
                print('dep loop not found due to deletions')               
        queryDay={'day':""}
        queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': "",'pleonasma':"",'elleimma':"" }
        flagHrms=False
        try:#hrms connection
            if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                c = conn.cursor()
                flagHrms=True
            else:
                messages.warning(request,"hrms δεν συνδέθηκε")
                flagHrms=False
        except cx_Oracle.DatabaseError as e: 
            print("error save one hrms connections", e)
        summaryQueryDict=[]
        summaryDays=[]
        print("db--querries")
        for i in range((d2 - d1).days + 1):#check every day in that range
            daysCounter+=1
            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
            queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
            print(queryDay['day'])
            summaryDays.append(queryDay.copy())
            queryDay.clear()
            print("membersUser")
            #print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                try:# get hrms data
                    if flagHrms:
                        if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                            queryDict['Hrms']='Σαβ/Κυριακο'
                        locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                        oraDate=(d1 + timedelta(days=i)).strftime('%d/%b/%Y')
                        #print("oraDate:"+oraDate)
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                        for row in c:
                            #print(row[12])
                            queryDict['Hrms']=row[12]
                    else:
                        #queryDict['Hrms']='----'
                        print('hrms not connected')
                except Exception as e:
                    print("Process terminate hrms : {}".format(e))
                for item in Holidays.objects.all():
                    if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                        print('holiday1')
                        if not dbu['works_on_holidays']:
                            print('holiday2')
                            queryDict['Hrms']=item.description           
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                        print('holiday3')
                        queryDict['Hrms']=item.description 
                #categorize users in dep
                for sumDep in summaryDep:
                    myDepID=int(sumDep['DepID'])
                    if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu['user_card']).count()<1:#without dep
                        queryDict['first_name']=dbu['first_name']
                        queryDict['last_name']=dbu['last_name']
                        queryDict['fathers_name']=dbu['fathers_name']
                        queryDict['user_card']=dbu['user_card']
                        queryDict['department'] = sumDep['DepName']
                        queryDict['Role']="-"
                        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                        queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                        #print('without dep1')
                        try:# check user att without dep
                            qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0]
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                            #print('without dep2')
                            for attR in q1:
                                queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='----' #den exei
                                    queryDict['should_work_hours']='----' #den exei
                                    queryDict['wrario']='----' #den exei
                                    queryDict['pleonasma']=str(time(0,0,0)) #den exei
                                    queryDict['elleimma']=str(time(0,0,0))#den exei
                                else: #2 χτυπηματα 
                                    queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                    queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']='----'#den exei
                                    queryDict['should_work_hours']='----'#den exei
                                    queryDict['wrario']='----'#den exei
                                    queryDict['pleonasma']=str(time(0,0,0)) #den exei
                                    queryDict['elleimma']=str(time(0,0,0)) #den exei
                                #queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                        except Exception as e:
                            print("#no attendance--without dep : {}".format(e))
                            #no attendance
                            print('without dep3')
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['worked_hours']='----'
                            queryDict['should_work_hours']='----'
                            queryDict['wrario']='----'
                            queryDict['pleonasma']=str(time(0,0,0)) #den exei
                            queryDict['elleimma']=str(time(0,0,0)) #den exei
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                    elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID): #has dep  
                        staff=Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID).first() 
                        if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)): #show dep if only on duty range of time
                            # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                            #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                            # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                            #     queryDict['Hrms']='δεν άρχισε ακόμα'
                                #check if user works that day of the week
                            if (d1 + timedelta(days=i)).weekday()==0:#monday
                                if staff.Monday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                                if staff.Tuesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                                if staff.Wednesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==3:#thursday
                                if staff.Thursday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==4:#Friday
                                if staff.Friday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==5:#saturday
                                if staff.Saturday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==6:#sunday
                                if staff.Sunday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                            if Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=False) :
                                try:# no spasto, normal dep
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                                    qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0]
                                    for attR in q1:
                                        #queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                        queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                        queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                        queryDict['wrario']=attR.wrario
                                        if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict['pleonasma']=str(time(0,0,0)) 
                                            queryDict['elleimma']=attR.should_work_hours.strftime('%H:%M:%S') 
                                        else:# 2 χτυπήματα(κανονικά) dep:  
                                            queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                            queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=attR.worked_hours_in_range.strftime('%H:%M:%S')
                                            res=timedelta(hours=attR.worked_hours.hour,minutes=attR.worked_hours.minute,seconds=attR.worked_hours.second)-timedelta(hours=attR.should_work_hours.hour,minutes=attR.should_work_hours.minute,seconds=attR.should_work_hours.second)
                                            anti_res=timedelta(hours=attR.should_work_hours.hour,minutes=attR.should_work_hours.minute,seconds=attR.should_work_hours.second)-timedelta(hours=attR.worked_hours.hour,minutes=attR.worked_hours.minute,seconds=attR.worked_hours.second)
                                            if res>=timedelta(0):
                                                queryDict['pleonasma']=res
                                                queryDict['elleimma']=str(time(0,0,0))
                                            else:
                                                queryDict['pleonasma']=str(time(0,0,0))
                                                queryDict['elleimma']=anti_res
                                        summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()                   
                                except Exception as e:#no attendance
                                    print("#no attendance has dep : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    queryDict['pleonasma']=str(time(0,0,0)) 
                                    queryDict['elleimma']=str(time(0,0,0))
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()
                                    
                            elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=True):
                                try:# spasto
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).last() 
                                    #queryDict['day']=q1.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                                    queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=q1.wrario
                                    if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        queryDict['pleonasma']=str(time(0,0,0)) 
                                        queryDict['elleimma']=q1.should_work_hours.strftime('%H:%M:%S')
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        queryDict['pleonasma']=str(time(0,0,0)) 
                                        queryDict['elleimma']=q1.should_work_hours2.strftime('%H:%M:%S')
                                    else:# 2 χτυπήματα(κανονικά) dep:  
                                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                        queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                        res=timedelta(hours=q1.worked_hours.hour,minutes=q1.worked_hours.minute,seconds=q1.worked_hours.second)-timedelta(hours=q1.should_work_hours.hour,minutes=q1.should_work_hours.minute,seconds=q1.should_work_hours.second)
                                        anti_res=timedelta(hours=q1.should_work_hours.hour,minutes=q1.should_work_hours.minute,seconds=q1.should_work_hours.second)-timedelta(hours=q1.worked_hours.hour,minutes=q1.worked_hours.minute,seconds=q1.worked_hours.second)
                                        if res>=timedelta(0):
                                            queryDict['pleonasma']=res
                                            queryDict['elleimma']=str(time(0,0,0))
                                        else:
                                            queryDict['pleonasma']=str(time(0,0,0))
                                            queryDict['elleimma']=anti_res
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2 
                                        if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                            queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict['pleonasma']=str(time(0,0,0)) 
                                            queryDict['elleimma']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        else:
                                            queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                        if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict['pleonasma']=str(time(0,0,0)) 
                                            queryDict['elleimma']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        else:
                                            queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                            queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S')
                                            res=timedelta(hours=q1.worked_hours2.hour,minutes=q1.worked_hours2.minute,seconds=q1.worked_hours2.second)-timedelta(hours=q1.should_work_hours2.hour,minutes=q1.should_work_hours2.minute,seconds=q1.should_work_hours2.second)
                                            anti_res=timedelta(hours=q1.should_work_hours2.hour,minutes=q1.should_work_hours2.minute,seconds=q1.should_work_hours2.second)-timedelta(hours=q1.worked_hours2.hour,minutes=q1.worked_hours2.minute,seconds=q1.worked_hours2.second)
                                            if res>=timedelta(0):
                                                queryDict['pleonasma']=res
                                                queryDict['elleimma']=str(time(0,0,0))
                                            else:
                                                queryDict['pleonasma']=str(time(0,0,0))
                                                queryDict['elleimma']=anti_res  
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()  
                                except Exception as e:#no attendance spasto
                                    print("#no attendance has dep spasto : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    queryDict['pleonasma']=str(time(0,0,0)) 
                                    queryDict['elleimma']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute)).strftime('%H:%M:%S')
                                    summaryQueryDict.append(queryDict.copy())#show 2 prints
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                                    queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2)
                                    queryDict['pleonasma']=str(time(0,0,0)) 
                                    queryDict['elleimma']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute)).strftime('%H:%M:%S')                                
                            #print(summaryQueryDict)
                            #print(queryDict['day'])
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()  
        print("---------")
        print(summaryQueryDict)
        print(summaryDays)
        print(summaryDep)
        summaryPeriodic=[]#Periodic print--------------
        queryPeriodic={'minTWrarioE':"",'maxTWrarioE':"",'minTwork':"",'maxTwork':"",'averageTWrario':"",'averageTWork':"",'first_name': "",'last_name': "",'Role':"",'user_card':"",'department':"",'day':"",'sumShouldWR':"",'sumWorkedHoursIR':"",'sumWorkedHours':"",'sumElleimma':"",'sumPleonasma':""}
        
        listMinTWrarioE=[]
        listMaxTWrarioE=[]
        listMinTWork=[]
        listMaxTWork=[]
        listAverageTWrario=[]
        listAverageTWork=[]
        #for periodic p-e
        listSumShouldWorkHours=[]
        listSumWorkedHoursInRange=[]
        listSumWorkedHours=[]
        listSumElleimma=[]
        listSumPleonasma=[]
        
        myCount=0
        for u in UsersForMembers(request):
            for item in summaryQueryDict:
                if u['user_card']==item.get('user_card'):
                    myCount+=1     
                    queryPeriodic['first_name']=item.get('first_name')
                    queryPeriodic['last_name']=item.get('last_name')
                    queryPeriodic['Role']=item.get('Role')
                    queryPeriodic['user_card']=item.get('user_card')
                    queryPeriodic['department']=item.get('department')
                    summaryPeriodic.append(queryPeriodic.copy())
                    queryPeriodic.clear()
                    break
        myCount2=0
        for qu in summaryPeriodic:
            tempDaysCounter=daysCounter
            for item in summaryQueryDict:
                if qu.get('user_card')==item.get('user_card') and not item.get('Hrms') :#no adeia-argia
                    myCount2+=1
                    if item.get('worked_hours_in_range')=='----' or item.get('worked_hours')=='----' or item.get('should_work_hours')=='----' or item.get('worked_hours')=='ελλιπές χτύπημα'  or item.get('worked_hours_in_range')=='ελλιπές χτύπημα':
                        item['worked_hours_in_range']=str(time(0,0,0))
                        item['worked_hours']=str(time(0,0,0))
                        #peiodic-e-p
                        item['should_work_hours']=str(time(0,0,0))
                    listMinTWrarioE.append(item.get('worked_hours_in_range'))
                    listMaxTWrarioE.append(item.get('worked_hours_in_range'))
                    listMinTWork.append(item.get('worked_hours'))
                    listMaxTWork.append(item.get('worked_hours'))
                    listAverageTWrario.append((datetime.strptime(item.get('worked_hours_in_range'),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                    listAverageTWork.append((datetime.strptime(item.get('worked_hours'),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                    #peiodic-e-p
                    #print('dayCounter')
                    #print(daysCounter)
                    if tempDaysCounter>0:
                        tempDaysCounter-=1
                        listSumShouldWorkHours.append((datetime.strptime(item.get('should_work_hours'),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                        listSumWorkedHoursInRange.append((datetime.strptime(item.get('worked_hours_in_range'),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                        listSumWorkedHours.append((datetime.strptime(item.get('worked_hours'),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                        listSumElleimma.append((datetime.strptime(str(item.get('elleimma')),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                        listSumPleonasma.append((datetime.strptime(str(item.get('pleonasma')),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                if not listMinTWrarioE:#not raise error of min,max with empty list and print zero time
                    listMinTWrarioE.append(str(time(0,0,0)))
                    listMaxTWrarioE.append(str(time(0,0,0)))
                    listMinTWork.append(str(time(0,0,0)))
                    listMaxTWork.append(str(time(0,0,0)))
                    listAverageTWrario.append((datetime.strptime(str(time(0,0,0)),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                    listAverageTWork.append((datetime.strptime(str(time(0,0,0)),"%H:%M:%S")-datetime(1900, 1, 1)).total_seconds())
                qu['minTWrarioE']=min(listMinTWrarioE)
                qu['maxTWrarioE']=max(listMaxTWrarioE)
                qu['minTWork']=min(listMinTWork)
                qu['maxTWork']=max(listMaxTWork)
            
            qu['averageTWrario']=str(timedelta(seconds=int(sum(listAverageTWrario)/len(listAverageTWrario))))
            qu['averageTWork']=str(timedelta(seconds=int(sum(listAverageTWork)/len(listAverageTWork))))
            listMinTWrarioE.clear()
            listMaxTWrarioE.clear()
            listMinTWork.clear()
            listMaxTWork.clear()       
            listAverageTWrario.clear()        
            listAverageTWork.clear()
            #peiodic-e-p
            qu['sumShouldWR']=str(convert(int(sum(listSumShouldWorkHours))))
            qu['sumWorkedHoursIR']=str(convert(int(sum(listSumWorkedHoursInRange))))
            qu['sumWorkedHours']=str(convert(int(sum(listSumWorkedHours))))
            qu['sumElleimma']=str(convert(int(sum(listSumElleimma))))
            qu['sumPleonasma']=str(convert(int(sum(listSumPleonasma))))
            listSumShouldWorkHours.clear()
            listSumWorkedHoursInRange.clear()
            listSumWorkedHours.clear()
            listSumElleimma.clear()
            listSumPleonasma.clear()
            
        #print(summaryPeriodic) 
        print(myCount)
        print(myCount2) 
        print('telos')    
        global contextPrint
        contextPrint = {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':departments_list,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'signature':signature,'url':url,'SumDeps':summaryDep,'dep':dep,'summaryPeriodic':summaryPeriodic}
        
        eventLogger(request,info="Χρήστης πάτησε εκτύπωση παρουσιών")
                 
        return render(request, 'printAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'dep':dep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'signature':signature,'signatures':sumSignature,'url':url,'SumDeps':summaryDep,"ChoicePrint":choicePrint})
    
def convert(seconds):# method that coverts seconds to hours-minutes-seconds
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)
        
        
def createAttendancesRearranged(request):
    eventLogger(request,info="μέθοδος για δημιουργία παρουσιών σε πίνακα συγκετρωτικό έτρεξε")
    summaryTable=[]
    today = date.today()
    weekBeforeToday = today - timedelta(days = 200)
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
                                    Staff_attendance_rearranged_report.objects.create(
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
                                Staff_attendance_rearranged_report.objects.create(
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
                                Staff_attendance_rearranged_report.objects.create(
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
                              
                        # if att.count() % 2==1 : # monos arithmos gia afikseis
                        #     queryTable['attendance_time_in']=attLast.attendance_time
                        #     queryTable['attendance_time_out']=time(0,0,0)#panta gia mona prepei apoxwriseis
                        #     queryTable['worked_hours']=time(0,0,0)#'ελλιπές χτύπημα'
                        # else:
                        #     queryTable['attendance_time_in']=(att[att.count()-2]).attendance_time #pisw apo last h afiksi
                        #     queryTable['attendance_time_out']=attLast.attendance_time# apoxwrisi 
                        #     queryTable['worked_hours']=str(timedelta(hours=queryTable.get('attendance_time_out').hour,minutes=queryTable.get('attendance_time_out').minute,seconds=queryTable.get('attendance_time_out').second)-timedelta(hours=queryTable.get('attendance_time_in').hour,minutes=queryTable.get('attendance_time_in').minute,seconds=queryTable.get('attendance_time_in').second))
                    # try:
                    #     Staff_attendance_rearranged_report.objects.create(
                    #     staff_card =queryTable.get('staff_card'),
                    #     username=queryTable.get('username'),
                    #     device_name=queryTable.get('device_name'),
                    #     department_name=queryTable.get('department_name'),
                    #     attendance_time_in =queryTable.get('attendance_time_in'),
                    #     attendance_time_out=queryTable.get('attendance_time_out'),
                    #     attendance_time_in2 = queryTable.get('attendance_time_in2'),
                    #     attendance_time_out2 =queryTable.get('attendance_time_out2'),
                    #     day = parse_date(queryTable.get('day')),
                    #     wrario=queryTable.get('wrario'),
                    #     wrario2=queryTable.get('wrario2'),
                    #     should_work_hours=queryTable.get('should_work_hours'),
                    #     should_work_hours2=queryTable.get('should_work_hours2'),
                    #     worked_hours_in_range=queryTable.get('worked_hours_in_range'),
                    #     worked_hours_in_range2=queryTable.get('worked_hours_in_range2'),
                    #     worked_hours =queryTable.get('worked_hours'),
                    #     worked_hours2 =queryTable.get('worked_hours2')
                    #     )
                    # except Exception as e:
                    #     print("Process terminate create row : {}".format(e))
                    # summaryTable.append(queryTable.copy())
                    # queryTable.clear() 
    #print(summaryTable)
                
                        
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, link_callback=link_callback,encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None     
      
@login_required()
def printAttendancePDF(request):
    context=contextPrint#={'fullattendaces': summaryQueryDict, 'myDateMax': today,'departments':departments_list,'dep':dep,'date1':myDate2s,'date2':myDate2e}
    pdf = render_to_pdf('realPrintAttendance.html', context)
    if pdf:
        eventLogger(request,info="Χρήστης εκτύπωσε αναλυτική")
        response = HttpResponse(pdf, content_type='application/pdf;encoding="utf-8"')
        filename = "printAnalytic_%s.pdf" %(datetime.now())
        content = "inline; filename='%s'" %(filename)#inline for attachment
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required()
def printPeriodicAttPDF(request):
    context=contextPrint#={'fullattendaces': summaryQueryDict, 'myDateMax': today,'departments':departments_list,'dep':dep,'date1':myDate2s,'date2':myDate2e}
    pdf = render_to_pdf('realPrintPeriodicAtt.html', context)
    if pdf:
        eventLogger(request,info="Χρήστης εκτύπωσε περιοδική")
        response = HttpResponse(pdf, content_type='application/pdf;encoding="utf-8"')
        filename = "printPeriodic_%s.pdf" %(datetime.now())
        content = "inline; filename='%s'" %(filename)#inline for attachment
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def printElPlDayPDF(request):
    context=contextPrint#={'fullattendaces': summaryQueryDict, 'myDateMax': today,'departments':departments_list,'dep':dep,'date1':myDate2s,'date2':myDate2e}
    pdf = render_to_pdf('realPrintElPlDay.html', context)
    if pdf:
        eventLogger(request,info="Χρήστης εκτύπωσε ελλείμματα-πλεονάσματα")
        response = HttpResponse(pdf, content_type='application/pdf;encoding="utf-8"')
        filename = "printElleimmaPleonasma_%s.pdf" %(datetime.now())
        content = "inline; filename='%s'" %(filename)#inline for attachment
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required()
def printElPlPeriodicPDF(request):
    context=contextPrint#={'fullattendaces': summaryQueryDict, 'myDateMax': today,'departments':departments_list,'dep':dep,'date1':myDate2s,'date2':myDate2e}
    pdf = render_to_pdf('realPrintElPlPeriodic.html', context)
    if pdf:
        eventLogger(request,info="Χρήστης εκτύπωσε ελλείμματα-πλεονάσματα περιοδική")
        response = HttpResponse(pdf, content_type='application/pdf;encoding="utf-8"')
        filename = "printElleimmaPleonasmaPeriodic_%s.pdf" %(datetime.now())
        content = "inline; filename='%s'" %(filename)#inline for attachment
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")
  
@login_required()
@admin_required
def printWrariaProsopikouPDF(request):
    print(summaryDaysW)
    print(summaryDepW)
    print(saveSearch)
    context=contextPrintWrario
    pdf = render_to_pdf('realPrintWrariaProsopikou.html', context)
    if pdf:
        eventLogger(request,info="Χρήστης εκτύπωσε ωράρια προσωπικού")
        response = HttpResponse(pdf, content_type='application/pdf;encoding="utf-8"')
        filename = "printWraria_%s.pdf" %(datetime.now())
        content = "inline; filename='%s'" %(filename)#inline for attachment
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

import xlwt
@admin_required
@login_required()
def printWrariaProsopikouExcel(request):
    response = HttpResponse(content_type='ms-excel')
    response['Content-Disposition'] = 'attachment; filename="printWraria_excel.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Ωράρια')
    # Sheet header, first row
    row_num = 0
    #font_style = xlwt.XFStyle()
    #font_style.font.bold = True
    font_style = xlwt.XFStyle()
    font_styleCap = xlwt.XFStyle()
    font_style.alignment.wrap = 1 # Set wrap
    font_styleCap.alignment.wrap = 1 # Set wrap
    font_style.font.bold = False
    font_styleCap.font.bold = True
    
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['light_green']
    #font_style.pattern = pattern
    font_styleCap.pattern = pattern
    
    first = ws.col(0)
    second = ws.col(1)
    third = ws.col(2)
    fourth = ws.col(3)
    fifth = ws.col(4)
    sixth = ws.col(5)
    seventh = ws.col(6)
    
    first.width =  220*20
    second.width =  220*20
    third.width =  320*20
    fourth.width = 220*20
    fifth.width =420*20
    sixth.width = 920*20
    seventh.width =220*20
    columns=['Αριθμός Κάρτας', 'Ημερομηνία', 'Επώνυμο', 'Όνομα','Ωράριο','Τμήμα','Ειδικότητα']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_styleCap)
    font_style = xlwt.XFStyle()
    rows =saveSearch
    for row in rows:
        row_num += 1
        for col_num in range(0,len(row)):
            ws.write(row_num, col_num, row.get('user_card'), font_style)
            break
        for col_num in range(1,len(row)):
            ws.write(row_num, col_num, row.get('date'), font_style)
            break
        for col_num in range(2,len(row)):
            ws.write(row_num, col_num, row.get('last_name'), font_style)
            break
        for col_num in range(3,len(row)):
            ws.write(row_num, col_num, row.get('first_name'), font_style)
            break
        for col_num in range(4,len(row)):
            ws.write(row_num, col_num, row.get('wrario'), font_style)
            break
        for col_num in range(5,len(row)):
            ws.write(row_num, col_num, row.get('department'), font_style)
            break
        for col_num in range(6,len(row)):
            ws.write(row_num, col_num, row.get('relationType'), font_style)
            break
       # writer.writerow({'A/A': item.get('IDuser'), 'Ημερομηνία': item.get('date'), 'Επώνυμο': item.get('last_name'),'Όνομα': item.get('first_name'), 'Ωράριο': item.get('wrario'), 'Τμήμα': item.get('department'),'Ειδικότητα': item.get('relationType')})
    eventLogger(request,info="Χρήστης εκτύπωσε ωράρια προσωπικού excel")
    wb.save(response)
    return response
       

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/
    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)
    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
    return path

        
@login_required()
@admin_required      
def synchronizeData(request):
    #global conn
    eventLogger(request,info="Χρήστης πάτησε συγχρονισμό χρηστών")
    devices=Devices.objects.all()
    for clock in devices:
        logger.error(clock)
        logger.error("----------------------------------")
        #  logger.error(deviceip)
        zk = ZK(clock.device_ip, port=clock.device_port, timeout=5, password=0,
                force_udp=False, ommit_ping=False)
        #CheckDevices(request)
        try:
            # connect to device
            conn = zk.connect()
            conn.disable_device()
            users = conn.get_users()#user of device
            # logger.error(users)
            deviceUsersList = []
            databaseUsersList = []
            dbUsers=Users.objects.order_by('id')
            i=0
            for user in users:
                # tmpstr = "['" + str(user.uid) + "', '" + str(user.name) + "'," + \
                #     " '0'" + ", '" + str(user.user_id) + \
                #     "', " + "'None', 'None', 'None']"
                # tmpsplitname = str(user.name).split()
                tmpstr = str(user.uid)+','+ str(user.name) + ','+ str(user.user_id) + ',' + str(user.card) 
                deviceUsersList.append(tmpstr)
                logger.error("deviceUser: "+tmpstr)
                #logger.error(tmpstr)
                # sheet1.write(i, 1, user.uid)
                # sheet1.write(i, 2, user.name)
                # sheet1.write(i, 3, user.privilege)
                # sheet1.write(i, 4, user.password)
                # sheet1.write(i, 5, user.group_id)
                # sheet1.write(i, 6, user.user_id)
                i=i+1
           
            for item in dbUsers:
                databaseUsersList.append(str(item.id)+","+ item.username +"," +str(item.device_card_id )+ "," + str(item.device_card_number))
                printdbUser=str(item.id)+","+ item.username +"," +str(item.device_card_id )+ "," + str(item.device_card_number)
                logger.error("databaseUser: "+printdbUser)
            #logger.error(databaseUsersList)
            #logger.error(
                #"*****up-databaseUsers**********************down-deviceUsers************************")
            #logger.error(deviceUsersList)
            
            newtodel=[]
            for delUser in deviceUsersList:
                # logger.error(newuser)
                if(str(delUser) not in databaseUsersList):
                    newtodel.append(delUser)                     
            res2 = []
            for i in newtodel:
                if i not in res2:
                    res2.append(i)       
            for i in res2:
                #logger.error(i)
                i = str(i).replace("'", "")
                i = str(i).replace("[", "")
                i = str(i).replace("]", "")
                newusertodel = str(i).split(',')
                logger.error("delete"+i)
                conn.delete_user(uid=int(newusertodel[0]),user_id=str(newusertodel[2]))
            newtoadd = []

            for newuser in databaseUsersList:
                if(str(newuser) not in deviceUsersList):
                    newtoadd.append(newuser)
            res = []
            for i in newtoadd:
                if i not in res:
                    res.append(i)
            
            for i in res:
                #logger.error(i)
                i = str(i).replace("'", "")
                i = str(i).replace("[", "")
                i = str(i).replace("]", "")
                newusertoadd = str(i).split(',')
                logger.error("OKKK"+i)
                conn.set_user(uid=int(newusertoadd[0]), name=str(newusertoadd[1]), privilege='user', password='', group_id='', user_id=str(newusertoadd[2]),card=str(newusertoadd[3]))
            conn.enable_device()
            conn.disconnect()
            messages.success(request,clock.device_location+' συγχρονίστηκε επιτυχώς')
        except Exception as e:
            print("Process terminate1 : {}".format(e))
            messages.error(request,clock.device_location+' συσκευή δεν συνδέθηκε')
            return redirect('users')
    return redirect('users')
           

@login_required()
def usersAttendance(request):
    if "GET" == request.method:
        yesterday=str(date.today()-timedelta(days=1))
        departments_list=Departments.objects.all().order_by('id')
        queryShowDep={"id":'',"department_name":''}
        global summaryShowDep
        global usersAtt
        summaryShowDep=[]
        print("membersDep")
        print(DepForMembers(request))
        try:
            for dep in DepForMembers(request):#departments_list: 
                queryShowDep['department_name']=dep['department_name']
                queryShowDep['id']=dep['id']
                summaryShowDep.append(queryShowDep.copy())
                queryShowDep.clear()  
        except Exception as e:
            print('dep loop not found due to deletions')      
        # queryShowDep['id']=Departments.objects.count()+1
        # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        # summaryShowDep.append(queryShowDep.copy())
        # queryShowDep.clear()
        usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
        eventLogger(request,info="Χρήστης μπήκε στις παρουσίες προσωπικού")
        return render(request, 'usersAttendance.html', {'myDateMax': yesterday,'departments':summaryShowDep,'Users':usersAtt})
    else:#when post method, real print is called
        yesterday=str(date.today()-timedelta(days=1))
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        departments_list=Departments.objects.all().order_by('id')
        myDateS = request.POST.get('startMyDate')
        myDateE = request.POST.get('endMyDate')
        myDepID = request.POST.get('dep_id')
        myUserID = request.POST.get('user_id')
        if myUserID:
            return usersAttendanceforUsers(request,myUserID,myDateS,myDateE)
        try:#get dep
            dep=Departments.objects.get(id=myDepID).department_name
            theDep=Departments.objects.get(id=myDepID).id
        except Exception as e:
            dep='ΧΩΡΙΣ ΤΜΗΜΑ'
            theDep=Departments.objects.count()+1
        if myDateS =='':#get dates
            myDateS=date.today()-timedelta(days=1)
            myDateS = myDateS.strftime("%Y-%m-%d")
        myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
        if myDateE =='':
            myDateE=date.today()-timedelta(days=1)
            myDateE = myDateE.strftime("%Y-%m-%d")
        myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
        dbUsers=Users.objects.order_by('last_name')
        d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
        d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
        if d1>d2 :#check date,start<end
            messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη τις δεύτερης")
            return redirect('usersAttendance')
        summaryDep=[]
        queryDep={'DepName':"",'DepParent':"",'DepID':""}#organize the deps
        if Staff_department_info.objects.filter(department_id=theDep).exclude(department_id=1):#take chosen dep,also child,except forea
            queryDep['DepName']=dep
            queryDep['DepParent']=Departments.objects.get(id=theDep).parent_id
            queryDep['DepID']=theDep
            summaryDep.append(queryDep.copy())
            queryDep.clear()
        for i in range (1,Departments.objects.count()+1,1):#aquire deps list,dimos has all,mpampas 1-6,child alone
            try:
                if theDep==1:#dimos all
                    if Staff_department_info.objects.filter(department_id=i):
                        queryDep['DepName']=Departments.objects.get(id=i).department_name
                        queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                        queryDep['DepID']=Departments.objects.get(id=i).id
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                    if Departments.objects.count()==i:#without(last loop,append to dimos deps),dimos has the xwris tmima
                        queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                        queryDep['DepParent']="None"
                        queryDep['DepID']=Departments.objects.count()+1
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                elif Departments.objects.get(id=i).parent_id==theDep and Staff_department_info.objects.filter(department_id=i) :#mpampas
                    queryDep['DepName']=Departments.objects.get(id=i).department_name
                    queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                    queryDep['DepID']=Departments.objects.get(id=i).id
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
                elif theDep==i+1 and dep=='ΧΩΡΙΣ ΤΜΗΜΑ':#without
                    queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDep['DepParent']="None"
                    queryDep['DepID']=theDep
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
            except Exception as e:
                print('dep loop not found due to deletions')               
        queryDay={'day':""}
        queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': ""}
        flagHrms=False
        try:#hrms connection
            if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                c = conn.cursor()
                flagHrms=True
            else:
                messages.warning(request,"Hrms δεν συνδέθηκε")
                flagHrms=False
        except cx_Oracle.DatabaseError as e: 
            print("error save one hrms connections", e)
        summaryQueryDict=[]
        summaryDays=[]
        print("db--querries")
        for i in range((d2 - d1).days + 1):#check every day in that range
            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
            queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
            print(queryDay['day'])
            summaryDays.append(queryDay.copy())
            queryDay.clear()
            print("membersUser")
            print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                try:# get hrms data
                    if flagHrms:
                        if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                            queryDict['Hrms']='Σαβ/Κυριακο'
                        locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                        oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                        #print("oraDate:"+oraDate)
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                        for row in c:
                            #print(row[12])
                            queryDict['Hrms']=row[12]
                    else:
                        #queryDict['Hrms']='----'
                        print('hrms not connected')
                    
                except Exception as e:
                    print("Process terminate hrms : {}".format(e))
                for item in Holidays.objects.all():
                    if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                        print('holiday1')
                        if not dbu['works_on_holidays']:
                            print('holiday2')
                            queryDict['Hrms']=item.description  
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                        print('holiday3')
                        queryDict['Hrms']=item.description 
                #categorize users in dep
                for sumDep in summaryDep:
                    myDepID=int(sumDep['DepID'])
                    if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu['user_card']).count()<1:#without dep
                        queryDict['first_name']=dbu['first_name']
                        queryDict['last_name']=dbu['last_name']
                        queryDict['fathers_name']=dbu['fathers_name']
                        queryDict['user_card']=dbu['user_card']
                        queryDict['department'] = sumDep['DepName']
                        queryDict['Role']="-"
                        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                        try:# check user att without dep
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                            qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0]
                            for attR in q1:
                                queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='----' #den exei
                                    queryDict['should_work_hours']='----' #den exei
                                    queryDict['wrario']='----' #den exei
                                else: #2 χτυπηματα 
                                    queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                    queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']='----'#den exei
                                    queryDict['should_work_hours']='----'#den exei
                                    queryDict['wrario']='----'#den exei
                                queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                        except Exception as e:
                            print("#no attendance--without dep : {}".format(e))
                            #no attendance
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours_in_range']='----'
                            queryDict['worked_hours']='----'
                            queryDict['should_work_hours']='----'
                            queryDict['wrario']='----'
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                    elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID): #has dep  
                        staff=Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID).first() 
                        if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)): #show dep if only on duty range of time
                            # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                            #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                            # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                            #     queryDict['Hrms']='δεν άρχισε ακόμα'
                                #check if user works that day of the week
                            if (d1 + timedelta(days=i)).weekday()==0:#monday
                                if staff.Monday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                                if staff.Tuesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                                if staff.Wednesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==3:#thursday
                                if staff.Thursday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==4:#Friday
                                if staff.Friday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==5:#saturday
                                if staff.Saturday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==6:#sunday
                                if staff.Sunday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                            if Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=False):
                                try:# no spasto, no double dep
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                                    qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0]
                                    for attR in q1: 
                                        queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                        queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                        queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                        queryDict['wrario']=attR.wrario
                                        if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα' 
                                        else:# 2 χτυπήματα(κανονικά) dep:  
                                            queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                            queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=attR.worked_hours_in_range.strftime('%H:%M:%S')
                                        summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()                    
                                except Exception as e:#no attendance
                                    print("#no attendance has dep : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()   
                                    
                            elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=True):
                                try:# spasto
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['device_card_number']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).first()
                                    qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0] 
                                    queryDict['day']=q1.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                                    queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=q1.wrario
                                    if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    else:# 2 χτυπήματα(κανονικά) dep:  
                                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                        queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2 
                                        if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                            queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        else:
                                            queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                        if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        else:
                                            queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                            queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S')
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()       
                                except Exception as e:#no attendance spasto
                                    print("#no attendance has dep spasto : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    summaryQueryDict.append(queryDict.copy())#show 2 prints
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                                    queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2)                                        
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()             
        print("---------")
        print(summaryQueryDict)
        print(summaryDays)
        print(summaryDep)
        flagUserAtt=0 
        eventLogger(request,info="Χρήστης αναζήτισε παρουσίες προσωπικού με τμήμα")    
        return render(request, 'usersAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'dep':dep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt})

@login_required()    
def usersAttendanceforUsers(request,myUserID,myDateS,myDateE):
    yesterday=str(date.today()-timedelta(days=1))
    departments_list=Departments.objects.all().order_by('id')
    queryShowDep={"id":'',"department_name":''}
    global summaryShowDep
    global usersAtt
    summaryShowDep=[]
    print("membersDep")
    print(DepForMembers(request))
    try:
        for dep in DepForMembers(request):#departments_list: 
            queryShowDep['department_name']=dep['department_name']
            queryShowDep['id']=dep['id']
            summaryShowDep.append(queryShowDep.copy())
            queryShowDep.clear()  
    except Exception as e:
        print('dep loop not found due to deletions')      
    # queryShowDep['id']=Departments.objects.count()+1
    # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
    # summaryShowDep.append(queryShowDep.copy())
    # queryShowDep.clear()
    usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
    if myDateS =='':#get dates
        myDateS=date.today()-timedelta(days=1)
        myDateS = myDateS.strftime("%Y-%m-%d")
    myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
    if myDateE =='':
        myDateE=date.today()-timedelta(days=1)
        myDateE = myDateE.strftime("%Y-%m-%d")
    myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
    dbu=Users.objects.get(id=int(myUserID))
    myUser=dbu.first_name+" "+dbu.last_name+" του "+str(dbu.fathers_name)
    d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
    d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
    if d1>d2 :#check date,start<end
        messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη τις δεύτερης")
        return redirect('usersAttendance')
    DepList=Staff_department_info.objects.filter(staff_card=dbu.device_card_number).values_list('department_id',flat=True)
    summaryDep=Departments.objects.filter(id__in=DepList)
    summaryDepTemp=''
    summaryDepTempID=''
    if not summaryDep:
        summaryDepTemp={'id':Departments.objects.count()+1,'department_name':"ΧΩΡΙΣ ΤΜΗΜΑ"}
        summaryDepTempID=summaryDepTemp['id']
    queryDay={'day':""}
    queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': ""}
    flagHrms=False
    try:#hrms connection
        if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
            myOra=Industry.objects.order_by('industry_settings_created_date')[0]
            comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
            #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
            conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
            c = conn.cursor()
            flagHrms=True
        else:
            messages.warning(request,"Hrms δεν συνδέθηκε")
            flagHrms=False
    except cx_Oracle.DatabaseError as e: 
        print("error save one hrms connections", e)
    summaryQueryDict=[]
    summaryDays=[]
    print("db--querries")
    for i in range((d2 - d1).days + 1):#check every day in that range
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
        print(queryDay['day'])
        summaryDays.append(queryDay.copy())
        queryDay.clear()
        
        try:# get hrms data
            if flagHrms:
                if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                    queryDict['Hrms']='Σαβ/Κυριακο'
                locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                #print("oraDate:"+oraDate)
                c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu.hrms_id)+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                for row in c:
                    #print(row[12])
                    queryDict['Hrms']=row[12]
            else:
                #queryDict['Hrms']='----'
                print('hrms not connected')
            
        except Exception as e:
            print("Process terminate hrms : {}".format(e))
        for item in Holidays.objects.all():
            if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                print('holiday1')
                if not dbu.works_on_holidays:
                    print('holiday2')
                    queryDict['Hrms']=item.description             
        for item in Staff_holidays.objects.filter(staff_card=dbu.device_card_number):        
            if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                print('holiday3')
                queryDict['Hrms']=item.description
        if summaryDepTempID==Departments.objects.count()+1:
            myDepID=summaryDepTemp['id']
            if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu.device_card_number).count()<1:#without dep
                queryDict['first_name']=dbu.first_name
                queryDict['last_name']=dbu.last_name
                queryDict['fathers_name']=dbu.fathers_name
                queryDict['user_card']=dbu.device_card_number
                queryDict['department'] = summaryDepTemp['department_name']
                queryDict['Role']="-"
                locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                try:# check user att without dep
                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).order_by('id')
                    qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0]
                    for attR in q1:
                        queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                        if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                            queryDict['worked_hours']='ελλιπές χτύπημα'
                            queryDict['worked_hours_in_range']='----' #den exei
                            queryDict['should_work_hours']='----' #den exei
                            queryDict['wrario']='----' #den exei
                        else: #2 χτυπηματα 
                            queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                            queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                            queryDict['worked_hours_in_range']='----'#den exei
                            queryDict['should_work_hours']='----'#den exei
                            queryDict['wrario']='----'#den exei
                        queryDict['day']=attR.day.strftime('%A %d %B %Y')
                        summaryQueryDict.append(queryDict.copy())
                    queryDict.clear()
                except Exception as e:
                    print("#no attendance--without dep : {}".format(e))
                    #no attendance
                    queryDict['Lattendance_time']='----'
                    queryDict['Fattendance_time']='----'
                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                    queryDict['worked_hours_in_range']='----'
                    queryDict['worked_hours']='----'
                    queryDict['should_work_hours']='----'
                    queryDict['wrario']='----'
                    summaryQueryDict.append(queryDict.copy())
                    queryDict.clear()
        for sumDep in summaryDep:
            myDepID=sumDep.id
            if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID): #has dep  
                staff=Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID).first()
                if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                    # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                    #         queryDict['Hrms']='τέλος περιόδου εργασίας'
                    # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                    #     queryDict['Hrms']='δεν άρχισε ακόμα'
                    #     #check if user works that day of the week
                    if (d1 + timedelta(days=i)).weekday()==0:#monday
                        if staff.Monday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                        if staff.Tuesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                        if staff.Wednesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==3:#thursday
                        if staff.Thursday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==4:#Friday
                        if staff.Friday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==5:#saturday
                        if staff.Saturday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==6:#sunday
                        if staff.Sunday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                    if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=False):
                        try:# no spasto, no double dep
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] = sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).order_by('id')
                            qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0]
                            for attR in q1:
                                queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                queryDict['wrario']=attR.wrario
                                if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα' 
                                else:# 2 χτυπήματα(κανονικά) dep:  
                                    queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                    queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']=attR.worked_hours_in_range.strftime('%H:%M:%S')
                                summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()                 
                        except Exception as e:#no attendance
                            print("#no attendance has dep : {}".format(e)) 
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()           
                    elif Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=True):
                        try:# spasto
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] =sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).first()
                            qcheck=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card'])[0] 
                            queryDict['day']=q1.day.strftime('%A %d %B %Y')
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                            queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                            queryDict['wrario']=q1.wrario
                            if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                            else:# 2 χτυπήματα(κανονικά) dep:  
                                queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2 
                                if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                    queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                else:
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                else:
                                    queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                    queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S')
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()    
                        except Exception as e:#no attendance spasto
                            print("#no attendance has dep spasto : {}".format(e)) 
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                            queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                            summaryQueryDict.append(queryDict.copy())#show 2 prints
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                            queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2)                            
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                        
    print("---------")
    print(summaryQueryDict)
    print(summaryDays)
    print(summaryDep)
    flagUserAtt=1
    array=[]
    if summaryDep:
        pass
    else:
        array.append(summaryDepTemp)
        summaryDep=array 
    eventLogger(request,info="Χρήστης αναζήτισε παρουσίες προσωπικού με χρήστη")       
    return render(request, 'usersAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt,'myUser':myUser})
                 

@login_required()
def usersHalfAttendance(request):
    if "GET" == request.method:
        yesterday=str(date.today()-timedelta(days=1))
        departments_list=Departments.objects.all().order_by('id')
        queryShowDep={"id":'',"department_name":''}
        global summaryShowDep
        global usersAtt
        summaryShowDep=[]
        print("membersDep")
        print(DepForMembers(request))
        try:
            for dep in DepForMembers(request):#departments_list: 
                queryShowDep['department_name']=dep['department_name']
                queryShowDep['id']=dep['id']
                summaryShowDep.append(queryShowDep.copy())
                queryShowDep.clear()  
        except Exception as e:
            print('dep loop not found due to deletions')      
        # queryShowDep['id']=Departments.objects.count()+1
        # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        # summaryShowDep.append(queryShowDep.copy())
        # queryShowDep.clear()
        usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
        eventLogger(request,info="Χρήστης μπήκε στις ημιτελείς παρουσίες χρηστών")
        return render(request, 'usersHalfAttendance.html', {'myDateMax': yesterday,'departments':summaryShowDep,'Users':usersAtt})
    else:#when post method, real print is called
        yesterday=str(date.today()-timedelta(days=1))
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        departments_list=Departments.objects.all().order_by('id')
        myDateS = request.POST.get('startMyDate')
        myDateE = request.POST.get('endMyDate')
        myDepID = request.POST.get('dep_id')
        myUserID = request.POST.get('user_id')
        if myUserID:
            return usersHalfAttendanceforUsers(request,myUserID,myDateS,myDateE)
        try:#get dep
            dep=Departments.objects.get(id=myDepID).department_name
            theDep=Departments.objects.get(id=myDepID).id
        except Exception as e:
            dep='ΧΩΡΙΣ ΤΜΗΜΑ'
            theDep=Departments.objects.count()+1
        if myDateS =='':#get dates
            myDateS=date.today()-timedelta(days=1)
            myDateS = myDateS.strftime("%Y-%m-%d")
        myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
        if myDateE =='':
            myDateE=date.today()-timedelta(days=1)
            myDateE = myDateE.strftime("%Y-%m-%d")
        myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
        dbUsers=Users.objects.order_by('last_name')
        d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
        d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
        if d1>d2 :#check date,start<end
            messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
            return redirect('usersHalfAttendance')
        summaryDep=[]
        queryDep={'DepName':"",'DepParent':"",'DepID':""}#organize the deps
        if Staff_department_info.objects.filter(department_id=theDep).exclude(department_id=1):#take chosen dep,also child,except forea
            queryDep['DepName']=dep
            queryDep['DepParent']=Departments.objects.get(id=theDep).parent_id
            queryDep['DepID']=theDep
            summaryDep.append(queryDep.copy())
            queryDep.clear()
        for i in range (1,Departments.objects.count()+1,1):#aquire deps list,dimos has all,mpampas 1-6,child alone
            try:
                if theDep==1:#dimos all
                    if Staff_department_info.objects.filter(department_id=i):
                        queryDep['DepName']=Departments.objects.get(id=i).department_name
                        queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                        queryDep['DepID']=Departments.objects.get(id=i).id
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                    if Departments.objects.count()==i:#without(last loop,append to dimos deps),dimos has the xwris tmima
                        queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                        queryDep['DepParent']="None"
                        queryDep['DepID']=Departments.objects.count()+1
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                elif Departments.objects.get(id=i).parent_id==theDep and Staff_department_info.objects.filter(department_id=i) :#mpampas
                    queryDep['DepName']=Departments.objects.get(id=i).department_name
                    queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                    queryDep['DepID']=Departments.objects.get(id=i).id
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
                elif theDep==i+1 and dep=='ΧΩΡΙΣ ΤΜΗΜΑ':#without
                    queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDep['DepParent']="None"
                    queryDep['DepID']=theDep
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
            except Exception as e:
                print('dep loop not found due to deletions')               
        queryDay={'day':""}
        queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': "", 'id':""}
        flagHrms=False
        try:#hrms connection
            if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                c = conn.cursor()
                flagHrms=True
            else:
                messages.warning(request,"Hrms δεν συνδέθηκε")
                flagHrms=False
        except cx_Oracle.DatabaseError as e: 
            print("error save one hrms connections", e)
        summaryQueryDict=[]
        summaryDays=[]
        print("db--querries")
        for i in range((d2 - d1).days + 1):#check every day in that range
            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
            queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
            print(queryDay['day'])
            summaryDays.append(queryDay.copy())
            queryDay.clear()
            print("membersUser")
            print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                myHrmsTemp=''
                try:# get hrms data
                    if flagHrms:
                        if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                            queryDict['Hrms']='Σαβ/Κυριακο'
                        locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                        oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                        #print("oraDate:"+oraDate)
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                        for row in c:
                            #print(row[12])
                            queryDict['Hrms']=row[12]
                            myHrmsTemp=row[12]
                    else:
                        #queryDict['Hrms']='----'
                        print('hrms not connected')
                    
                except Exception as e:
                    print("Process terminate hrms : {}".format(e))
                for item in Holidays.objects.all():
                    if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                        print('holiday1')
                        if not dbu['works_on_holidays']:
                            print('holiday2')
                            queryDict['Hrms']=item.description
                            myHrmsTemp=item.description  
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                        print('holiday3')
                        queryDict['Hrms']=item.description
                        myHrmsTemp=item.description 
                #categorize users in dep
                for sumDep in summaryDep:
                    myDepID=int(sumDep['DepID'])
                    if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu['user_card']).count()<1:#without dep
                        #here was querydict first_name to role
                        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                        try:# check user att without dep
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                            for attR in q1:
                                queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role']="-"
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='----' #den exei
                                    queryDict['should_work_hours']='----' #den exei
                                    queryDict['wrario']='----' #den exei
                                    queryDict['id']=attR.id
                                    queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                    queryDict['Hrms']=myHrmsTemp
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()
                        except Exception as e:
                            print("#no attendance--without dep : {}".format(e))
                            #no attendance    
                        #summaryQueryDict.append(queryDict.copy())
                        #queryDict.clear()
                    elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID): #has dep  
                        staff=Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID).first()
                        if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                            # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                            #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                            # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                            #     queryDict['Hrms']='δεν άρχισε ακόμα'
                                #check if user works that day of the week
                            if (d1 + timedelta(days=i)).weekday()==0:#monday
                                if staff.Monday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                                if staff.Tuesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                                if staff.Wednesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==3:#thursday
                                if staff.Thursday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==4:#Friday
                                if staff.Friday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==5:#saturday
                                if staff.Saturday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==6:#sunday
                                if staff.Sunday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                            if  Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=False):
                                try:# no spasto, no double dep
                                    #here was querydict first_name to role
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                                    for attR in q1:
                                        if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict['first_name']=dbu['first_name']
                                            queryDict['last_name']=dbu['last_name']
                                            queryDict['fathers_name']=dbu['fathers_name']
                                            queryDict['user_card']=dbu['user_card']
                                            queryDict['department'] = sumDep['DepName']
                                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                            queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                            queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                            queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                            queryDict['wrario']=attR.wrario
                                            queryDict['id']=attR.id
                                            queryDict['Hrms']=myHrmsTemp
                                            summaryQueryDict.append(queryDict.copy())
                                            queryDict.clear()                     
                                except Exception as e:#no attendance
                                    print("#no attendance has dep : {}".format(e)) 
                    
                            elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=True):
                                try:# spasto
                                    #here was querydict first_name to role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).first()
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role 
                                    queryDict['day']=q1.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                                    queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=q1.wrario
                                    queryDict['id']=q1.id 
                                    if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    else:# 2 χτυπήματα(κανονικά) dep:  
                                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                        queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2 
                                        if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                            queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        else:
                                            queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                        if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'      
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()               
                                except Exception as e:#no attendance spasto
                                    print("#no attendance has dep spasto : {}".format(e))                           
                              
        print("---------")
        print(summaryQueryDict)
        print(summaryDays)
        print(summaryDep)
        flagUserAtt=0  
        eventLogger(request,info="Χρήστης αναζήτισε ημιτελείς παρουσίες προσωπικού με τμήμα")   
        return render(request, 'usersHalfAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'dep':dep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt})

@admin_required    
@login_required()
def usersHalfAttendanceEdit(request):
    if "POST" == request.method: 
        myId = request.POST.get('id')
        apoxwrisi = request.POST.get('apoxwrisi')
        afiksi2 = request.POST.get('afiksi2')
        apoxwrisi2 = request.POST.get('apoxwrisi2')
        attRR=Staff_attendance_rearranged_report.objects.get(id=int(myId))
        next = request.POST.get('next')
    if parse_time(apoxwrisi)<=attRR.attendance_time_in:
        messages.warning(request,"άφιξη μεγαλύτερη-ίση από αποχώριση")
        return redirect('usersHalfAttendance')
    if afiksi2 and apoxwrisi2:
        if parse_time(apoxwrisi2)<=parse_time(afiksi2):
            messages.warning(request,"άφιξη2 μεγαλύτερη-ίση από αποχώριση2")
            return redirect('usersHalfAttendance')
    if afiksi2 and not apoxwrisi2:
        messages.warning(request,"δεν δώθηκε αποχώριση2")
        return redirect('usersHalfAttendance')
    if apoxwrisi2 and not afiksi2:
        messages.warning(request,"δεν δώθηκε άφιξη2")
        return redirect('usersHalfAttendance')
    wh=str(timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0)-timedelta(hours=attRR.attendance_time_in.hour,minutes=attRR.attendance_time_in.minute,seconds=attRR.attendance_time_in.second))
    
    ds1=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work.minute,seconds=0)
    ds2=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work.minute,seconds=0)
    print("ela1")
    if ds1>timedelta(hours=attRR.attendance_time_in.hour,minutes=attRR.attendance_time_in.minute,seconds=attRR.attendance_time_in.second):
        rs1=ds1
    else:
        rs1=timedelta(hours=attRR.attendance_time_in.hour,minutes=attRR.attendance_time_in.minute,seconds=attRR.attendance_time_in.second)
    print("ela2")
    if ds2<timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0):
        rs2=ds2
    else:
        rs2=timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0)
    print("ela3")
    if rs2-rs1<timedelta(0):
        whir=time(0,0,0)
    else:
        whir=str(rs2-rs1)
        
    s=Staff_attendance_rearranged_report.objects.filter(id=int(myId)).update(attendance_time_out=parse_time(apoxwrisi),worked_hours=wh,worked_hours_in_range=whir)
    
    if Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().spasto and afiksi2 and apoxwrisi2:
        wh2=str(timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0)-timedelta(hours=attRR.attendance_time_in2.hour,minutes=attRR.attendance_time_in2.minute,seconds=attRR.attendance_time_in2.second))
    
        ds11=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work2.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work2.minute,seconds=0)
        ds22=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work2.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work2.minute,seconds=0)
        print("ela1")
        if ds11>timedelta(hours=attRR.attendance_time_in2.hour,minutes=attRR.attendance_time_in2.minute,seconds=attRR.attendance_time_in2.second):
            rs11=ds11
        else:
            rs11=timedelta(hours=attRR.attendance_time_in2.hour,minutes=attRR.attendance_time_in2.minute,seconds=attRR.attendance_time_in2.second)
        print("ela2")
        if ds22<timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0):
            rs22=ds22
        else:
            rs22=timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0)
        print("ela3")
        if rs22-rs11<timedelta(0):
            whir2=time(0,0,0)
        else:
            whir2=str(rs2-rs1)
        
        s=Staff_attendance_rearranged_report.objects.filter(id=int(myId)).update(attendance_time_in2=parse_time(afiksi2),attendance_time_out2=parse_time(apoxwrisi2),worked_hours2=wh2,worked_hours_in_range2=whir2)
    
    eventLogger(request,info="Χρήστης ανανέωσε ημιτελής παρουσία χρήστη με τιμές: "+str(s))     
    messages.success(request,"ημιτελείς παρουσία χρήστη ανανεώθηκε")
    return redirect(next)
 

 
@login_required()    
def usersHalfAttendanceforUsers(request,myUserID,myDateS,myDateE):
    yesterday=str(date.today()-timedelta(days=1))
    departments_list=Departments.objects.all().order_by('id')
    queryShowDep={"id":'',"department_name":''}
    global summaryShowDep
    global usersAtt
    summaryShowDep=[]
    print("membersDep")
    print(DepForMembers(request))
    try:
        for dep in DepForMembers(request):#departments_list: 
            queryShowDep['department_name']=dep['department_name']
            queryShowDep['id']=dep['id']
            summaryShowDep.append(queryShowDep.copy())
            queryShowDep.clear()  
    except Exception as e:
        print('dep loop not found due to deletions')      
    # queryShowDep['id']=Departments.objects.count()+1
    # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
    # summaryShowDep.append(queryShowDep.copy())
    # queryShowDep.clear()
    usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
    if myDateS =='':#get dates
        myDateS=date.today()-timedelta(days=1)
        myDateS = myDateS.strftime("%Y-%m-%d")
    myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
    if myDateE =='':
        myDateE=date.today()-timedelta(days=1)
        myDateE = myDateE.strftime("%Y-%m-%d")
    myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
    dbu=Users.objects.get(id=int(myUserID))
    myUser=dbu.first_name+" "+dbu.last_name+" του "+str(dbu.fathers_name)
    d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
    d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
    if d1>d2 :#check date,start<end
        messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
        return redirect('usersHalfAttendance')
    DepList=Staff_department_info.objects.filter(staff_card=dbu.device_card_number).values_list('department_id',flat=True)
    summaryDep=Departments.objects.filter(id__in=DepList)
    summaryDepTemp=''
    summaryDepTempID=''
    if not summaryDep:
        summaryDepTemp={'id':Departments.objects.count()+1,'department_name':"ΧΩΡΙΣ ΤΜΗΜΑ"}
        summaryDepTempID=summaryDepTemp['id']
    queryDay={'day':""}
    queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': "",'id':""}
    flagHrms=False
    try:#hrms connection
        if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
            myOra=Industry.objects.order_by('industry_settings_created_date')[0]
            comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
            #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
            conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
            c = conn.cursor()
            flagHrms=True
        else:
            messages.warning(request,"Hrms δεν συνδέθηκε")
            flagHrms=False
    except cx_Oracle.DatabaseError as e: 
        print("error save one hrms connections", e)
    summaryQueryDict=[]
    summaryDays=[]
    print("db--querries")
    for i in range((d2 - d1).days + 1):#check every day in that range
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
        print(queryDay['day'])
        summaryDays.append(queryDay.copy())
        queryDay.clear()
        myHrmsTemp=''
        try:# get hrms data
            if flagHrms:
                if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                    queryDict['Hrms']='Σαβ/Κυριακο'
                locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                #print("oraDate:"+oraDate)
                c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu.hrms_id)+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                for row in c:
                    #print(row[12])
                    queryDict['Hrms']=row[12]
                    myHrmsTemp=[12]
            else:
                #queryDict['Hrms']='----'
                print('hrms not connected')
            
        except Exception as e:
            print("Process terminate hrms : {}".format(e))
        for item in Holidays.objects.all():
            if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                print('holiday1')
                if not dbu.works_on_holidays:
                    print('holiday2')
                    queryDict['Hrms']=item.description
                    myHrmsTemp=item.description             
        for item in Staff_holidays.objects.filter(staff_card=dbu.device_card_number):        
            if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                print('holiday3')
                queryDict['Hrms']=item.description
                myHrmsTemp=item.description
        if summaryDepTempID==Departments.objects.count()+1:
            myDepID=summaryDepTemp['id']
            if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu.device_card_number).count()<1:#without dep
                try:# check user att without dep
                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).order_by('id')
                    for attR in q1:
                        queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                        if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                            queryDict['worked_hours']='ελλιπές χτύπημα'
                            queryDict['worked_hours_in_range']='----' #den exei
                            queryDict['should_work_hours']='----' #den exei
                            queryDict['wrario']='----' #den exei
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] = summaryDepTemp['department_name']
                            queryDict['Role']="-"
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            queryDict['day']=attR.day.strftime('%A %d %B %Y')
                            queryDict['id']=attR.id
                            queryDict['Hrms']=myHrmsTemp
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                except Exception as e:
                    print("#no attendance--without dep : {}".format(e))
                    #no attendance 
        for sumDep in summaryDep:
            myDepID=sumDep.id  
            if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID): #has dep  
                staff=Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID).first()
                if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                    # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                    #         queryDict['Hrms']='τέλος περιόδου εργασίας'
                    # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                    #     queryDict['Hrms']='δεν άρχισε ακόμα'
                        #check if user works that day of the week
                    if (d1 + timedelta(days=i)).weekday()==0:#monday
                        if staff.Monday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                        if staff.Tuesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                        if staff.Wednesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==3:#thursday
                        if staff.Thursday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==4:#Friday
                        if staff.Friday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==5:#saturday
                        if staff.Saturday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==6:#sunday
                        if staff.Sunday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                    if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=False):
                        try:# no spasto, no double dep
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).order_by('id')
                            for attR in q1: 
                                if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    queryDict['first_name']=dbu.first_name
                                    queryDict['last_name']=dbu.last_name
                                    queryDict['fathers_name']=dbu.fathers_name
                                    queryDict['user_card']=dbu.device_card_number
                                    queryDict['department'] = sumDep.department_name
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8") 
                                    queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                    queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=attR.wrario
                                    queryDict['id']=attR.id
                                    queryDict['Hrms']=myHrmsTemp
                                    summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()        
                        except Exception as e:#no attendance  
                            print("#no attendance has dep without sp-dd : {}".format(e))      
                    elif Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=True):
                        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                        try:# spasto
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).first() 
                            queryDict['day']=q1.day.strftime('%A %d %B %Y')
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                            queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                            queryDict['wrario']=q1.wrario
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] =sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            queryDict['id']=q1.id
                            
                            if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                            else:# 2 χτυπήματα(κανονικά) dep:  
                                queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2 
                                if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                    queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                else:
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()            
                        except Exception as e:#no attendance spasto
                            print("#no attendance has dep spasto : {}".format(e))                    
                        
    print("---------")
    print(summaryQueryDict)
    print(summaryDays)
    print(summaryDep)
    flagUserAtt=1 
    array=[]
    if summaryDep:
        pass
    else:
        array.append(summaryDepTemp)
        summaryDep=array 
    eventLogger(request,info="Χρήστης αναζήτισε ημιτελής παρουσίες προσωπικού με χρήστη")       
    return render(request, 'usersHalfAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt,'myUser':myUser})
    
    
@login_required()
def usersNoAttendance(request):
    if "GET" == request.method:
        yesterday=str(date.today()-timedelta(days=1))
        departments_list=Departments.objects.all().order_by('id')
        queryShowDep={"id":'',"department_name":''}
        global summaryShowDep
        global usersAtt
        summaryShowDep=[]
        print("membersDep")
        print(DepForMembers(request))
        try:
            for dep in DepForMembers(request):#departments_list: 
                queryShowDep['department_name']=dep['department_name']
                queryShowDep['id']=dep['id']
                summaryShowDep.append(queryShowDep.copy())
                queryShowDep.clear()  
        except Exception as e:
            print('dep loop not found due to deletions')      
        # queryShowDep['id']=Departments.objects.count()+1
        # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        # summaryShowDep.append(queryShowDep.copy())
        # queryShowDep.clear()
        usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
        eventLogger(request,info="Χρήστης μπήκε στις απουσίες χρηστών")
        return render(request, 'usersNoAttendance.html', {'myDateMax': yesterday,'departments':summaryShowDep,'Users':usersAtt})
    else:#when post method, real print is called
        yesterday=str(date.today()-timedelta(days=1))
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        departments_list=Departments.objects.all().order_by('id')
        myDateS = request.POST.get('startMyDate')
        myDateE = request.POST.get('endMyDate')
        myDepID = request.POST.get('dep_id')
        myUserID = request.POST.get('user_id')
        myHrmsTemp=''
        if myUserID:
            return usersNoAttendanceforUsers(request,myUserID,myDateS,myDateE)
        try:#get dep
            dep=Departments.objects.get(id=myDepID).department_name
            theDep=Departments.objects.get(id=myDepID).id
        except Exception as e:
            dep='ΧΩΡΙΣ ΤΜΗΜΑ'
            theDep=Departments.objects.count()+1
        if myDateS =='':#get dates
            myDateS=date.today()-timedelta(days=1)
            myDateS = myDateS.strftime("%Y-%m-%d")
        myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
        if myDateE =='':
            myDateE=date.today()-timedelta(days=1)
            myDateE = myDateE.strftime("%Y-%m-%d")
        myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
        dbUsers=Users.objects.order_by('last_name')
        d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
        d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
        if d1>d2 :#check date,start<end
            messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
            return redirect('usersNoAttendance')
        summaryDep=[]
        queryDep={'DepName':"",'DepParent':"",'DepID':""}#organize the deps
        if Staff_department_info.objects.filter(department_id=theDep).exclude(department_id=1):#take chosen dep,also child,except forea
            queryDep['DepName']=dep
            queryDep['DepParent']=Departments.objects.get(id=theDep).parent_id
            queryDep['DepID']=theDep
            summaryDep.append(queryDep.copy())
            queryDep.clear()
        for i in range (1,Departments.objects.count()+1,1):#aquire deps list,dimos has all,mpampas 1-6,child alone
            try:
                if theDep==1:#dimos all
                    if Staff_department_info.objects.filter(department_id=i):
                        queryDep['DepName']=Departments.objects.get(id=i).department_name
                        queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                        queryDep['DepID']=Departments.objects.get(id=i).id
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                    if Departments.objects.count()==i:#without(last loop,append to dimos deps),dimos has the xwris tmima
                        queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                        queryDep['DepParent']="None"
                        queryDep['DepID']=Departments.objects.count()+1
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                elif Departments.objects.get(id=i).parent_id==theDep and Staff_department_info.objects.filter(department_id=i) :#mpampas
                    queryDep['DepName']=Departments.objects.get(id=i).department_name
                    queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                    queryDep['DepID']=Departments.objects.get(id=i).id
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
                elif theDep==i+1 and dep=='ΧΩΡΙΣ ΤΜΗΜΑ':#without
                    queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDep['DepParent']="None"
                    queryDep['DepID']=theDep
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
            except Exception as e:
                print('dep loop not found due to deletions')               
        queryDay={'day':"",'dayClean':""}
        queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': ""}
        flagHrms=False
        try:#hrms connection
            if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                c = conn.cursor()
                flagHrms=True
            else:
                messages.warning(request,"Hrms δεν συνδέθηκε")
                flagHrms=False
        except cx_Oracle.DatabaseError as e: 
            print("error save one hrms connections", e)
        summaryQueryDict=[]
        summaryDays=[]
        print("db--querries")
        for i in range((d2 - d1).days + 1):#check every day in that range
            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
            queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
            queryDay['dayClean']=str(d1 + timedelta(days=i))
            print(queryDay['day'])
            print(queryDay['dayClean'])
            summaryDays.append(queryDay.copy())
            queryDay.clear()
            print("membersUser")
            print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                try:# get hrms data
                    if flagHrms:
                        if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                            queryDict['Hrms']='Σαβ/Κυριακο'
                        locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                        oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                        #print("oraDate:"+oraDate)
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                        for row in c:
                            #print(row[12])
                            queryDict['Hrms']=row[12]
                            myHrmsTemp=row[12]
                    else:
                        #queryDict['Hrms']='----'
                        print('hrms not connected')
                    
                except Exception as e:
                    print("Process terminate hrms : {}".format(e))
                for item in Holidays.objects.all():
                    if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                        print('holiday1')
                        if not dbu['works_on_holidays']:
                            print('holiday2')
                            queryDict['Hrms']=item.description
                            myHrmsTemp=item.description  
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                        print('holiday3')
                        queryDict['Hrms']=item.description
                        myHrmsTemp=item.description 
                #categorize users in dep
                for sumDep in summaryDep:
                    myDepID=int(sumDep['DepID'])
                    if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu['user_card']).count()<1:#without dep
                        queryDict['first_name']=dbu['first_name']
                        queryDict['last_name']=dbu['last_name']
                        queryDict['fathers_name']=dbu['fathers_name']
                        queryDict['user_card']=dbu['user_card']
                        queryDict['department'] = sumDep['DepName']
                        queryDict['Role']="-"
                        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                        try:# check user att without dep
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).first()
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name
                            if q1.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='----' #den exei
                                queryDict['should_work_hours']='----' #den exei
                                queryDict['wrario']='----' #den exei
                                queryDict.clear()
                            else: #2 χτυπηματα 
                                queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name
                                queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                queryDict['worked_hours_in_range']='----'#den exei
                                queryDict['should_work_hours']='----'#den exei
                                queryDict['wrario']='----'#den exei
                                queryDict.clear()
                            queryDict['day']=q1.day.strftime('%A %d %B %Y')
                        except Exception as e:
                            print("#no attendance--without dep : {}".format(e))
                            #no attendance
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours_in_range']='----'
                            queryDict['worked_hours']='----'
                            queryDict['should_work_hours']='----'
                            queryDict['wrario']='----'
                        summaryQueryDict.append(queryDict.copy())
                        queryDict.clear()
                    elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID): #has dep  
                        staff=Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID).first()
                        if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                            # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                            #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                            # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                            #     queryDict['Hrms']='δεν άρχισε ακόμα'
                                #check if user works that day of the week
                            if (d1 + timedelta(days=i)).weekday()==0:#monday
                                if staff.Monday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                                if staff.Tuesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                                if staff.Wednesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==3:#thursday
                                if staff.Thursday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==4:#Friday
                                if staff.Friday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==5:#saturday
                                if staff.Saturday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==6:#sunday
                                if staff.Sunday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                            if Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=False):
                                try:# no spasto, no double dep
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).first() 
                                    queryDict['day']=q1.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name
                                    queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=q1.wrario
                                    if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        queryDict.clear()
                                    else:# 2 χτυπήματα(κανονικά) dep:  
                                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name
                                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                        queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S') 
                                        queryDict.clear()                
                                except Exception as e:#no attendance
                                    print("#no attendance has dep : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    
                            elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=True):
                                try:# spasto
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).first() 
                                    queryDict['day']=q1.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                                    queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=q1.wrario
                                    if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        queryDict.clear()
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        queryDict.clear()
                                    else:# 2 χτυπήματα(κανονικά) dep:  
                                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                        queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                        queryDict.clear()
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2 
                                        if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                            queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict.clear()
                                        else:
                                            queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                            queryDict.clear()
                                        if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict.clear()
                                        else:
                                            queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                            queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S')  
                                            queryDict.clear()  
                                except Exception as e:#no attendance spasto
                                    print("#no attendance has dep spasto : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    summaryQueryDict.append(queryDict.copy())#show 2 prints
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                                    queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2)                            
                                
                            summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                              
        print("---------")
        print(summaryQueryDict)
        print(summaryDays)
        print(summaryDep)
        flagUserAtt=0
        device=Devices.objects.all()
        eventLogger(request,info="Χρήστης αναζήτισε απουσίες προσωπικού με τμήμα")     
        return render(request, 'usersNoAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'dep':dep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt,'Devices':device})


@admin_required    
@login_required()
def usersNoAttendanceEdit(request):
    if "POST" == request.method: 
        myId = request.POST.get('id')#user_card
        myDay=request.POST.get('day')
        myDeviceId = request.POST.get('device')
        myDevice=Devices.objects.get(id=myDeviceId)
        afiksi = request.POST.get('afiksi')
        apoxwrisi = request.POST.get('apoxwrisi')
        afiksi2 = request.POST.get('afiksi2')
        apoxwrisi2 = request.POST.get('apoxwrisi2')
        if Staff_department_info.objects.filter(staff_card=int(myId)):
            staff=Staff_department_info.objects.filter(staff_card=int(myId)).first()
        else:
            staff=None
        next = request.POST.get('next')
        u=Users.objects.get(device_card_number=myId)
        if parse_time(apoxwrisi)<=parse_time(afiksi):
            messages.warning(request,"άφιξη μεγαλύτερη-ίση από αποχώριση")
            return redirect(next)
        if afiksi2 and apoxwrisi2:
            if parse_time(apoxwrisi2)<=parse_time(afiksi2):
                messages.warning(request,"άφιξη2 μεγαλύτερη-ίση από αποχώριση2")
                return redirect(next)
            if parse_time(afiksi2)<=parse_time(afiksi):
                messages.warning(request,"άφιξη μεγαλύτερη-ίση από άφιξη2")
                return redirect(next)
        if afiksi2 and not apoxwrisi2:
            messages.warning(request,"δεν δώθηκε αποχώριση2")
            return redirect(next)
        if apoxwrisi2 and not afiksi2:
            messages.warning(request,"δεν δώθηκε άφιξη2")
            return redirect(next)
        wh=str(timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0)-timedelta(hours=parse_time(afiksi).hour,minutes=parse_time(afiksi).minute,seconds=0))
    
        if staff:#has dep
            ds1=timedelta(hours=Staff_department_info.objects.filter(staff_card=myId).first().start_of_work.hour,minutes=Staff_department_info.objects.filter(staff_card=myId).first().start_of_work.minute,seconds=0)
            ds2=timedelta(hours=Staff_department_info.objects.filter(staff_card=myId).first().end_of_work.hour,minutes=Staff_department_info.objects.filter(staff_card=myId).first().end_of_work.minute,seconds=0)
            print("ela1")
            if ds1>timedelta(hours=parse_time(afiksi).hour,minutes=parse_time(afiksi).minute,seconds=0):
                rs1=ds1
            else:
                rs1=timedelta(hours=parse_time(afiksi).hour,minutes=parse_time(afiksi).minute,seconds=0)
            print("ela2")
            if ds2<timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0):
                rs2=ds2
            else:
                rs2=timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0)
            print("ela3")
            if rs2-rs1<timedelta(0):
                whir=time(0,0,0)
            else:
                whir=str(rs2-rs1)
            
            
            s=Staff_attendance_rearranged_report.objects.create(staff_card=u.device_card_number,username=u.username,device_name=myDevice,attendance_time_in=parse_time(afiksi),attendance_time_out=parse_time(apoxwrisi),day=myDay,wrario=str(staff.start_of_work)+"-"+str(staff.end_of_work),should_work_hours=str(ds2-ds1),worked_hours=wh,worked_hours_in_range=whir,department_name=Departments.objects.get(id=staff.department_id).department_name)
        else:#no dep
            s=Staff_attendance_rearranged_report.objects.create(staff_card=u.device_card_number,username=u.username,device_name=myDevice,attendance_time_in=parse_time(afiksi),attendance_time_out=parse_time(apoxwrisi),day=myDay,wrario=time(0,0,0),should_work_hours=time(0,0,0),worked_hours=wh,worked_hours_in_range=time(0,0,0),department_name="ΧΩΡΙΣ ΤΜΗΜΑ")
        
    
        if staff.spasto and afiksi2 and apoxwrisi2:
            wh2=str(timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0)-timedelta(hours=parse_time(afiksi2).hour,minutes=parse_time(afiksi2).minute,seconds=0))
        
            ds11=timedelta(hours=Staff_department_info.objects.filter(staff_card=myId).first().start_of_work2.hour,minutes=Staff_department_info.objects.filter(staff_card=myId).first().start_of_work2.minute,seconds=0)
            ds22=timedelta(hours=Staff_department_info.objects.filter(staff_card=myId).first().end_of_work2.hour,minutes=Staff_department_info.objects.filter(staff_card=myId).first().end_of_work2.minute,seconds=0)
            print("ela1")
            if ds11>timedelta(hours=parse_time(afiksi2).hour,minutes=parse_time(afiksi2).minute,seconds=0):
                rs11=ds11
            else:
                rs11=timedelta(hours=parse_time(afiksi2).hour,minutes=parse_time(afiksi2).minute,seconds=0)
            print("ela2")
            if ds22<timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0):
                rs22=ds22
            else:
                rs22=timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0)
            print("ela3")
            if rs22-rs11<timedelta(0):
                whir2=time(0,0,0)
            else:
                whir2=str(rs2-rs1)
            
            s=Staff_attendance_rearranged_report.objects.create(staff_card=u.device_card_number,username=u.username,device_name=myDevice,attendance_time_in=parse_time(afiksi),attendance_time_out=parse_time(apoxwrisi),day=myDay,wrario=str(staff.start_of_work)+"-"+str(staff.end_of_work),should_work_hours=str(ds2-ds1),worked_hours=wh,worked_hours_in_range=whir,department_name=Departments.objects.get(id=staff.department_id).department_name,attendance_time_in2=parse_time(afiksi2),attendance_time_out2=parse_time(apoxwrisi2),worked_hours2=wh2,worked_hours_in_range2=whir2,should_work_hours2=str(ds22-ds11),wrario2=str(staff.start_of_work2)+"-"+str(staff.end_of_work2))
    
    eventLogger(request,info="Χρήστης ανανέωσε απουσία χρήστη με τιμές: "+str(s))     
    messages.success(request,"απουσία χρήστη ανανεώθηκε")
    return redirect(next)

@login_required()
def usersNoAttendanceforUsers(request,myUserID,myDateS,myDateE):
    yesterday=str(date.today()-timedelta(days=1))
    departments_list=Departments.objects.all().order_by('id')
    queryShowDep={"id":'',"department_name":''}
    global summaryShowDep
    global usersAtt
    summaryShowDep=[]
    print("membersDep")
    print(DepForMembers(request))
    try:
        for dep in DepForMembers(request):#departments_list: 
            queryShowDep['department_name']=dep['department_name']
            queryShowDep['id']=dep['id']
            summaryShowDep.append(queryShowDep.copy())
            queryShowDep.clear()  
    except Exception as e:
        print('dep loop not found due to deletions')      
    # queryShowDep['id']=Departments.objects.count()+1
    # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
    # summaryShowDep.append(queryShowDep.copy())
    # queryShowDep.clear()
    usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
    if myDateS =='':#get dates
        myDateS=date.today()-timedelta(days=1)
        myDateS = myDateS.strftime("%Y-%m-%d")
    myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
    if myDateE =='':
        myDateE=date.today()-timedelta(days=1)
        myDateE = myDateE.strftime("%Y-%m-%d")
    myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
    dbu=Users.objects.get(id=int(myUserID))
    myUser=dbu.first_name+" "+dbu.last_name+" του "+str(dbu.fathers_name)
    d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
    d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
    if d1>d2 :#check date,start<end
        messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
        return redirect('usersNoAttendance')
    DepList=Staff_department_info.objects.filter(staff_card=dbu.device_card_number).values_list('department_id',flat=True)
    summaryDep=Departments.objects.filter(id__in=DepList)
    summaryDepTemp=""
    summaryDepTempID=""
    summaryDepTempName=""
    if not summaryDep:
        summaryDepTemp={'id':Departments.objects.count()+1,'department_name':"ΧΩΡΙΣ ΤΜΗΜΑ"}
        summaryDepTempName=summaryDepTemp['department_name']
        summaryDepTempID=summaryDepTemp['id']
    queryDay={'day':"",'dayClean':""}
    queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': ""}
    flagHrms=False
    try:#hrms connection
        if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
            myOra=Industry.objects.order_by('industry_settings_created_date')[0]
            comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
            #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
            conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
            c = conn.cursor()
            flagHrms=True
        else:
            messages.warning(request,"Hrms δεν συνδέθηκε")
            flagHrms=False
    except cx_Oracle.DatabaseError as e: 
        print("error save one hrms connections", e)
    summaryQueryDict=[]
    summaryDays=[]
    print("db--querries")
    for i in range((d2 - d1).days + 1):#check every day in that range
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
        print(queryDay['day'])
        queryDay['dayClean']=str(d1 + timedelta(days=i))
        summaryDays.append(queryDay.copy())
        queryDay.clear()
        
        try:# get hrms data
            if flagHrms:
                if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                    queryDict['Hrms']='Σαβ/Κυριακο'
                locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                #print("oraDate:"+oraDate)
                c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu.hrms_id)+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                for row in c:
                    #print(row[12])
                    queryDict['Hrms']=row[12]
            else:
                #queryDict['Hrms']='----'
                print('hrms not connected')
            
        except Exception as e:
            print("Process terminate hrms : {}".format(e))
        for item in Holidays.objects.all():
            if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                print('holiday1')
                if not dbu.works_on_holidays:
                    print('holiday2')
                    queryDict['Hrms']=item.description             
        for item in Staff_holidays.objects.filter(staff_card=dbu.device_card_number):        
            if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                print('holiday3')
                queryDict['Hrms']=item.description
        if summaryDepTempID==Departments.objects.count()+1:
            myDepID=summaryDepTemp['id']
            if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu.device_card_number).count()<1:#without dep
                queryDict['first_name']=dbu.first_name
                queryDict['last_name']=dbu.last_name
                queryDict['fathers_name']=dbu.fathers_name
                queryDict['user_card']=dbu.device_card_number
                queryDict['department'] = summaryDepTemp['department_name']
                queryDict['Role']="-"
                locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                try:# check user att without dep
                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).first()
                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name
                    if q1.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                        queryDict['worked_hours']='ελλιπές χτύπημα'
                        queryDict['worked_hours_in_range']='----' #den exei
                        queryDict['should_work_hours']='----' #den exei
                        queryDict['wrario']='----' #den exei
                        queryDict.clear()
                    else: #2 χτυπηματα 
                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name
                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                        queryDict['worked_hours_in_range']='----'#den exei
                        queryDict['should_work_hours']='----'#den exei
                        queryDict['wrario']='----'#den exei
                        queryDict.clear()
                    queryDict['day']=q1.day.strftime('%A %d %B %Y')
                except Exception as e:
                    print("#no attendance--without dep : {}".format(e))
                    #no attendance
                    queryDict['Lattendance_time']='----'
                    queryDict['Fattendance_time']='----'
                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                    queryDict['worked_hours_in_range']='----'
                    queryDict['worked_hours']='----'
                    queryDict['should_work_hours']='----'
                    queryDict['wrario']='----'
                summaryQueryDict.append(queryDict.copy())
                queryDict.clear()
        for sumDep in summaryDep:
            myDepID=sumDep.id
            if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID): #has dep  
                staff=Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID).first()
                if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                    # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                    #         queryDict['Hrms']='τέλος περιόδου εργασίας'
                    # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                    #     queryDict['Hrms']='δεν άρχισε ακόμα'
                        #check if user works that day of the week
                    if (d1 + timedelta(days=i)).weekday()==0:#monday
                        if staff.Monday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                        if staff.Tuesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                        if staff.Wednesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==3:#thursday
                        if staff.Thursday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==4:#Friday
                        if staff.Friday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==5:#saturday
                        if staff.Saturday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==6:#sunday
                        if staff.Sunday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                    if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=False):
                        try:# no spasto, no double dep
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] = sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).first() 
                            queryDict['day']=q1.day.strftime('%A %d %B %Y')
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name
                            queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                            queryDict['wrario']=q1.wrario
                            if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                queryDict.clear() 
                            else:# 2 χτυπήματα(κανονικά) dep:  
                                queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name
                                queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')   
                                queryDict.clear()              
                        except Exception as e:#no attendance
                            print("#no attendance has dep : {}".format(e)) 
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    
                    elif Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=True):
                        try:# spasto
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] =sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).first() 
                            queryDict['day']=q1.day.strftime('%A %d %B %Y')
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                            queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                            queryDict['wrario']=q1.wrario
                            if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                queryDict.clear()
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                queryDict.clear()
                            else:# 2 χτυπήματα(κανονικά) dep:  
                                queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                queryDict.clear()
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2 
                                queryDict.clear()
                                if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                    queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    queryDict.clear()
                                else:
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                    queryDict.clear()
                                if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    queryDict.clear()
                                else:
                                    queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                    queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S') 
                                    queryDict.clear()   
                        except Exception as e:#no attendance spasto
                            print("#no attendance has dep spasto : {}".format(e)) 
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                            queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                            summaryQueryDict.append(queryDict.copy())#show 2 prints
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                            queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2)                            
                            
                summaryQueryDict.append(queryDict.copy())
                queryDict.clear()
                        
    print("---------")
    print(summaryQueryDict)
    print(summaryDays)
    print(summaryDep)
    flagUserAtt=1
    device=Devices.objects.all()
    array=[]
    if summaryDep:
        pass
    else:
        array.append(summaryDepTemp)
        summaryDep=array 
    eventLogger(request,info="Χρήστης αναζήτισε απουσίες προσωπικού με τμήμα")       
    return render(request, 'usersNoAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt,'Devices':device,'myUser':myUser})


@login_required()
def usersFullAttendance(request):
    if "GET" == request.method:
        yesterday=str(date.today()-timedelta(days=1))
        departments_list=Departments.objects.all().order_by('id')
        queryShowDep={"id":'',"department_name":''}
        global summaryShowDep
        global usersAtt
        summaryShowDep=[]
        print("membersDep")
        print(DepForMembers(request))
        try:
            for dep in DepForMembers(request):#departments_list: 
                queryShowDep['department_name']=dep['department_name']
                queryShowDep['id']=dep['id']
                summaryShowDep.append(queryShowDep.copy())
                queryShowDep.clear()  
        except Exception as e:
            print('dep loop not found due to deletions')      
        # queryShowDep['id']=Departments.objects.count()+1
        # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
        # summaryShowDep.append(queryShowDep.copy())
        # queryShowDep.clear()
        usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
        eventLogger(request,info="Χρήστης μπήκε στις πλήρης παρουσίες προσωπικού")
        return render(request, 'usersFullAttendance.html', {'myDateMax': yesterday,'departments':summaryShowDep,'Users':usersAtt})
    else:#when post method, real print is called
        yesterday=str(date.today()-timedelta(days=1))
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        departments_list=Departments.objects.all().order_by('id')
        myDateS = request.POST.get('startMyDate')
        myDateE = request.POST.get('endMyDate')
        myDepID = request.POST.get('dep_id')
        myUserID = request.POST.get('user_id')
        if myUserID:
            return usersFullAttendanceforUsers(request,myUserID,myDateS,myDateE)
        try:#get dep
            dep=Departments.objects.get(id=myDepID).department_name
            theDep=Departments.objects.get(id=myDepID).id
        except Exception as e:
            dep='ΧΩΡΙΣ ΤΜΗΜΑ'
            theDep=Departments.objects.count()+1
        if myDateS =='':#get dates
            myDateS=date.today()-timedelta(days=1)
            myDateS = myDateS.strftime("%Y-%m-%d")
        myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
        if myDateE =='':
            myDateE=date.today()-timedelta(days=1)
            myDateE = myDateE.strftime("%Y-%m-%d")
        myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
        dbUsers=Users.objects.order_by('last_name')
        d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
        d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
        if d1>d2 :#check date,start<end
            messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
            return redirect('usersFullAttendance')
        summaryDep=[]
        queryDep={'DepName':"",'DepParent':"",'DepID':""}#organize the deps
        if Staff_department_info.objects.filter(department_id=theDep).exclude(department_id=1):#take chosen dep,also child,except forea
            queryDep['DepName']=dep
            queryDep['DepParent']=Departments.objects.get(id=theDep).parent_id
            queryDep['DepID']=theDep
            summaryDep.append(queryDep.copy())
            queryDep.clear()
        for i in range (1,Departments.objects.count()+1,1):#aquire deps list,dimos has all,mpampas 1-6,child alone
            try:
                if theDep==1:#dimos all
                    if Staff_department_info.objects.filter(department_id=i):
                        queryDep['DepName']=Departments.objects.get(id=i).department_name
                        queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                        queryDep['DepID']=Departments.objects.get(id=i).id
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                    if Departments.objects.count()==i:#without(last loop,append to dimos deps),dimos has the xwris tmima
                        queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                        queryDep['DepParent']="None"
                        queryDep['DepID']=Departments.objects.count()+1
                        summaryDep.append(queryDep.copy())
                        queryDep.clear()
                elif Departments.objects.get(id=i).parent_id==theDep and Staff_department_info.objects.filter(department_id=i) :#mpampas
                    queryDep['DepName']=Departments.objects.get(id=i).department_name
                    queryDep['DepParent']=Departments.objects.get(id=i).parent_id
                    queryDep['DepID']=Departments.objects.get(id=i).id
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
                elif theDep==i+1 and dep=='ΧΩΡΙΣ ΤΜΗΜΑ':#without
                    queryDep['DepName']='ΧΩΡΙΣ ΤΜΗΜΑ'
                    queryDep['DepParent']="None"
                    queryDep['DepID']=theDep
                    summaryDep.append(queryDep.copy())
                    queryDep.clear()
            except Exception as e:
                print('dep loop not found due to deletions')               
        queryDay={'day':""}
        queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': "",'id':""}
        flagHrms=False
        try:#hrms connection
            if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
                myOra=Industry.objects.order_by('industry_settings_created_date')[0]
                comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
                #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
                conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
                c = conn.cursor()
                flagHrms=True
            else:
                messages.warning(request,"Hrms δεν συνδέθηκε")
                flagHrms=False
        except cx_Oracle.DatabaseError as e: 
            print("error save one hrms connections", e)
        summaryQueryDict=[]
        summaryDays=[]
        print("db--querries")
        for i in range((d2 - d1).days + 1):#check every day in that range
            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
            queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
            print(queryDay['day'])
            summaryDays.append(queryDay.copy())
            queryDay.clear()
            print("membersUser")
            print(UsersForMembers(request))
            for dbu in UsersForMembers(request):#dbUsers:#loop for attendances begins
                myHrmsTemp=''
                try:# get hrms data
                    if flagHrms:
                        if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                            queryDict['Hrms']='Σαβ/Κυριακο'
                        locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                        oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                        #print("oraDate:"+oraDate)
                        c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu['hrms_id'])+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                        for row in c:
                            #print(row[12])
                            queryDict['Hrms']=row[12]
                            myHrmsTemp=row[12]
                    else:
                        #queryDict['Hrms']='----'
                        print('hrms not connected')
                    
                except Exception as e:
                    print("Process terminate hrms : {}".format(e))
                for item in Holidays.objects.all():
                    if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                        print('holiday1')
                        if not dbu['works_on_holidays']:
                            print('holiday2')
                            queryDict['Hrms']=item.description
                            myHrmsTemp=item.description  
                for item in Staff_holidays.objects.filter(staff_card=dbu['user_card']):        
                    if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                        print('holiday3')
                        queryDict['Hrms']=item.description
                        myHrmsTemp=item.description  
                #categorize users in dep
                for sumDep in summaryDep:
                    myDepID=int(sumDep['DepID'])
                    if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu['user_card']).count()<1:#without dep
                        queryDict['first_name']=dbu['first_name']
                        queryDict['last_name']=dbu['last_name']
                        queryDict['fathers_name']=dbu['fathers_name']
                        queryDict['user_card']=dbu['user_card']
                        queryDict['department'] = sumDep['DepName']
                        queryDict['Role']="-"
                        queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                        try:# check user att without dep
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                            for attR in q1:
                                queryDict['id']=attR.id
                                queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='----' #den exei
                                    queryDict['should_work_hours']='----' #den exei
                                    queryDict['wrario']='----' #den exei
                                    queryDict.clear()
                                else: #2 χτυπηματα 
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role']="-"
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                        
                                    queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                    queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']='----'#den exei
                                    queryDict['should_work_hours']='----'#den exei
                                    queryDict['wrario']='----'#den exei
                                    queryDict['Hrms']=myHrmsTemp
                                    summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()
                        except Exception as e:
                            print("#no attendance--without dep : {}".format(e))
                            #no attendance
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours_in_range']='----'
                            queryDict['worked_hours']='----'
                            queryDict['should_work_hours']='----'
                            queryDict['wrario']='----'
                            queryDict.clear()
                        #summaryQueryDict.append(queryDict.copy())
                        #queryDict.clear()
                    elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID): #has dep  
                        staff=Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID).first()
                        if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                            # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                            #     queryDict['Hrms']='τέλος περιόδου εργασίας'
                            # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                            #     queryDict['Hrms']='δεν άρχισε ακόμα'
                                #check if user works that day of the week
                            if (d1 + timedelta(days=i)).weekday()==0:#monday
                                if staff.Monday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                                if staff.Tuesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                                if staff.Wednesday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==3:#thursday
                                if staff.Thursday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==4:#Friday
                                if staff.Friday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==5:#saturday
                                if staff.Saturday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                            if (d1 + timedelta(days=i)).weekday()==6:#sunday
                                if staff.Sunday:
                                    pass
                                else:
                                    pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                            if Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=False):
                                try:# no spasto, no double dep
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).order_by('id')
                                    for attR in q1:
                                        queryDict['id']=attR.id 
                                        queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                        queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                        queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                        queryDict['wrario']=attR.wrario
                                        queryDict['first_name']=dbu['first_name']
                                        queryDict['last_name']=dbu['last_name']
                                        queryDict['fathers_name']=dbu['fathers_name']
                                        queryDict['user_card']=dbu['user_card']
                                        queryDict['department'] = sumDep['DepName']
                                        queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                        queryDict['Hrms']=myHrmsTemp
                                        if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict.clear() 
                                        else:# 2 χτυπήματα(κανονικά) dep:  
                                            queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                            queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=attR.worked_hours_in_range.strftime('%H:%M:%S')
                                            summaryQueryDict.append(queryDict.copy())
                                    queryDict.clear()                 
                                except Exception as e:#no attendance
                                    print("#no attendance has dep : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    queryDict.clear()
                                    
                            elif Staff_department_info.objects.filter(staff_card=dbu['user_card'],department_id=myDepID,spasto=True):
                                try:# spasto
                                    queryDict['first_name']=dbu['first_name']
                                    queryDict['last_name']=dbu['last_name']
                                    queryDict['fathers_name']=dbu['fathers_name']
                                    queryDict['user_card']=dbu['user_card']
                                    queryDict['department'] = sumDep['DepName']
                                    queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu['user_card'],department_id=myDepID).role
                                    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu['user_card']).first() 
                                    queryDict['id']=q1.id
                                    queryDict['day']=q1.day.strftime('%A %d %B %Y')
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                                    queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                                    queryDict['wrario']=q1.wrario
                                    if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                        queryDict.clear()
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2
                                        queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                        queryDict['worked_hours']='ελλιπές χτύπημα'
                                        queryDict['worked_hours_in_range']='ελλιπές χτύπημα'   
                                    else:# 2 χτυπήματα(κανονικά) dep:  
                                        queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                        queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                        queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                        summaryQueryDict.append(queryDict.copy())#show 2 prints
                                        queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                        queryDict['wrario']=q1.wrario2 
                                        if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                            queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict.clear()
                                        else:
                                            queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                        if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                            queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                            queryDict['worked_hours']='ελλιπές χτύπημα'
                                            queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                            queryDict.clear()
                                        else:
                                            queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                            queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                            queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S')
                                            summaryQueryDict.append(queryDict.copy())
                                            queryDict.clear()    
                                except Exception as e:#no attendance spasto
                                    print("#no attendance has dep spasto : {}".format(e)) 
                                    queryDict['Lattendance_time']='----'
                                    queryDict['Fattendance_time']='----'
                                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                                    queryDict['worked_hours']='----'
                                    queryDict['worked_hours_in_range']='----'
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                                    queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                                    queryDict.clear()
                                    summaryQueryDict.append(queryDict.copy())#show 2 prints
                                    queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                                    queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2) 
                                    queryDict.clear()                           
                              
        print("---------")
        print(summaryQueryDict)
        print(summaryDays)
        print(summaryDep)
        flagUserAtt=0
        eventLogger(request,info="Χρήστης αναζήτισε πλήρης παρουσίες προσωπικού με τμήμα")     
        return render(request, 'usersFullAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'dep':dep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt})
 
@admin_required    
@login_required()
def usersFullAttendanceEdit(request):
    if "POST" == request.method: 
        myId = request.POST.get('id')
        afiksi = request.POST.get('afiksi')
        #print(afiksi)
        apoxwrisi = request.POST.get('apoxwrisi')
        afiksi2 = request.POST.get('afiksi2')
        apoxwrisi2 = request.POST.get('apoxwrisi2')
        attRR=Staff_attendance_rearranged_report.objects.get(id=int(myId))
        next = request.POST.get('next')
    if parse_time(apoxwrisi)<=parse_time(afiksi):
        messages.warning(request,"άφιξη μεγαλύτερη-ίση από αποχώριση")
        return redirect(next)
    if afiksi2 and apoxwrisi2:
        if parse_time(apoxwrisi2)<=parse_time(afiksi2):
            messages.warning(request,"άφιξη2 μεγαλύτερη-ίση από αποχώριση2")
            return redirect(next)
    if afiksi2 and not apoxwrisi2:
        messages.warning(request,"δεν δώθηκε αποχώριση2")
        return redirect(next)
    if apoxwrisi2 and not afiksi2:
        messages.warning(request,"δεν δώθηκε άφιξη2")
        return redirect(next)
    wh=str(timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0)-timedelta(hours=parse_time(afiksi).hour,minutes=parse_time(afiksi).minute,seconds=0))
    
    ds1=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work.minute,seconds=0)
    ds2=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work.minute,seconds=0)
    print("ela1")
    if ds1>timedelta(hours=parse_time(afiksi).hour,minutes=parse_time(afiksi).minute,seconds=0):
        rs1=ds1
    else:
        rs1=timedelta(hours=parse_time(afiksi).hour,minutes=parse_time(afiksi).minute,seconds=0)
    print("ela2")
    if ds2<timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0):
        rs2=ds2
    else:
        rs2=timedelta(hours=parse_time(apoxwrisi).hour,minutes=parse_time(apoxwrisi).minute,seconds=0)
    print("ela3")
    if rs2-rs1<timedelta(0):
        whir=time(0,0,0)
    else:
        whir=str(rs2-rs1)
        
    #print(parse_time(afiksi))   
    s=Staff_attendance_rearranged_report.objects.filter(id=int(myId)).update(attendance_time_in=parse_time(afiksi),attendance_time_out=parse_time(apoxwrisi),worked_hours=wh,worked_hours_in_range=whir)
    
    if Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().spasto and afiksi2 and apoxwrisi2:
        wh2=str(timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0)-timedelta(hours=attRR.attendance_time_in2.hour,minutes=attRR.attendance_time_in2.minute,seconds=attRR.attendance_time_in2.second))
    
        ds11=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work2.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().start_of_work2.minute,seconds=0)
        ds22=timedelta(hours=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work2.hour,minutes=Staff_department_info.objects.filter(staff_card=attRR.staff_card).first().end_of_work2.minute,seconds=0)
        print("ela1")
        if ds11>timedelta(hours=attRR.attendance_time_in2.hour,minutes=attRR.attendance_time_in2.minute,seconds=attRR.attendance_time_in2.second):
            rs11=ds11
        else:
            rs11=timedelta(hours=attRR.attendance_time_in2.hour,minutes=attRR.attendance_time_in2.minute,seconds=attRR.attendance_time_in2.second)
        print("ela2")
        if ds22<timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0):
            rs22=ds22
        else:
            rs22=timedelta(hours=parse_time(apoxwrisi2).hour,minutes=parse_time(apoxwrisi2).minute,seconds=0)
        print("ela3")
        if rs22-rs11<timedelta(0):
            whir2=time(0,0,0)
        else:
            whir2=str(rs2-rs1)
        
        s=Staff_attendance_rearranged_report.objects.filter(id=int(myId)).update(attendance_time_in2=parse_time(afiksi2),attendance_time_out2=parse_time(apoxwrisi2),worked_hours2=wh2,worked_hours_in_range2=whir2)
         
    messages.success(request,"πλήρης παρουσία χρήστη ανανεώθηκε με τιμές: "+str(s))
    eventLogger(request,info="Χρήστης ανανέωσε πλήρη παρουσία χρήστη")
    return redirect(next)

   
@login_required()
def usersFullAttendanceforUsers(request,myUserID,myDateS,myDateE):
    yesterday=str(date.today()-timedelta(days=1))
    departments_list=Departments.objects.all().order_by('id')
    queryShowDep={"id":'',"department_name":''}
    global summaryShowDep
    global usersAtt
    summaryShowDep=[]
    print("membersDep")
    print(DepForMembers(request))
    try:
        for dep in DepForMembers(request):#departments_list: 
            queryShowDep['department_name']=dep['department_name']
            queryShowDep['id']=dep['id']
            summaryShowDep.append(queryShowDep.copy())
            queryShowDep.clear()  
    except Exception as e:
        print('dep loop not found due to deletions')      
    # queryShowDep['id']=Departments.objects.count()+1
    # queryShowDep['department_name']='ΧΩΡΙΣ ΤΜΗΜΑ'
    # summaryShowDep.append(queryShowDep.copy())
    # queryShowDep.clear()
    usersAtt=UsersForMembers(request)#Users.objects.order_by('last_name')
    if myDateS =='':#get dates
        myDateS=date.today()-timedelta(days=1)
        myDateS = myDateS.strftime("%Y-%m-%d")
    myDate2s = datetime.strptime(myDateS, '%Y-%m-%d').strftime('%d/%m/%Y')
    if myDateE =='':
        myDateE=date.today()-timedelta(days=1)
        myDateE = myDateE.strftime("%Y-%m-%d")
    myDate2e = datetime.strptime(myDateE, '%Y-%m-%d').strftime('%d/%m/%Y')
    dbu=Users.objects.get(id=int(myUserID))
    myUser=dbu.last_name+" "+dbu.first_name+" του "+str(dbu.fathers_name)
    d2=datetime.strptime(myDate2e, '%d/%m/%Y').date()
    d1=datetime.strptime(myDate2s, '%d/%m/%Y').date()
    if d1>d2 :#check date,start<end
        messages.warning(request,"πρώτη ημερομηνία μεγαλύτερη της δεύτερης")
        return redirect('usersFullAttendance')
    DepList=Staff_department_info.objects.filter(staff_card=dbu.device_card_number).values_list('department_id',flat=True)
    summaryDep=Departments.objects.filter(id__in=DepList)
    summaryDepTemp=""
    summaryDepTempID=""
    summaryDepTempName=""
    if not summaryDep:
        summaryDepTemp={'id':Departments.objects.count()+1,'department_name':"ΧΩΡΙΣ ΤΜΗΜΑ"}
        summaryDepTempName=summaryDepTemp['department_name']
        summaryDepTempID=summaryDepTemp['id']
    queryDay={'day':""}
    queryDict= {'first_name': "",'last_name': "",'Role':"",'user_card':"",'fathers_name':"",'department':"",'Hrms':"", 'day':"",'should_work_hours':"",'worked_hours':"",'worked_hours_in_range':"",'wrario':"",
                        'Fattendance_time': "", 'Lattendance_time': "",'id':""}
    flagHrms=False
    try:#hrms connection
        if Industry.objects.order_by('industry_settings_created_date')[0].hrms_connect:
            myOra=Industry.objects.order_by('industry_settings_created_date')[0]
            comID=str(Industry.objects.order_by('industry_settings_created_date')[0].hrms_com_id)
            #conn = cx_Oracle.connect('SHR/SHR@192.168.10.17:1521/OTA')
            conn = cx_Oracle.connect(myOra.hrms_username+'/'+myOra.hrms_password+'@'+myOra.hrms_ip+':'+str(myOra.hrms_port)+'/'+myOra.hrms_service_name)
            c = conn.cursor()
            flagHrms=True
        else:
            messages.warning(request,"Hrms δεν συνδέθηκε")
            flagHrms=False
    except cx_Oracle.DatabaseError as e: 
        print("error save one hrms connections", e)
    summaryQueryDict=[]
    summaryDays=[]
    print("db--querries")
    for i in range((d2 - d1).days + 1):#check every day in that range
        locale.setlocale(locale.LC_ALL, "el_GR.utf8")
        queryDay['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
        print(queryDay['day'])
        summaryDays.append(queryDay.copy())
        queryDay.clear()
        myHrmsTemp=''
        try:# get hrms data
            if flagHrms:
                if (d1 + timedelta(days=i)).weekday()==5 or (d1 + timedelta(days=i)).weekday()==6:
                    queryDict['Hrms']='Σαβ/Κυριακο'
                locale.setlocale(locale.LC_ALL, "en_EN.utf8")
                oraDate=(d1 + timedelta(days=i)).strftime('%d %b %Y')
                #print("oraDate:"+oraDate)
                c.execute("""SELECT a.lev_com_id, a.lev_leave_id, a.lev_emp_id,a.lev_date_request, a.lev_type_period,a.lev_from_leave_date, a.lev_to_leave_date,a.lev_period,a.lev_lty_id3,b.lda_date,b.lda_type, b.lda_lty_id,c.lty_descr FROM tl_leaves a, tl_leave_days b, tl_leave_types c WHERE A.lev_com_id="""+comID+""" and A.lev_emp_id="""+str(dbu.hrms_id)+"""and B.lda_date=TO_DATE( '"""+oraDate+"""', 'DD MON YYYY' )  and a.lev_com_id=b.lda_com_id and a.lev_leave_id=b.lda_leave_id and a.lev_emp_id=b.lda_emp_id and b.lda_com_id=c.lty_com_id and b.lda_lty_id=c.lty_id """) 
                for row in c:
                    #print(row[12])
                    queryDict['Hrms']=row[12]
                    myHrmsTemp=row[12]
            else:
                #queryDict['Hrms']='----'
                print('hrms not connected')
            
        except Exception as e:
            print("Process terminate hrms : {}".format(e))
        for item in Holidays.objects.all():
            if item.date_from<=(d1 + timedelta(days=i))<=item.date_to: # is holiday and user not work on holidays
                print('holiday1')
                if not dbu.works_on_holidays:
                    print('holiday2')
                    queryDict['Hrms']=item.description 
                    myHrmsTemp=item.description            
        for item in Staff_holidays.objects.filter(staff_card=dbu.device_card_number):        
            if item.date_from<=pytz.utc.localize(datetime.combine((d1 + timedelta(days=i)),datetime.min.time()))<=item.date_to:# user has adeia
                print('holiday3')
                queryDict['Hrms']=item.description
                myHrmsTemp=item.description 
        if summaryDepTempID== Departments.objects.count()+1:   
            myDepID=summaryDepTemp['id']
            if myDepID==int(Departments.objects.count()+1) and Staff_department_info.objects.filter(staff_card=dbu.device_card_number).count()<1:#without dep
                queryDict['first_name']=dbu.first_name
                queryDict['last_name']=dbu.last_name
                queryDict['fathers_name']=dbu.fathers_name
                queryDict['user_card']=dbu.device_card_number
                queryDict['department'] = summaryDepTemp['department_name']
                queryDict['Role']="-"
                queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                try:# check user att without dep
                    q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).order_by('id')
                    for attR in q1:
                        queryDict['id']=attR.id
                        queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                        queryDict['Hrms']=myHrmsTemp
                        queryDict['first_name']=dbu.first_name
                        queryDict['last_name']=dbu.last_name
                        queryDict['fathers_name']=dbu.fathers_name
                        queryDict['user_card']=dbu.device_card_number
                        queryDict['department'] = summaryDepTemp['department_name']
                        queryDict['Role']="-"
                        queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                        if attR.attendance_time_out==time(0,0,0):#ελλιπες χτύπημα
                            queryDict['Lattendance_time']='ελλιπές χτύπημα'
                            queryDict['worked_hours']='ελλιπές χτύπημα'
                            queryDict['worked_hours_in_range']='----' #den exei
                            queryDict['should_work_hours']='----' #den exei
                            queryDict['wrario']='----' #den exei
                            queryDict.clear()
                        else: #2 χτυπηματα 
                            queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                            queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                            queryDict['worked_hours_in_range']='----'#den exei
                            queryDict['should_work_hours']='----'#den exei
                            queryDict['wrario']='----'#den exei
                            summaryQueryDict.append(queryDict.copy())
                    queryDict.clear()
                except Exception as e:
                    print("#no attendance--without dep : {}".format(e))
                    #no attendance
                    queryDict['Lattendance_time']='----'
                    queryDict['Fattendance_time']='----'
                    queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                    queryDict['worked_hours_in_range']='----'
                    queryDict['worked_hours']='----'
                    queryDict['should_work_hours']='----'
                    queryDict['wrario']='----'
                    queryDict.clear()     
        for sumDep in summaryDep:
            myDepID=sumDep.id
            if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID): #has dep  
                staff=Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID).first()
                if  staff.apply_to >= (d1 + timedelta(days=i)) and staff.apply_from <= (d1 + timedelta(days=i)):
                    # if staff.apply_to < (d1 + timedelta(days=i)):#has expired
                    #         queryDict['Hrms']='τέλος περιόδου εργασίας'
                    # if staff.apply_from > (d1 + timedelta(days=i)):#has not started
                    #     queryDict['Hrms']='δεν άρχισε ακόμα'
                        #check if user works that day of the week
                    if (d1 + timedelta(days=i)).weekday()==0:#monday
                        if staff.Monday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==1:#tuesday
                        if staff.Tuesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==2:#wednesday
                        if staff.Wednesday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==3:#thursday
                        if staff.Thursday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==4:#Friday
                        if staff.Friday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==5:#saturday
                        if staff.Saturday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                    if (d1 + timedelta(days=i)).weekday()==6:#sunday
                        if staff.Sunday:
                            pass
                        else:
                            pass#queryDict['Hrms']='Δεν εργάζεται αυτή την ημέρα'
                                    
                    if Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=False):
                        try:# no spasto, no double dep
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] = sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).order_by('id')
                            for attR in q1:
                                queryDict['id']=attR.id 
                                queryDict['day']=attR.day.strftime('%A %d %B %Y')
                                queryDict['Fattendance_time']=str(attR.attendance_time_in)+", "+attR.device_name
                                queryDict['should_work_hours']=attR.should_work_hours.strftime('%H:%M:%S')
                                queryDict['wrario']=attR.wrario
                               # queryDict['Hrms']=myHrmsTemp
                                queryDict['first_name']=dbu.first_name
                                queryDict['last_name']=dbu.last_name
                                queryDict['fathers_name']=dbu.fathers_name
                                queryDict['user_card']=dbu.device_card_number
                                queryDict['department'] = sumDep.department_name
                                queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                                if  attR.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    queryDict.clear() 
                                else:# 2 χτυπήματα(κανονικά) dep:  
                                    queryDict['Lattendance_time']=str(attR.attendance_time_out)+", "+attR.device_name
                                    queryDict['worked_hours']=attR.worked_hours.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']=attR.worked_hours_in_range.strftime('%H:%M:%S')
                                    summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()                 
                        except Exception as e:#no attendance
                            print("#no attendance has dep : {}".format(e)) 
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                            queryDict.clear()        
                    elif Staff_department_info.objects.filter(staff_card=dbu.device_card_number,department_id=myDepID,spasto=True):
                        try:# spasto
                            queryDict['first_name']=dbu.first_name
                            queryDict['last_name']=dbu.last_name
                            queryDict['fathers_name']=dbu.fathers_name
                            queryDict['user_card']=dbu.device_card_number
                            queryDict['department'] =sumDep.department_name
                            queryDict['Role'] =Staff_department_info.objects.get(staff_card=dbu.device_card_number,department_id=myDepID).role
                            locale.setlocale(locale.LC_ALL, "el_GR.utf8")
                            q1=Staff_attendance_rearranged_report.objects.filter(day=d1 + timedelta(days=i),staff_card=dbu.device_card_number).first() 
                            queryDict['id']=q1.id
                            queryDict['day']=q1.day.strftime('%A %d %B %Y')
                            queryDict['Fattendance_time']=str(q1.attendance_time_in)+", "+q1.device_name+" ,"+'σπαστό'
                            queryDict['should_work_hours']=q1.should_work_hours.strftime('%H:%M:%S')
                            queryDict['wrario']=q1.wrario
                            if  q1.attendance_time_out==time(0,0,0):# ελλιπές χτύπημα with dep spasto
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                queryDict.clear()
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2
                                queryDict['Lattendance_time']='ελλιπές χτύπημα'
                                queryDict['worked_hours']='ελλιπές χτύπημα'
                                queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                queryDict.clear()
                            else:# 2 χτυπήματα(κανονικά) dep:  
                                queryDict['Lattendance_time']=str(q1.attendance_time_out)+", "+q1.device_name+" ,"+'σπαστό'
                                queryDict['worked_hours']=q1.worked_hours.strftime('%H:%M:%S')
                                queryDict['worked_hours_in_range']=q1.worked_hours_in_range.strftime('%H:%M:%S')
                                summaryQueryDict.append(queryDict.copy())#show 2 prints
                                queryDict['should_work_hours']=q1.should_work_hours2.strftime('%H:%M:%S')
                                queryDict['wrario']=q1.wrario2 
                                if  q1.attendance_time_in2==time(0,0,0):#third hit miss
                                    queryDict['Fattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    queryDict.clear()
                                else:
                                    queryDict['Fattendance_time']=str(q1.attendance_time_in2)+", "+q1.device_name+" ,"+'σπαστό'
                                if q1.attendance_time_out2==time(0,0,0):#fourth hit miss
                                    queryDict['Lattendance_time']='ελλιπές χτύπημα'+" ,"+'σπαστό'
                                    queryDict['worked_hours']='ελλιπές χτύπημα'
                                    queryDict['worked_hours_in_range']='ελλιπές χτύπημα'
                                    queryDict.clear()
                                else:
                                    queryDict['Lattendance_time']=str(q1.attendance_time_out2)+", "+q1.device_name
                                    queryDict['worked_hours']=q1.worked_hours2.strftime('%H:%M:%S')
                                    queryDict['worked_hours_in_range']=q1.worked_hours_in_range2.strftime('%H:%M:%S')
                                    summaryQueryDict.append(queryDict.copy())
                            queryDict.clear()    
                        except Exception as e:#no attendance spasto
                            print("#no attendance has dep spasto : {}".format(e)) 
                            queryDict['Lattendance_time']='----'
                            queryDict['Fattendance_time']='----'
                            queryDict['day']=(d1 + timedelta(days=i)).strftime('%A %d %B %Y')
                            queryDict['worked_hours']='----'
                            queryDict['worked_hours_in_range']='----'
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work.hour,minutes=staff.end_of_work.minute)-timedelta(hours=staff.start_of_work.hour,minutes=staff.start_of_work.minute))
                            queryDict['wrario']=str(staff.start_of_work)+" "+str(staff.end_of_work)
                            queryDict.clear()
                            summaryQueryDict.append(queryDict.copy())#show 2 prints
                            queryDict['should_work_hours']=str(timedelta(hours=staff.end_of_work2.hour,minutes=staff.end_of_work2.minute)-timedelta(hours=staff.start_of_work2.hour,minutes=staff.start_of_work2.minute))
                            queryDict['wrario']=str(staff.start_of_work2)+" "+str(staff.end_of_work2)
                            queryDict.clear()                           
                        
    print("---------")
    print(summaryQueryDict)
    print(summaryDays)
    print(summaryDep)
    flagUserAtt=1
    array=[]
    if summaryDep:
        pass
    else:
        array.append(summaryDepTemp)
        summaryDep=array 
    eventLogger(request,info="Χρήστης αναζήτισε πλήρης παρουσίες προσωπικού με χρήστη")         
    return render(request, 'usersFullAttendance.html', {'fullattendaces': summaryQueryDict, 'myDateMax': yesterday,'departments':summaryShowDep,'date1':myDate2s,'date2':myDate2e,'SumDays':summaryDays,'SumDeps':summaryDep,'Users':usersAtt,'flagUserAtt':flagUserAtt,'myUser':myUser})