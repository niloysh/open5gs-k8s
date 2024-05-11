import os
import random
import time
import subprocess

def getAddress():
    cmd = "ip a show uesimtun0 | grep inet | head -n 1 | awk '{print $2}'"
    result = subprocess.check_output(cmd, shell=True)
    return result

while True:
    address = getAddress
    act = random.randint(0, 5)
    if act == 0:
        os.system("ping -I uesimtun0 google.com > /tmp/$LOGFILE 2>&1 & -c 100")
    elif act == 1:
        os.system("ping -I uesimtun0 facebook.com > /tmp/$LOGFILE 2>&1 & -c 100")
    elif act == 2:
        os.system("curl --interface uesimtun0 ")
    elif act == 3:
        url = "https://www.youtube.com/watch?v=rHvhsQ9dvJI"
        os.system(f"yt-dlp --source-address {address} -P ~/Videos {url}")
        time.sleep(75)
        os.system("rm -dr ~/Videos")
    elif act == 4:
        url = ""
        os.system(f"wget --bind-address {address} {url}")
    sleeptime = random.randint(2, 7)
    time.sleep(sleeptime)
