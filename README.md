# gdb_event_supervisor

THIS CODE IS DEPRICATED/ABANDONED-WARE. INSTEAD, YOU SHOULD USE THE GRiNCH REPO HOSTED OUT OF UWM (git clone albert.einstein@ligo-vcs.phys.uwm.ede:/usr/local/git/grinch.git)

This repo contains an extremely light-weight monitor for automatic follow-up processes launched whenever an event enters GraceDB. 
Through a config file, users can specify which processes they want to monitor (check) depending on the event type as well as when they want to check on these processes.

The exectuable (gdb_event_supervisor.py) should be launched via an lvalert_listen instance and will only persist for alert_type="new" messages.
It constructs a schedule of checks that are requested based on the config file and sleeps between each check as needed.
If a check (implemented as simple function calls in checks.py) suggests that further action is required, an email is sent to a list of addresses specified in the config file.


