from django.urls import path
from .import viewsSeeders,viewsMain
from django.conf import settings
from django.conf.urls.static import static

#all the urls of bootstrap front-end and seeders, format=actual path,location of method,name alias as method called
urlpatterns = [
    path('', viewsMain.pagelogin,name='pagelogin'),
    path('welcome', viewsMain.welcome,name='welcome'),
    path('deviceSelect', viewsMain.deviceSelect,name='deviceSelect'),
    path('deviceData', viewsMain.deviceData,name='deviceData'),
    path('searchDevU', viewsMain.searchDevU,name='searchDevU'),
    path('searchDevAtt', viewsMain.searchDevAtt,name='searchDevAtt'),
    path('deviceAdd', viewsMain.deviceAdd,name='deviceAdd'),
    path('deviceDelete', viewsMain.deviceDelete,name='deviceDelete'),
    path('deviceClear', viewsMain.deviceClear,name='deviceClear'),
    path('users', viewsMain.users,name='users'),
    path('usersSearch', viewsMain.usersSearch,name='usersSearch'),
    path('usersSearchNumID', viewsMain.usersSearchNumID,name='usersSearchNumID'),
    path('devicesSearch', viewsMain.devicesSearch,name='devicesSearch'),
    path('NavGet', viewsMain.NavGet,name='NavGet'),
    path('userAdd', viewsMain.userAdd,name='userAdd'),
    path('userEdit', viewsMain.userEdit,name='userEdit'),
    path('userDelete', viewsMain.userDelete,name='userDelete'),
    path('RecordAtt', viewsMain.RecordAtt,name='RecordAtt'),
    path('eventLogPage', viewsMain.eventLogPage,name='eventLogPage'),
    path('currentAttendance', viewsMain.currentAttendance,name='currentAttendance'),
    path('printAttendance', viewsMain.printAttendance,name='printAttendance'),
    path('usersAttendance', viewsMain.usersAttendance,name='usersAttendance'),
    path('usersFullAttendance', viewsMain.usersFullAttendance,name='usersFullAttendance'),
    path('usersNoAttendance', viewsMain.usersNoAttendance,name='usersNoAttendance'),
    path('usersHalfAttendance', viewsMain.usersHalfAttendance,name='usersHalfAttendance'),
    path('usersFullAttendanceEdit', viewsMain.usersFullAttendanceEdit,name='usersFullAttendanceEdit'),
    path('usersHalfAttendanceEdit', viewsMain.usersHalfAttendanceEdit,name='usersHalfAttendanceEdit'),
    path('usersNoAttendanceEdit', viewsMain.usersNoAttendanceEdit,name='usersNoAttendanceEdit'),
    path('printAttendancePDF', viewsMain.printAttendancePDF,name='printAttendancePDF'),
    path('printPeriodicAttPDF', viewsMain.printPeriodicAttPDF,name='printPeriodicAttPDF'),
    path('printElPlDayPDF', viewsMain.printElPlDayPDF,name='printElPlDayPDF'), 
    path('printElPlPeriodicPDF', viewsMain.printElPlPeriodicPDF,name='printElPlPeriodicPDF'),
    path('synchronizeData', viewsMain.synchronizeData,name='synchronizeData'),
    path('pagelogout', viewsMain.pagelogout,name='pagelogout'),
    path('userGet/<int:id>', viewsMain.userGet,name='userGet'),
    path('AttRRGet/<int:id>', viewsMain.AttRRGet,name='AttRRGet'),
    path('AttRRNoGet/<int:id>', viewsMain.AttRRNoGet,name='AttRRNoGet'),
    path('departments', viewsMain.departments,name='departments'),
    path('staffAdd', viewsMain.staffAdd,name='staffAdd'),
    path('staffDelete', viewsMain.staffDelete,name='staffDelete'),
    path('staffEdit', viewsMain.staffEdit,name='staffEdit'),
    path('staffGet/<int:id>', viewsMain.staffGet,name='staffGet'),
    path('industry', viewsMain.industry,name='industry'),
    path('industryLogo', viewsMain.industryLogo,name='industryLogo'),
    path('SynchronizeAttendances', viewsMain.SynchronizeAttendances,name='SynchronizeAttendances'),
    path('CheckDevices', viewsMain.CheckDevices,name='CheckDevices'),
    path('Signature', viewsMain.Signature,name='Signature'),
    path('signatureSearch', viewsMain.signatureSearch,name='signatureSearch'),
    path('SignatureDelete', viewsMain.SignatureDelete,name='SignatureDelete'),
    path('holidayDelete', viewsMain.holidayDelete,name='holidayDelete'),
    path('holiday', viewsMain.holiday,name='holiday'),
    path('eventSearch', viewsMain.eventSearch,name='eventSearch'),
    path('holidaySearch', viewsMain.holidaySearch,name='holidaySearch'),
    path('holidayDateSearch', viewsMain.holidayDateSearch,name='holidayDateSearch'),
    path('eventDateSearch', viewsMain.eventDateSearch,name='eventDateSearch'),
    path('holidayCurrentYear', viewsMain.holidayCurrentYear,name='holidayCurrentYear'),
     path('holidayNextYear', viewsMain.holidayNextYear,name='holidayNextYear'),
    path('OrganizationChart', viewsMain.OrganizationChart,name='OrganizationChart'),
    path('OrganizationChartMove', viewsMain.OrganizationChartMove,name='OrganizationChartMove'),
    path('OrganizationChartDel', viewsMain.OrganizationChartDel,name='OrganizationChartDel'),
    path('role', viewsMain.role,name='role'),
    path('roleDelete', viewsMain.roleDelete,name='roleDelete'),
    path('roleEdit', viewsMain.roleEdit,name='roleEdit'),
    path('holidayEdit', viewsMain.holidayEdit,name='holidayEdit'),
    path('staffHolidayEdit', viewsMain.staffHolidayEdit,name='staffHolidayEdit'),
    path('roleGet/<int:id>', viewsMain.roleGet,name='roleGet'),
    path('holidayGet/<int:id>', viewsMain.holidayGet,name='holidayGet'),
    path('staffHolidayGet/<int:id>', viewsMain.staffHolidayGet,name='staffHolidayGet'),
    path('relationType', viewsMain.relationType,name='relationType'),
    path('relationTypeDelete', viewsMain.relationTypeDelete,name='relationTypeDelete'),
    path('relationTEdit', viewsMain.relationTEdit,name='relationTEdit'),
    path('relationTGet/<int:id>', viewsMain.relationTGet,name='relationTGet'),
    path('membersTeam', viewsMain.membersTeam,name='membersTeam'),
    path('staffHolidays', viewsMain.staffHolidays,name='staffHolidays'),
    path('staffHolidaysSearch', viewsMain.staffHolidaysSearch,name='staffHolidaysSearch'),
    path('staffHolidaysDelete', viewsMain.staffHolidaysDelete,name='staffHolidaysDelete'),
    path('wrariaProsopikou', viewsMain.wrariaProsopikou,name='wrariaProsopikou'),
    path('wrariaProsopikouSearch', viewsMain.wrariaProsopikouSearch,name='wrariaProsopikouSearch'),
    path('printWrariaProsopikouPDF', viewsMain.printWrariaProsopikouPDF,name='printWrariaProsopikouPDF'),
    path('printWrariaProsopikouExcel', viewsMain.printWrariaProsopikouExcel,name='printWrariaProsopikouExcel'),
    path('searchCurrDep', viewsMain.searchCurrDep,name='searchCurrDep'),
    path('searchCurrID', viewsMain.searchCurrID,name='searchCurrID'),
    path('searchCurrLF', viewsMain.searchCurrLF,name='searchCurrLF'),
    path('depInfoSearch', viewsMain.depInfoSearch,name='depInfoSearch'),
    
    
    #path('seed1', viewsSeeders.seedUsers,name='seed1'),# test seed users from excel  
    #path('seed2', viewsSeeders.seedDevices,name='seed2'),# test seed devices from excel
    #path('seed3', viewsSeeders.seedDepartments,name='seed3'),# test seed departments from excel
    #path('seed4', viewsSeeders.seedStaffDepartments,name='seed4'),# test seed staff departments info from excel
    #path('seed5', viewsSeeders.seedRoles,name='seed5'),# test seed roles from excel
    #path('seed6', viewsSeeders.seedIndustry,name='seed6'),# test seed industry from excel
    #path('seed7', viewsSeeders.seedSignatures,name='seed7'),# test seed signatures from excel, same as roles
    #path('seed8', viewsSeeders.seedMembers,name='seed8'),# test seed members from excel
    #path('seed9', viewsSeeders.seedRelationTypes,name='seed9')# test seed members from excel
]
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)