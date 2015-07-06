description = """ a module for performing checks of GraceDB triggered processes. NOTE: the "check" functions return TRUE if the check failed (action is needed) and FALSE if everything is fine """

import numpy as np

#=================================================
# set up schedule of checks
#=================================================

def config_to_schedule( config, event_type, verbose=False ):
    """
    determines the schedule of checks that should be performed for this event
    the checks should be (timestamp, function, kwargs, email) tuples, where timestamp is the amount of time after NOW we wait until performing the check, function is the specific function that performs the check (should have a uniform input argument? just the gracedb connection?) that returns either True or False depending on whether the check was passed, kwargs are any extra arguments needed for function, and email is a list of people to email if the check fails
    """

    ### extract lists of checks
    if verbose:
        print "reading in default checks"
    checks = dict( config.items("default") )
    if config.has_section(event_type):
        if verbose:
            print "reading in extra checks specific for event_type : %s"%(event_type)
        checks.update( dict( config.items(event_type) ) )
    elif verbose:
        print "no section found corresponding to event_type : %s"%(event_type)

    ### construct schedule
    schedule = []

    #=== event creation
    group, pipeline = event_type.split("_")[:2]
    if pipeline == "cwb":
        if verbose:
            print "\tcWB event"
        dt = 10
        kwargs = {'verbose':verbose}

        schedule.append( (dt, cwb_eventcreation, kwargs, checks['eventcreation'].split(), "cwb_eventcreation") )

    elif pipeline == "olib":
        if verbose:
            print "\toLIB event"
        dt = 10
        kwargs = {'verbose':verbose}

        schedule.append( (dt, olib_eventcreation, kwargs, checks['eventcreation'].split(), "olib_eventcreation") )

    elif pipeline == "gstlal":
        if verbose:
            print "\tgstlal event"
        dt = 10
        kwargs = {'verbose':verbose}

        schedule.append( (dt, gstlal_eventcreation, kwargs, checks['eventcreation'].split(), "gstlal_eventcreation") )

    elif pipeline == "mbtaonline":
        if verbose:
            print "\tMBTA event"
        dt = 10
        kwargs = {'verbose':verbose}

        schedule.append( (dt, mbta_eventcreation, kwargs, checks['eventcreation'].split(), "mbta_eventcreation") )

    #=== local properties of event streams
    if checks.has_key("local_rates"):
        if verbose:
            print "\tcheck local_rates"
        dt = 0
        kwargs = {"rate_thr":config.getfloat("local_rates","rate") , "window":config.getfloat("local_rates","window"), "verbose":verbose}

        schedule.append( (dt, local_rates, kwargs, checks["local_rates"].split(), "local_rates") )

    #=== idq
    if checks.has_key("idq_start"):
        if verbose:
            print "\tcheck idq_start"
        dt = config.getfloat("idq", "start")
        kwargs = {"ifos":config.get("idq","ifos").split(), 'verbose':verbose}

        schedule.append( (dt, idq_start, kwargs, checks['idq_start'].split(), "idq_start") )

    if checks.has_key("idq_finish"):
        if verbose:
            print "\tcheck idq_finish"
        dt = config.getfloat("idq", "finish")
        kwargs = {"ifos":config.get("idq","ifos").split(), 'verbose':verbose}

        schedule.append( (dt, idq_finish, kwargs, checks['idq_finish'].split(), "idq_finish") )

    #=== lib
    if checks.has_key("lib_start"):
        if verbose:
            print "\tcheck lib_start"
        dt = config.getfloat("lib", "start")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, lib_start, kwargs, checks['lib_start'].split(), "lib_start") )        

    if checks.has_key("lib_finish"):
        if verbose:
            print "\tcheck lib_finish"
        dt = config.getfloat("lib", "finish")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, lib_finish, kwargs, checks['lib_finish'].split(), "lib_finish") )

    #=== bayestar
    if checks.has_key("bayestar_start"):
        if verbose:
            print "\tcheck bayestar_start"
        dt = config.getfloat("bayestar", "start")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, bayestar_start, kwargs, checks['bayestar_start'].split(), "bayestar_start") )

    if checks.has_key("bayestar_finish"):
        if verbose:
            print "\tcheck bayestar_finish"
        dt = config.getfloat("bayestart", "finish")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, bayestar_finish, kwargs, checks['bayestar_finish'].split(), "bayestar_finish") )

    #=== bayeswave
    if checks.has_key("bayeswave_start"):
        if verbose:
            print "\tcheck bayeswave_start"
        dt = config.getfloat("bayeswave", "start")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, bayeswave_start, kwargs, checks['bayeswave_start'].split(), "bayeswave_start") )

    if checks.has_key("bayeswave_finish"):
        if verbose:
            print "\tcheck bayeswave_finish"
        dt = config.getfloat("bayeswave", "finish")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, bayeswave_finish, kwargs, checks['bayeswave_finish'].split(), "bayeswave_finish") )

    #=== lalinference
    if checks.has_key("lalinference_start"):
        if verbose:
            print "\tcheck lalinference_start"
        dt = config.getfloat("lalinference", "start")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, lalinference_start, kwargs, checks['lalinference_start'].split(), "lalinference_start") )

    if checks.has_key("lalinference_finish"):
        if verbose:
            print "\tcheck lalinference_finish"
        dt = config.getfloat("lalinference", "finish")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, lalinference_finish, kwargs, checks['lalinference_finish'].split(), "lalinference_finish") )

    #=== externaltriggers
    if checks.has_key("externaltriggers_search"):
        if verbose:
            print "\tcheck externaltriggers_search"
        dt = config.getfloat("externaltriggers_search", "dt")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, externaltriggers_search, kwargs, checks['externaltriggers_search'].split(), "externaltriggers_search") )

    #=== unblindinjections
    if checks.has_key("unblindinjections_search"):
        if verbose:
            print "\tcheck unblindinjections_search"
        dt = config.getfloat("unblindinjections_search", "dt")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, unblindinjections_search, kwargs, checks['unblindinjections_search'].split(), "unblindinjections_search") )

    #=== plot_skymaps
    if checks.has_key("plot_skymaps"):
        if verbose:
            print "\tcheck plot_skymaps"
        dt = config.getfloat("plot_skymaps", "dt")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, plot_skymaps, kwargs, checks['plot_skymaps'].split(), "plot_skymaps") )

    #=== json_skymaps
    if checks.has_key("json_skymaps"):
        if verbose:
            print "\tcheck json_skymaps"
        dt = config.getfloat("json_skymaps", "dt")
        kwargs = {'verbose':verbose}

        schedule.append( (dt, json_skymaps, kwargs, checks['json_skymaps'].split(), "json_skymaps") )

    ### order according to dt, smallest to largest
    schedule.sort(key=lambda l:l[0])

    return schedule

#=================================================
# methods that check the local properties of the stream of events submitted to GraceDB
#=================================================

def local_rates( gdb, gdb_id, verbose=False, window=5.0, rate_thr=5.0, event_type=None ):
    """
    checks that the local rate of events does not exceed the threshold (rate_thr) over the window
    performs this check for ALL event types and for this event type in particular
    """
    if verbose:
        print "%s : local_rates"%(gdb_id)

    if window*rate_thr < 1:
        print "\tWARNING: window*rate_thr < 1. We will always require action for this check"

    ### get this event
    if verbose:
        print "\tretrieving information about this event:"
    gdb_entry = gdb.event( gdb_id ).json()

    ### get event time
    event_time = float(gdb_entry['gpstime'])
    if verbose:
        print "\t\tgpstime : %.6f"%(event_time)

    ### get event type
    group = gdb_entry['group']
    pipeline = gdb_entry['pipeline']
    if gdb_entry.has_key('search'):
        search = gdb_entry['search']
        event_type = "%s_%s_%s"%(group, pipeline, search)
    else:
        search = None
        event_type = "%s_%s"%(group, pipeline)
    if verbose:
        print "\t\tevent_type : %s"%(event_type)

    ### query for neighbors in (t-window, t+window), excluding this event
    if verbose:
        print "\tretrieving neighbors within [%.6f-%.6f, %.6f+%6f]"%(event_time, window, event_time, window)
    gdb_entries = [ entry for entry in gdb.events( "%d..%d"%(np.floor(event_time-window), np.ceil(event_time+window)) ) if entry['graceid'] != gdb_id ]

    ### count numbers of events
    if verbose:
        print "\tcounting events:"
    nevents = 1
    nevents_type = 1
    for entry in gdb_entries:
        nevents += 1
        if entry.has_key('search'):
            e_type = "%s_%s_%s"%(entry['group'], entry['pipeline'], entry['search'])
        else:
            e_type = "%s_%s"%(entry['group'], entry['pipeline'])
        event_type += (e_type == event_type) ### increment if true

    if verbose:
        print "\t\t%d %s\n\t\t%d total"%(nevents_type, event_type, nevents)

    ### check rates
    count_thr = 2*window*rate_thr
    if (nevents_type) > count_thr:
        if verbose:
            print "\tevent rate higher than %.3f observed within [%.6f-%.6f, %.6f+%.6f] for event type : %s\n\taction_required : True"%(rate_thr, event_time, window, event_time, window, event_type)
        return True

    elif (nevents) > count_thr: 
        if verbose:
            print "\tevent rate higher than %.3f observed within [%.6f-%.6f, %.6f+%.6f] for all event types\n\taction_required : True"%(rate_thr, event_time, window, event_time, window)
        return True

    if verbose:
        print "\taction_required : False"
    return False

#=================================================
# methods that check that an event was created successfully and all expected meta-data/information has been uploaded
#=================================================

def cwb_eventcreation( gdb, gdb_id, verbose=False, fits="skyprobcc.fits.gz" ):
    """
    checks that all expected data is present for newly created cWB events.
    This includes:
        the cWB ascii file uploaded by the pipeline for this event
        the fits file generated as part of the detection processes.
    """
#    files = gdb.files( gdb_id )
    if verbose:
        print "%s : cwb_eventcreation\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    fit = False
    pe = False
    for log in logs:
        comment = log['comment']
        if "cWB skymap fit" in comment:
            fit = True
        elif "cWB parameter estimation" in comment:
            pe = True

        if (fit and pe):
            break

    if verbose:
        print "\taction required : ", not (fit and pe)

    return not (fit and pe)

def olib_eventcreation( gdb, gdb_id, verbose=False ):
    """
    checks that all expected data is present for newly created oLIB (eagle) events.
    This includes:
        the json dictionary uploaed by the pipeline
    """
#    files = gdb.files( gdb_id )
    if verbose:
        print "%s : olib_eventcreation\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    prelim = False
    for log in logs:
        comment = log['comment']
        if "Preliminary results: " in comment:
            prelim = True

        if prelim:
            break

    if verbose:
        print "\taction required : ", not (prelim)
    return not (prelim)

def gstlal_eventcreation( gdb, gdb_id, verbose=False ):
    """
    checks that all expected data is present for newly created gstlal events.
    This includes:
        inspiral_coinc table
        psd estimates from the detectors
    """
#    files = gdb.files( gdb_id )
    if verbose:
        print "%s : gstlal_eventcreation\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    psd = False
    coinc = False
    for log in logs:
        comment = log['comment']
        if "strain spectral densities" in comment:
            psd = True
        elif "Coinc Table Created" in comment:
            coinc = True

        if psd and coinc:
            break

    if verbose:
        print "\taction required : ", not (psd and coinc)
    return not (psd and coinc)

def mbta_eventcreation( gdb, gdb_id, verbose=False ):
    """
    checks that all expected data is present for newly created mbta events.
    This includes:
        the "original data" file
    """
#    files = gdb.files( gdb_id )
    if verbose:
        print "%s : mbta_eventcreation\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    psd = False
    coinc = False
    for log in logs:
        comment = log['comment']
        if "Coinc Table Created" in comment:
            coinc = True
        if "PSDs" in comment:
            psd = True

        if (psd and coinc):
            break

    if verbose:
        print "\taction required : ", not (psd and coinc)
    return not (psd and coinc)

#=================================================
# methods that check whether idq processes were triggered and completed
#=================================================

def idq_start( gdb, gdb_id, ifos=['H','L'], verbose=False ):
    """
    check that iDQ processes were started at each of the specified ifos
    """

    if verbose:
        print "%s : idq_start\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log'] ### retrieve the log messages attached to this event

    if verbose:
        print "\tparsing log"
    result = [1]*len(ifos)
    for log in logs:
        comment = log['comment']
        if ("Started searching for iDQ information" in comment):
            for ind, ifo in enumerate(ifos):
                if result[ind] and (ifo in comment):
                    result[ind] = 0
    
    if verbose:
        action_required = False
        for r, ifo in zip(result, ifos):
            if r:
                print "\tWARNING: no idq_start statement found for ifo : %s"%ifo
                action_required = True
            else:
                print "\tidq_start statement found for ifo : %s"%ifo
        print "\taction required : ", action_required 

    return sum(result) > 0

def idq_finish( gdb, gdb_id, ifos=['H','L'], verbose=False ):
    """
    check that iDQ processes finished at each of the specified ifos
    """

    if verbose:
        print "%s : idq_finish\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    result = [1]*len(ifos)
    for log in logs:
        comment = log['comment']
        if ("Finished searching for iDQ information" in comment):
            for ind, ifo in enumerate(ifos):
                if result[ind] and (ifo in comment):
                    result[ind] = 0

    if verbose:
        action_required = False
        for r, ifo in zip(result, ifos):
            if r:
                print "\tWARNING: no idq_finish statement found for ifo : %s"%ifo
                action_required = True
            else:
                print "\tidq_finish statement found for ifo : %s"%ifo
        print "\taction required : ", action_required

    return sum(result) > 0

#=================================================
# methods that check whether lib processes were triggered and completed
#=================================================

def lib_start( gdb, gdb_id, verbose=False ):
    """
    checsk that LIB PE followup processes started (and were tagged correctly?)
    """
    if verbose:
        print "%s : lib_start\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "LIB Parameter estimation started." in comment:
            if verbose:
                print "\taction required : False"
            return False

    if verbose:
        print "\taction required : True"

    return True

def lib_finish( gdb, gdb_id, verbose=False ):
    """
    checks that LIB PE followup processes finished (and were tagged correctly?)
    """
    if verbose:
        print "%s : lib_finish\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "LIB Parameter estimation finished." in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

#=================================================
# methods that check whether bayeswave processes were triggered and completed
#=================================================

def bayeswave_start( gdb, gdb_id, verbose=False ):
    """
    checks that BayesWave PE processes started (and were tagged correctly?)
    """
    if verbose:
        print "%s : bayeswave_start\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "BayesWaveBurst launched" in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

def bayeswave_finish( gdb, gdb_id, verbose=False ):
    """
    checks that BayesWave PE processes finished (and were tagged correctly?)
    """
    if verbose:
        print "%s : bayeswave_finish\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "BWB Follow-up results" in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

#=================================================
# methods that check whether bayestar processes were triggered and completed
#=================================================

def bayestar_start( gdb, gdb_id, verbose=False ):
    """
    checks that BAYESTAR processes started (and were tagged correctly?)
    """
    if verbose:
        print "%s : bayestar_start\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "INFO:BAYESTAR:starting sky localization" in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

def bayestar_finish( gdb, gdb_id, verbose=False ):
    """
    checks that BAYESTAR processes finished (and were tagged correctly?)
    """
    if verbose:
        print "%s : bayestar_finish\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "INFO:BAYESTAR:sky localization complete" in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

#=================================================
# methods that check whether lalinference processes were triggered and completed
#=================================================

def lalinference_start( gdb, gdb_id, verbose=False ):
    """
    checks that LALInference PE processes started (and were tagged correctly?)
    """
    if verbose:
        print "%s : lalinference_start\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"

    print "\tWARNING: Currently lalinference does not report that it has started, so there is nothing to check... proceeding assuming everything is kosher"
    return False

def lalinference_finish( gdb, gdb_id, verbose=False ):
    """
    checks that LALInference PE processes finished (and were tagged correctly?)
    """
    if verbose:
        print "%s : lalinference_finish\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "online parameter estimation" in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

#=================================================
# tasks managed by gdb_processor
#=================================================

def externaltriggers_search( gdb, gdb_id, verbose=False ):
    """
    checks that external trigger searches were performed
    """
    if verbose:
        print "%s : externaltriggers_search\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if "Coincidence search complete" in comment:
            if verbose:
                print "\taction required : False"
            return False
    if verbose:
        print "\taction required : True"
    return True

def unblindinjections_search( gdb, gdb_id, verbose=False ):
    """
    checks that unblind injection search was performed
    """
    if verbose:
        print "%s : unblindinjections_search\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"
    for log in logs:
        comment = log['comment']
        if ("No unblind injections in window" in comment):
            if verbose:
                print "\taction required : False"
            return False

    print "\tWARNING: we do not currently know how to parse out statements when there is an unblind injection...proceeding assuming everything is kosher"

    if verbose:
        print "\taction required : False"
    return False

def plot_skymaps( gdb, gdb_id, verbose=False ):
    """
    checks that all FITS files attached to this event have an associated png file (produced by gdb_processor)
    """
    if verbose:
        print "%s : plot_skymaps\n\tretrieving event files"%(gdb_id)
    files = gdb.files( gdb_id ).json().keys() ### we really just care about the filenames

    if verbose:
        print "\tidentifying all FITS files"
    fitsfiles = [ filename for filename in files if filename.endswith(".fits") or filename.endswith(".fits.gz") ]

    if verbose:
        print "\tchecking for corresponding png figures"
    result = []
    for fitsfile in fitsfiles:
#        if fitsfile.endswith(".gz"):
#            fitsfile = fitsfile[:-3]
#        pngfile = "%spng"%(fitsfile[:-4])
        pngfile = "%s.png"%(fitsfile.split(".")[0])
        result.append( (not (pngfile in files), pngfile, fitsfile) )

    if verbose:
        action_required = False
        for r, pngfile, fitsfile in result:
            if r:
                print "\tWARNING: no png file found for FITS : %s <-> %s"%(fitsfile, pngfile)
                action_required = True
            else:
                print "\tpng file found for FITS : %s <-> %s"%(fitsfile, pngfile)
        print "\taction required : ", action_required

    return sum([r[0] for r in result]) > 0

#=================================================
# tasks managed by skyviewer and friends
#=================================================

def json_skymaps( gdb, gdb_id, verbose=False ):
    """
    checks that all FITS files attached to this event have an associated json file
    """
    if verbose:
        print "%s : json_skymaps\n\tretrieving event files"%(gdb_id)
    files = gdb.files( gdb_id ).json().keys() ### get just the names, not the urls

    if verbose:
        print "\tidentifying all FITS files"
    fitsfiles = [filename for filename in files if filename.endswith(".fits") or filename.endswith(".fits.gz") ]

    if verbose:
        print "\tchecking for corresponding json files"
    result = []
    for fitsfile in fitsfiles:
        if fitsfile.endswith(".gz"):
            fitsfile = fitsfile[:-3]
        jsonfile = "%sjson"%(fitsfile[:-4])
        result.append( (not (jsonfile in files), jsonfile, fitsfile) )

    if verbose:
        action_required = False
        for r, jsonfile, fitsfile in result:
            if r:
                print "\tWARNING: no json file found for FITS : %s <-> %s"%(fitsfile, jsonfile)
                action_required = True
            else:
                print "\tjson file found for FITS : %s <-> %s"%(fitsfile, jsonfile)
        print "\taction required : ", action_required

    return sum([r[0] for r in result]) > 0

#=================================================
# tasks managed by approval_processor
#=================================================

### what are these? labeling, etc?


