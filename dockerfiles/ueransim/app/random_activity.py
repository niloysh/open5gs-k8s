import os
import random
import time

while True:
    act = random.randint(0, 5)
    if act == 0:
        os.system("ping -I uesimtun0 google.com > /tmp/$LOGFILE 2>&1 & -c 100")
    elif act == 1:
        os.system("ping -I uesimtun0 facebook.com > /tmp/$LOGFILE 2>&1 & -c 100")
    elif act == 2:
        os.system("curl --interface uesimtun0 ")
    elif act == 3:
        url = "https://www.youtube.com/watch?v=rHvhsQ9dvJI"
        os.system(f"yt-dlp -P ~/Videos {url}")
        os.system("rm -dr ~/Videos")
        
    sleeptime = random.randint(2, 7)
    time.sleep(sleeptime)
