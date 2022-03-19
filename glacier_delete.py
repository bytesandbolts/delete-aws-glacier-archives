#!/usr/bin/env python3

import json
import subprocess
import time
import signal
import sys
from arnparse import arnparse
import shutil
from os.path import exists as file_exists
import datetime

def signal_handler(sig, frame):
    print("saving inventory ... ", end='', flush=True)
    with open(json_file, 'w') as outfile:
        json.dump(data, outfile)
    print("done.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

json_file=sys.argv[1]

if not file_exists(json_file+'.bak'):
    print("backing up inventory ... ", end='', flush=True)
    shutil.copy2(json_file,json_file+'.bak')
    print("done.")

with open(json_file) as f:
    data = json.load(f)

arn=arnparse(data['VaultARN'])
archlist = list(data['ArchiveList'])
total = len(archlist)

stttime = datetime.datetime.now()
oldtime = stttime
savtime = stttime

for ind, item in enumerate(archlist):
    cmd = "aws glacier delete-archive --account-id %s --region %s --vault-name %s --archive-id=\'%s\'" % (arn.account_id, arn.region, arn.resource, item['ArchiveId'])
    print('Deleting archive %d of %d ...\n%s' % (ind+1, total, cmd))
    returned_value = subprocess.call(cmd, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    print('returned value: %d, ' % returned_value, end='', flush=True)
    if returned_value == 0:
         data['ArchiveList'].pop(next(i for i, v in enumerate(
            data['ArchiveList']) if v['ArchiveId'] == item['ArchiveId']))
         print('deleted archive from list.')
    nowtime = datetime.datetime.now()
    runtime = nowtime - stttime
    avgtime = runtime/(ind+1)
    rsttime = datetime.timedelta(seconds=round((avgtime*(total-ind-1)).total_seconds()))
    fintime = nowtime.replace(microsecond=0)+rsttime
    runtime = datetime.timedelta(seconds=round(runtime.total_seconds()))
    print('total run time: %s, current item time: %s s, average item time: %s s, remaining time: ~%s, finished: ~%s' % (runtime, (nowtime-oldtime).total_seconds(), avgtime.total_seconds(), rsttime, fintime))
    oldtime = nowtime
    if (nowtime-savtime).total_seconds() > 600 or ind == total-1:
        print("saving inventory ... ", end='', flush=True)
        savtime = nowtime
        with open(json_file, 'w') as outfile:
            json.dump(data, outfile)
        print("done.")
    print()

cmd = "aws glacier initiate-job --account-id %s --region %s --vault-name %s --job-parameters '{\"Type\": \"inventory-retrieval\"}'" % (arn.account_id, arn.region, arn.resource)
print('Initiating inventory ...\n%s' % cmd)
result = subprocess.run(cmd, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
print(result.stdout.decode('utf-8'))
