#!/usr/bin/env python3
# Site and mysql db backup via xtrabackup

import time
import requests
import sys
import re
import os
from datetime import datetime
import subprocess
import shutil


dbuser = 'root'
dbpass = 'Str0ngP@sSw0RD32423543246`812nj'
hostname = os.uname()[1]
webdirbackup = '/var/www'
sevenzcpulimit = 2

# Get current date and time for directory
now = datetime.now()
currentdate = now.strftime("%Y-%m-%d_%H-%M-%S")

# Backup location
backuplocation = '/backup/'+currentdate

# Backup statuses
databasebackupiscomplete = 0

# Unzipped backup size (in bytes)
unzipbackupsize = 0

# 7z backup size (in bytes)
zip7zbackupsize = 0

# Success status of backup
successstatus = 0

print (currentdate)
 
 
 
# Create backup directory
def mkbackupdir():
    try:  
        os.mkdir(backuplocation)
    except OSError:  
        print ("Creation of the directory %s failed" % backuplocation)
        return 1
    else:  
        print ("Successfully created the directory %s " % backuplocation)
        return 0
 
 
# Make first full backup
def makeinnobackup():
    process = subprocess.Popen(["/usr/bin/xtrabackup", '--user='+dbuser, '--password='+dbpass, '--backup','--target-dir='+backuplocation], stdout=subprocess.PIPE)
    process.communicate()[0]
    return (process.returncode)
 
# Make prepare database backup
def makeabackuppplylog():
    print ('Make log transaction')
    process = subprocess.Popen(["/usr/bin/xtrabackup", '--prepare', '--target-dir='+backuplocation], stdout=subprocess.PIPE)
    print ('---------------------------------------------------------------------------------------------------------')
    process.communicate()[0]
    print (process.returncode)
    return (process.returncode)
 
 
# Count unzipped backup size
def getfirstbackupsize():
    process = subprocess.check_output(['du','-sb', backuplocation]).split()[0].decode('utf-8')
    return (process)
 
 
# # Make 7z backup of database and webdir and delete source
def makezipofbackup():
    print ('---------------------------------------------------------------------------------------------------------')
    print ('Making 7z archive...')
    process = subprocess.Popen(["/usr/bin/7za", 'a', '-mmt='+str(sevenzcpulimit), backuplocation+'.7z', backuplocation, webdirbackup], stdout=subprocess.PIPE)
    process.communicate()[0]
    shutil.rmtree(backuplocation, ignore_errors=True)
    return (process.returncode)
 
 
# Count 7z backup size
def get7zbackupsize():
    process = subprocess.check_output(['du','-sb', backuplocation+'.7z']).split()[0].decode('utf-8')
    return (process)
 
 
 
if __name__ == "__main__":
    if (mkbackupdir() == 0):
        if (makeinnobackup() == 0):
            print ('Full backup has been maded successfully!')
            if (makeabackuppplylog() == 0):
                print ('Transaction log has been applied!')
                databasebackupiscomplete = 1
                print ('---------------------------------------------------------------------------------------------------------')
                if (getfirstbackupsize() != 0):
                    unzipbackupsize = getfirstbackupsize()
                    print ('Unzipped size is: '+str(unzipbackupsize))
                    if (makezipofbackup() == 0):
                        print ('Archive creation is completed!')
                        zip7zbackupsize = get7zbackupsize()
                        if (zip7zbackupsize != 0):
                            print (zip7zbackupsize)
                            successstatus = 1
                            print ('Backup status: '+str(successstatus))
                        else:
                            print ('System error, exit..')
                            sys.exit(1)
                    else:
                        print ('System error, exit..')
                        sys.exit(1)
                else:
                    print ('System error, exit..')
                    sys.exit(1)
            else:
                print ('Prepare backup error, exit..')
                sys.exit(1)
        else:
            print ('Full backup error, exit..')
            sys.exit(1)
    else:
        print ('System error, exit..')
        sys.exit(1)
