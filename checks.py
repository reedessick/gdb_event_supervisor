description = """ a module for performing checks of GraceDB triggered processes. NOTE: the "check" functions return TRUE if the check failed (action is needed) and FALSE if everything is fine """

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

    #=== else?
#    print "WARNING: there are many checks that are not yet implemented!"

    ### order according to dt, smallest to largest
    schedule.sort(key=lambda l:l[0])

    return schedule

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
        print "\tsuccess : ", not (fit and pe)

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
        print "\tsuccess : ", not (prelim)
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
        print "\tsuccess : ", not (psd and coinc)
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
        print "\tsuccess : ", not (psd and coinc)
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
        for r, ifo in zip(result, ifos):
            if r:
                print "\tWARNING: no idq_start statement found for ifo : %s"%ifo
            else:
                print "\tidq_start statement found for ifo : %s"%ifo
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
        for r, ifo in zip(result, ifos):
            if r:
                print "\tWARNING: no idq_finish statement found for ifo : %s"%ifo
            else:
                print "\tidq_finish statement found for ifo : %s"%ifo
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
                print "\tsuccess : False"
            return False

    if verbose:
        print "\tsuccess : True"

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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False
    if verbose:
        print "\tsuccess : True"
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
                print "\tsuccess : False"
            return False

    print "WARNING: we do not currently know how to parse out statements for when there is an unblind injection...proceeding assuming everything is kosher"

    if verbose:
        print "\tsuccess : False"
    return False

def plot_skymaps( gdb, gdb_id, verbose=False ):
    """
    checks that all FITS files attached to this event have an associated png file (produced by gdb_processor)
    """
    if verbose:
        print "%s : plot_skymaps\n\tretrieving log messages"%(gdb_id)
    logs = gdb.logs( gdb_id ).json()['log']

    if verbose:
        print "\tparsing log"

    print "\tWRITE ME : plot_skymaps"

    return False

#=================================================
# tasks managed by approval_processor
#=================================================

### what are these? labeling, etc?


