import os
import schedule
import time
import subprocess


#p = subprocess.Popen('node scrape.js', shell=True)
def deleteFiles():
    target = '/home/bill/Desktop/'
    for x in os.listdir(target):
        if x.endswith('.csv'):
            os.unlink(target+x)


def job():
    p = subprocess.Popen('node scrape.js', shell=True)
#    return p
#    p=os.system("node /home/bill/api/scrape.js")
#    p

#schedule.every(1).minutes.do(job)
schedule.every(6).hours.do(job)
schedule.every(1).minutes.do(deleteFiles)

while True:
    schedule.run_pending()
    time.sleep(1)

#job()

