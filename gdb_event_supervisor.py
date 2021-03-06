#!/usr/bin/python

usage = "gdb_event_supervisor.py [--options] config.ini"
description = \
"""
launched for each new lvalert message, this script will exit if alert_type!="new".
It then determines a schedule of checks that need to be performed (specified in config.ini) and sets about monitoring the GraceDB event.
If everything is kosher, we exit gracefully. Otherwise, we send emails to the people specified in the config file.
"""

#=================================================

import os
import sys
import time
import ConfigParser
import json
from ligo.gracedb.rest import GraceDb

import checks
 
from optparse import OptionParser

#=================================================

parser = OptionParser(usage=usage, description=description)

parser.add_option('-v', '--verbose', default=False, action="store_true")

parser.add_option('-g', '--graceid', default=False, type="string", help="a graceid for which we perform the scheduled checks. If not supplied, we parse this information from an lvalert assumed to be in STDIN")
parser.add_option('-G', '--gracedb_url', default=None, type="string")

parser.add_option('-a', '--annotate-gracedb', default=False, action="store_true", help="write log messages describing checks into GraceDb")

opts, args = parser.parse_args()

if len(args)!=1:
    raise ValueError("please supply exactly one config.ini file as an argument")
configfile = args[0]

#=================================================

if opts.graceid: ### user defines the graceid, no need to reference an lvaler
    gdb_id = opts.graceid
    if opts.verbose:
        print "processing event : %s"%gdb_id

else: ### parse the alert to determine gdb_id
    ### parse the alert
    alert_message = sys.stdin.read()
    if opts.verbose:
        print "alert received :\n%s"%alert_message

    alert = json.loads(alert_message)
    if alert["alert_type"] != "new":
        if opts.verbose:
            print "alert_type!=\"new\", skipping"
        sys.exit(0) ### not a new alert

    gdb_id = alert['uid']
    if opts.verbose:
        print "New event detectected : %s"%gdb_id

### set up the connection to gracedb
if opts.gracedb_url:
    if opts.verbose:
        print "conecting to GraceDb : %s"%(opts.gracedb_url)
    gracedb = GraceDb( opts.gracedb_url )
else:
    if opts.verbose:
        print "connecting to GraceDb"
    gracedb = GraceDb()

try:
    gdb_entry = json.loads(gracedb.event(gdb_id).read())
except:
    import traceback
    traceback.print_exc()
    sys.exit(1)

### get parameters about event type from gracedb
group = gdb_entry['group']
pipeline = gdb_entry['pipeline']
if gdb_entry.has_key('search'):
    search = gdb_entry['search']
    event_type = "%s_%s_%s"%(group, pipeline, search)
else:
    search = None
    event_type = "%s_%s"%(group, pipeline)

event_type = event_type.lower() ### cast to all lower case to match config file sections
if opts.verbose:
    print "\tevent_type : %s"%(event_type)

#=================================================

### read in the config file
if opts.verbose:
    print "reading config from : %s\nand setting up schedule of checks"%(configfile)
config = ConfigParser.SafeConfigParser()
config.read(configfile)

### set up the schedule of checks
schedule = checks.config_to_schedule( config, event_type, verbose=opts.verbose )

### annotate gracedb with list of scheduled checks
if opts.annotate_gracedb:
    log = "event_supervisor scheduled to check: %s"%(", ".join([description for dt, foo, kwargs, email, description in schedule]))
    gracedb.writeLog( gdb_id, log )

### perform the scheduled checks
if opts.verbose:
    print "performing schedule"
#to = time.time() ### start time of our checking proceedures
to = time.mktime(time.strptime(gdb_entry['created'], '%Y-%m-%d %H:%M:%S %Z')) ### parse creation time from GraceDB

for dt, foo, kwargs, email, description in schedule:
    ### check current time stamp
    wait = dt - (time.time()-to)
    if wait > 0:
        if opts.verbose:
            print "\nwaiting %.3f seconds before performing : %s\n"%(wait, description)
        time.sleep( wait )

    if foo( gracedb, gdb_id, **kwargs ): ### perform this check. (foo -> True) means the check failed!
        if email:
            os.system( "echo \"action required for GraceDB event : %s\n%s\" | mail -s \"action required for GraceDB event : %s\" %s"%(gdb_id, description, gdb_id, " ".join(email)) )
            if opts.annotate_gracedb:
                log = "event_supervisor checked : %s. Action required! email sent to %s"%(description, ", ".join(email))
                gracedb.writeLog( gdb_id, log )
        else:
            print "WARNING: check failed but no email recipients specified! No warning messages will be sent!"
            if opts.annotate_gracedb:
                log = "event_supervisor checked : %s. Action required! but no email specified"%(description)
                gracedb.writeLog( gdb_id, log )
    elif opts.annotate_gracedb:
        log = "event_supervisor checked : %s. No action required."%(description)
        gracedb.writeLog( gdb_id, log )

if opts.annotate_gracedb:
    log = "event_supervisor completed all scheduled checks"
    gracedb.writeLog( gdb_id, log )

