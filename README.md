# torqueacct
Parses the Torque accounting files to extract some importants fields.

Use as default directory, /var/spool/torque/server_priv/account, for accounting files. 

This can be changed in code.

For my use, I put an argument ("-n or --cluster") to change a little the directory of accounting files. 
That is because I have many clusters to manage and put all accounting logs into /var/spool/torque/<name_cluster>/accounting.

If you want to use it, fell free to change.


Parses the Torque accounting files to extract some importants fields.

    usage: torqueacct.py [-h] [-l FILENAME] [-j JOBID] [-u USERNAME] [-q QUEUE]
                         [-n CLUSTER] [-d] [-t] [-f | -c] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      -l FILENAME, --log FILENAME
                             The input log file to be parsed. REQUIRED
      -j JOBID, --job JOBID
                              Search for a specific JobID
      -u USERNAME, --user USERNAME
                            Search for a specific username
      -q QUEUE, --queue QUEUE
                            Search for queue name
      -n CLUSTER, --cluster CLUSTER
                            Name of the cluster 
      -d, --del             Shows the Deleted results
      -t, --segs            Shows time fields in seconds
      -f, --csv             Shows the output results in a CSV format. DO NOT USE
                            with --count
      -c, --count           Shows only the Total count of results. DO NOT USE with
                            --csv
      -v, -V, --version     show program's version number and exit



### Here are some examples of filename use
--------------------------------------

    torqueacct.py -l 20170401            -> This will parse this date
    torqueacct.py -l "201704*"           -> This will parse all accounting files starting with 201704*. 
    torqueacct.py -l "2017*"             -> This will parse all accounting files starting with 2017*
    torqueacct.py -l 20170401 --csv      -> This will parse this date and output in CSV format
    torqueacct.py -l 20170401 -d --csv   -> This will parse this date, only for deleted jobs and output in CSV format

Note: When you are using wildcard, you must put it between quotation marks ("") 
      because unix shell expand it before to pass it to program.

You can mixe up all parameters to extract information you need
                     
### Attention:

The default directory is /var/spool/torque/server_priv/accounting

The option '-n or --cluster' is used to parse the log file in other directory where I put log files from many clusters.

In my case, /var/spool/torque/<CLUSTER NAME>/accounting

Maybe you will need to change this.


