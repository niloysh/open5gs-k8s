import os
import random
import time
import subprocess
from datetime import datetime
import argparse

def getAddress():
    cmd = "ip a show uesimtun0 | grep inet | head -n 1 | awk '{print $2}' | cut -d'/' -f1"
    result = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    print(result)
    return result

def run_action(act):
    address = getAddress()
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = f"/tmp/{current_time}_logfile.txt"

    if act == 0:
        print('Ping Google')
        os.system(f"ping -I uesimtun0 google.com -c 100 2>&1 | tee {logfile}")
    elif act == 1:
        print('Ping FB')
        os.system(f"ping -I uesimtun0 facebook.com -c 100 2>&1 | tee {logfile}")
    elif act == 2:
        print('Curl Wiki')
        url = random.randint(0, 1)
        if url == 0: url = "https://en.wikipedia.org/wiki/5G"
        else: url = "https://en.wikipedia.org/wiki/Jitter"
        os.system(f"curl --interface uesimtun0 {url} 2>&1 | tee {logfile}")
    elif act == 3:
        print('Youtube')
        url = "https://www.youtube.com/watch?v=rHvhsQ9dvJI"
        os.makedirs("./Videos", exist_ok=True)
        os.system(f"./yt-dlp --source-address {address} -P ./Videos {url} 2>&1 | tee {logfile}")
        time.sleep(75)
        os.system("rm -dr ./Videos")
    elif act == 4:
        print('Download Ubunutu ISO')
        url = "https://releases.ubuntu.com/focal/ubuntu-20.04.6-desktop-amd64.iso"
        file = url.split('/')[-1]
        os.system(f"wget --bind-address {address} {url} 2>&1 | tee {logfile}")
        os.system(f"rm {file}")

def main(debug=False):
    if debug:
        act = int(input("Enter the act number (0-4): "))
        run_action(act)
    else:
        while True:
            act = random.randint(0, 4)
            run_action(act)
            sleeptime = random.randint(2, 7)
            time.sleep(sleeptime)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug mode for script")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    main(args.debug)