# executes the methods one by one as wriiten order in file Sync.py, can be executed in task scheduler, needs windows settings env variable in place
import os
os.chdir("C:\\Users\Administrator\Desktop\IPearancePythonVersions\clockInVoioBackend\ipearanceMain")

os.system('cmd /c "workon test & python manage.py test ipearanceBackend.Sync"')
#cmd /k leaves console open, /c it closes the console at the end
#env variables
#C:\WINDOWS\system32
#C:\Users\p.lysikatos\Anaconda3\python.exe
#C:\Users\p.lysikatos\Anaconda3\Scripts
