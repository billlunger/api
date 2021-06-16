import os
import subprocess

def job():
#    p = subprocess.Popen('node scrape.js', shell=True)
#    return p
    p=os.system("node /home/bill/api/scrape.js")
#    p

job()

