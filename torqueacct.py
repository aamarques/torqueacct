#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# torqueacct.py parses the Torque accounting files to extract some importants fields.
# Feel free to adapt for you needs.
#
# Antonio Marques - April 2017 - aamarques@gmail.com

import sys
import getpass
import datetime
import argparse
from glob import glob
from collections import defaultdict
from platform import python_version


def open_file(filename):
    try:
        filehandle = open(filename)
        return filehandle
    except IOError as e:
        print "I/O error({0}): {1} - {2}".format(e.errno, filename, e.strerror)
        exit()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        exit()

def parse_status(filename):
    fh = open_file(filename)
    # date formats
    dthformat = "%a %b %d %H:%M:%S %Y"
    dtformat = "%a %b %d %Y"

    # Create dict
    d_item = defaultdict(lambda: '<missing>')
    e_item = defaultdict(lambda: '<missing>')

    # others variables
    exit_msg = "empty"

    # Declare "global" and we can modify it'
    global _jobcnt
    global _jobcnt_d
    global _jobcnt_c
    global _jobcnt_a
    global _sub_tot

    for linefh in fh:
        # Create a list with 4 fields delimited by ';'
        stuff = linefh.split(';')

        # Search for "A"borted records. Just fo accumulate
        if stuff[1] == 'A':
            _jobcnt_a = _jobcnt_a + 1
            continue

        # Search for "D"eleted lines
        if stuff[1] == 'D':
           # jobid
            job_id = stuff[2]
            # _jobid was passed in command line option
            if _jobid is not None:
                if _jobid != job_id:
                    continue

            # username
            # the 3rd field is like "requestor=user@headnode.fqdn"
            # The next comand is to extract only the 'user' field. Splitting 1st for '=' and then '@'
            d_item[job_id] = stuff[3].split('=')[1].split('@')[0]

            # username was passed in command line to search for.
            if _username is not None:
                if d_item['job_id'] != _username:
                    continue

        # Search for "E"xit lines
        if stuff[1] == 'E':
           # the first part of stuff is date in american format (MM/DD/YYYY)
           # I will not use this format. If you want uncomment the next line and comment the format line below
           # where the format is weekday month day Year.
           # date = stuff[0].split()[0]

           # jobid
            job_id = stuff[2]
           # _jobid was passed in command line option
            if _jobid is not None:
                if _jobid != job_id:
                    continue

           # Split the filed 4 delimited by spaces. This will create a list of 'key=value" that will be used to populate a dict
            line_rest = stuff[3].split()

            # loop thru "line_rest" list. The format is 'chave=valor'
            # Do a "split" on the first delimiter '=' because has fields with more than one "=" delimiter.

            for itens in line_rest:
                chave, valor = itens.split('=', 1)
                e_item[chave] = valor

            # username was passed in command line to search for.
            if _username is not None:
                if e_item['user'] != _username:
                    continue

            # queue was passed in command line to search for.
            if _queue is not None:
                if e_item['queue'] != _queue:
                    continue

            # Paring the field that has two '=' delimiters to extract ppn value
            # i.e: Resource_List.neednodes=1:ppn=20 will be split into ('Resource_List.neednodes', '1:ppn=20')
            ppn = 0
            nodo_ppn = e_item['Resource_List.nodes']
            recursos = nodo_ppn.split(':')
            for recurso in recursos:
                if recurso.split('=')[0] == 'ppn':
                    ppn = int(recurso.split('=')[1])

            # New versions : cpu = total_execution_slots and node = unique_node_jobcnt
            node = e_item['unique_node_count']
            cpus = e_item['total_execution_slots']

            # Old versions of PBS/Torque:
            # node = Resource_List.nodect
            # Total of CPUs is nodect * ppn
            if node == "<missing>":
                node = int(e_item['Resource_List.nodect'])

            if cpus == "<missing>":
                cpus = node * ppn

            if e_item['account'] == "<missing>":
                e_item['account'] = _cluster

            # Time wasted waitting to run
            if int(e_item['etime']) > 0:
                waittime = int(e_item['start']) - int(e_item['etime'])
            else:
                waittime = int(e_item['start']) - int(e_item['qtime'])


            # Date formatting (weekday month day Year)
            date = datetime.datetime.fromtimestamp(float(e_item['etime'])).strftime(dtformat)
            # Converting the timestamp (epoch) into a formatted date and hour
            ct = datetime.datetime.fromtimestamp(float(e_item['ctime'])).strftime(dthformat)
            et = datetime.datetime.fromtimestamp(float(e_item['etime'])).strftime(dthformat)
            qt = datetime.datetime.fromtimestamp(float(e_item['qtime'])).strftime(dthformat)
            st = datetime.datetime.fromtimestamp(float(e_item['start'])).strftime(dthformat)
            ed = datetime.datetime.fromtimestamp(float(e_item['end'])).strftime(dthformat)
            wtime_seg = int(e_item['end']) - int(e_item['start'])

            if _deleted is True:
                if d_item[job_id] == '<missing>':
                    continue

            if d_item[job_id] != '<missing>':
                exit_msg = "This job was deleted by requestor { %s } " % (d_item[job_id].rstrip())
                _jobcnt_d = _jobcnt_d + 1
            else:
                exit_msg = "Completed"
                _jobcnt_c = _jobcnt_c + 1

            # Count the amount of jobs
            _jobcnt = _jobcnt +1

            # Accumulate in a global dict, tot of completed, tot of deleted and grand total, but only if --count is set
            if _show_count is True:
                _sub_tot[_fname.replace(_path, '')] = _jobcnt_a, _jobcnt_d, _jobcnt_c, _jobcnt
                continue

            # Let's print the fields

            if _choice != "csv":
                print "\n"
                print "jobid       : ", job_id
                print "date        : ", date
                print "user        : ", e_item['user']
                print "group       : ", e_item['group']
                print "account     : ", e_item['account']
                print "queue       : ", e_item['queue']
                print "node        : ", node
                print "ppn         : ", ppn
                print "cpus        : ", cpus

                if _segs is not True:
                    print "ctime       : ", ct
                    print "etime       : ", et
                    print "qtime       : ", qt
                    print "start       : ", st
                    print "end         : ", ed
                    print "walltime    : ", e_item['resources_used.walltime']
                else:
                    print "ctime       : ", e_item['ctime']
                    print "etime       : ", e_item['etime']
                    print "qtime       : ", e_item['qtime']
                    print "start       : ", e_item['start']
                    print "end         : ", e_item['end']
                    print "walltime    : ", wtime_seg

                print "waittime    : ", waittime
                print "exec host   : ", e_item['exec_host']
                print "jobname     : ", e_item['jobname']
                print "exit status : ", e_item['Exit_status']
                print "exit msg    : ", exit_msg
                print "\n"
            else:
                if _segs is not True:
                    print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
                        job_id, date, e_item['user'], e_item['group'], e_item['account'], e_item['queue'],
                        node, ppn, cpus, ct, et, qt, st, ed, waittime, e_item['resources_used.walltime'],
                        e_item['Exit_status'], e_item['exec_host'], e_item['jobname'], exit_msg)
                else:
                    print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
                        job_id, date, e_item['user'], e_item['group'], e_item['account'], e_item['queue'],
                        node, ppn, cpus, e_item['ctime'], e_item['etime'], e_item['qtime'], e_item['start'],
                        e_item['end'], waittime, wtime_seg, e_item['Exit_status'], e_item['exec_host'],
                        e_item['jobname'], exit_msg)


            # If reached at this point, all informations were printed and its done
            if _jobid is not None: break

    fh.close()
##### END of def parse_status()


def display_count():
    # Just print the total of displayed jobs. Just for fun!
    aborted = deleted = completed = total = 0
    print "\nDaily Summary Report of Jobs \n"
    print "Date\t\tAborted\t\tDeleted\t\tCompleted\tDaily Total \n"
    for x, sub  in sorted(_sub_tot.items()):
        dt = x[6:] + "/" + x[4:6] + "/" + x[:4]
        aborted = aborted + sub[0]
        deleted = deleted + sub[1]
        completed = completed + sub[2]
        total = total + sub[3]
        print "{0}\t{1}\t\t{2}\t\t{3}\t\t{4}".format(dt, sub[0], sub[1], sub[2], sub[3])

    print "\n{0}\t{1}\t\t{2}\t\t{3}\t\t{4}".format('Totals    ', aborted, deleted, completed, total)



#*#*#*#*#*#*#*#*#*#
# main execution *#
#*#*#*#*#*#*#*#*#*#

# Parse of arguments
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
             epilog=(''' \
Here are some examples of filename use
--------------------------------------

torqueacct.py -l 20170401  -> This will parse this date
torqueacct.py -l "201704*" -> This will parse all accounting files starting with 201704*. 
torqueacct.py -l "2017*"   -> This will parse all accounting files starting with 2017*

Note: When you are using wildcard, you must put it between quotation marks ("") 
      because unix shell expand it before to pass it to program.

You can mixe up all parameters to extract information you need
                     '''))

#
group = parser.add_mutually_exclusive_group()
#parser.add_argument("filename", help="The input log file to be parsed. REQUIRED", nargs="+")
parser.add_argument("-l", "--log",     help="The input log file to be parsed. REQUIRED", action="store", dest="filename")
parser.add_argument("-j", "--job",     help="Search for a specific JobID",               action="store",      dest="jobid")
parser.add_argument("-u", "--user",    help="Search for a specific username",            action="store",      dest="username")
parser.add_argument("-q", "--queue",   help="Search for queue name",                     action="store",      dest="queue")
parser.add_argument("-n", "--cluster", help="Name of the cluster (clermg1, lobo, volk)", action="store",      dest="cluster")
parser.add_argument("-d", "--del",     help="Shows the Deleted results",                 action="store_true", dest="deleted")
parser.add_argument("-t", "--segs",    help="Shows time fields in seconds",              action="store_true", dest="segs")
group.add_argument("-f", "--csv",      help="Shows the output results in a CSV format. DO NOT USE with --count",  action="store_true", dest="csv")
group.add_argument("-c", "--count",    help="Shows only the Total count of results. DO NOT USE with --csv",     action="store_true", dest="count")
parser.add_argument("-v", "-V", "--version",                                      action="version", version="%(prog)s 1.7.30.17")

args = parser.parse_args()

#_ver       = '.'.join(map(str, python_version().split('.')))
_ver       = python_version()
# Parsing Args 
_name_file   = args.filename  
_jobid       = args.jobid
_username    = args.username
_deleted     = args.deleted
_queue       = args.queue
_show_count  = args.count
_segs        = args.segs
_cluster     = args.cluster

# Global Vars
_choice    = "display"  # default value
_path      = "/var/spool/torque/server_priv/accounting/"
_jobcnt    = 0
_jobcnt_d  = 0
_jobcnt_c  = 0
_jobcnt_a  = 0

# Colors
_RED_font  = "\033[1;31;48m"
_NORM_bg   = "\033[0;37;48m"
# Dicts for Totals
_sub_tot=defaultdict(lambda: 0)

# Ajusting some cases.

# Verify Python Version
if _ver < "2.7.0":
	print _RED_font + "You need python in 2.7.0 or superior." + _NORM_bg
	print "Your python version is = {0}".format(_ver)
	sys.exit()

# Call help if user is no root
if getpass.getuser() != 'root':
   print(_RED_font + "\ntorqueacct.py: must be root to run this program!\n" + _NORM_bg)
   parser.parse_args(['-h'])
   sys.exit()

# Call help if there is no filename
#if _name_file or _path_name_file is None: 
if _name_file is None : 
    parser.parse_args(['-h'])
    sys.exit()

# Adusting PATH
# if cluster is passed 
if _cluster is not None:
    _path = "/var/spool/torque/" + _cluster + "/accounting/"

# Use glob to get the list os files using _path plus _name_file (multiple files)
_fnames_list = glob(_path + _name_file)

# Verify if glob returs a empty list 
if not _fnames_list:
    print(_RED_font + "\nThe file(s) was not found: " + _NORM_bg + _path + _name_file)
    print "Please verify if the filename(s) is/are correct!\n"
    sys.exit()

# if is CSV, set global var _choice
if args.csv:
   print "jobid;date;user;group;account;queue;node;ppn;cpus;ctime;etime;qtime;start;end;waittime;walltime;exit status;exec host;jobname;exit mensage"
   _choice="csv"


# Read(s) the file(s) and process it!
for _fname in _fnames_list:
    # set 0 to reset counts by day
    _jobcnt_a = _jobcnt_d = _jobcnt_c = _jobcnt = 0
    try:
        parse_status(_fname)
    except KeyboardInterrupt:
        print "\n\nInterrupted by user!!\n"
        sys.exit()

if _show_count:
    display_count()


sys.exit()

