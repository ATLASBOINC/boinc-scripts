#!/usr/bin/env python3
#
# Validation script for ATLAS WU
# The script_validator should be configured to all this script like this:
# script_validator --app ATLAS --init_script "atlas_validator.py files runtime" --compare_script "true"
#
# Arguments: <output files> <CPU time>
#
import os, sys, tarfile, re, json

print('Arguments: %s' % ' '.join(sys.argv))
if len(sys.argv) != 4:
    print('Bad arguments')
    sys.exit(1)

ResultFile = sys.argv[1]
HitsFile = sys.argv[2]
boinccputime = float(sys.argv[3])
print('CPU time from BOINC: %d' % boinccputime)

jid = os.path.basename(ResultFile).split("_")[0]
cputime = 0
walltime = 0
HITS = None
try:
    with tarfile.open(ResultFile) as tar:
        try:
            diag = tar.extractfile('%s.diag' % jid)
            data = diag.read()
            print(data)
            usertime = re.search('UserTime=(\d*)', data)
            wallclock = re.search('WallTime=(\d*)', data)
            processors = re.search('Processors=(\d*)', data)
            if processors:
                processors = int(processors.group(1))
            else:
                processors = 1
            if usertime:
                cputime = int(usertime.group(1)) * processors
                print('CPU time measured by ARC %d (%d x %d)' % (cputime, cputime/processors, processors))
            if wallclock:
                walltime = int(wallclock.group(1))
                print('Wall time %d' % walltime)
        except:
            print('Could not extract diag from results tarball')

        try:
            heartbeat = tar.extractfile('./heartbeat.json')
            hbdata = json.load(heartbeat)
            try:
                xml = json.loads(hbdata['xml'])
                HITS = [f for f in xml if re.search('pool.root', f)][0]
                print('HITS file %s was produced successfully' % HITS)
            except:
                print('No HITS in heartbeat.json')
        except:
            print('Could not extract heartbeat file from results tarball')

except Exception as e:
    print('Failed to open result tar file: %s' % str(e))

if HITS and os.path.exists(HitsFile):
    print('Output files all present, validation passed')
    sys.exit(0)

# If CPU time is over 20 mins or walltime over 1hr let the job go through even if it failed
if boinccputime > 1200 or walltime > 3600:
    print('CPU time or walltime is long enough to pass validation')
    sys.exit(0)

print('An output file is missing, and cputime < 20 minutes, validation failed')
sys.exit(1)

