import shutil
import os
import time

s = r'C:\Users\SuriyaaP\momentecautomation\Momentec_Automation\python_playwright'
d = r'C:\Users\SuriyaaP\OneDrive - Royal Cyber Inc\Desktop\AGUSTA\MOMENTEC\agentplaywrightpython\playwright-agent\python_playwright'

try:
    if os.path.exists(d):
        shutil.rmtree(d, ignore_errors=True)
    time.sleep(1)
    shutil.copytree(s, d)
    print("Successfully copied python_playwright")
except Exception as e:
    print("Error copying python_playwright:", str(e))

s2 = r'C:\Users\SuriyaaP\momentecautomation\Momentec_Automation\data'
d2 = r'C:\Users\SuriyaaP\OneDrive - Royal Cyber Inc\Desktop\AGUSTA\MOMENTEC\agentplaywrightpython\playwright-agent\data'

try:
    if os.path.exists(d2):
        shutil.rmtree(d2, ignore_errors=True)
    time.sleep(1)
    shutil.copytree(s2, d2)
    print("Successfully copied data")
except Exception as e:
    print("Error copying data:", str(e))
