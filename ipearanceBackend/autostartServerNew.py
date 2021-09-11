# a quick way to run our django application, works also from task scheduler, needs enviroment variables in place on windows settings
import os
os.chdir("C:\\Users\Administrator\Desktop\IPearancePythonVersions\clockInVoioBackend\ipearanceMain")
#os.system('cmd /k "workon env2 & cd.. & python manage.py runserver 127.0.0.1:8000"') # works on double click on bat ,not scheduler
os.system('cmd /k "workon test & python manage.py runserver 10.129.113.10:8000"')

#env variables
#C:\WINDOWS\system32
#C:\Users\p.lysikatos\Anaconda3\python.exe
#C:\Users\p.lysikatos\Anaconda3\Scripts
