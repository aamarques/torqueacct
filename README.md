# torqueacct
Parses the Torque accounting files to extract some importants fields.

Use as default directory, /var/spool/torque/server_priv/account, for accounting files. 

This can be changed in code.

For my use, I put a "-n or --cluster" to change a little the directory of accounting files. 
That is because I have many clusters to manage and put all accounting logs into /var/spool/torque/<name_cluster>/accounting.

If you want to use it, fell free to change.


