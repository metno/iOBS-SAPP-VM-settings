#!/usr/local/bin/python -u
# Copyright 2005-2016 ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction

#  Local settings, this file (as any local*) is NOT under git control  and it is imported by settings
import getpass

#################
## Paths
#################
hostid=1  # vsapp only
sapp_user=getpass.getuser()

cluname='vsapp'

cluster={}
cluster['lxpp','gpfs']='/sapp/'
cluster['lxpp','master']='lxppdev'
cluster['lxpp','nodes']=[0,1,2]

cluster['sappa','gpfs']='/sapp/'
cluster['sappa','master']='sappa'
cluster['sappa','nodes']=[0,1,2,3]

cluster['sappb','gpfs']='/sapp/'
cluster['sappb','master']='sappb'
cluster['sappb','nodes']=[0,1,2,3]

cluster['vsapp','gpfs']='/sapp/'
cluster['vsapp','master']='vsapp02'
cluster['vsapp','nodes']=[2,]

cluster['monitor']=(cluname,) 	# used by create_suite, which clusters to be monitored

main_clu=   'vsapp'
backup_clu= 'vsapp'

mon_clu_list=           (cluname,)   # list of clusters to be monitored in clu*check actions

gpfsdir=    cluster[cluname,'gpfs']
dbdir=      gpfsdir+'mysql/msb/master/'
basedir=    gpfsdir+'git/%s/'%sapp_user
sappdir=    basedir+'sapp/'
djdir=      gpfsdir+'dj/acq/'
djport=     '8000'

ukmftpdir=  sappdir+'../ukmftp/'        # TODO move to common pathnames
datadir=    sappdir+'inbox/'            # files in <source>/data subfolder, (TestDataset, not cleaned by crontab jobs on lxppdev)
workdir=    sappdir+'work/'             # <deqc>/<source>/YYYYMMDD_xxxxx dirs are created for each processing job
procdir=    sappdir+'processed/'        # <deqc> dirs, report repository
outputdir=  sappdir+'outbox/'           # extraction output (for scp/ftp distribution)
archdir=    sappdir+'archive/'          # YYYYMMDD/<source> archive (based on mdate == arrival time)
ecfsdir=    sappdir+'ecfs/'             # local  dir to be used for ecfs archiving 
ecfdir=     sappdir+'ecflow/'
logdir=     sappdir+'logs/'             # host-task related logfles like acq|proc|ext.<hostid>.log
scriptdir=  sappdir+'scripts/'          # python scripts
convdir=    sappdir+'conv/bin/'         # converter binaries
bkdir=      sappdir+'backup/'           

bindir=     sappdir+'preproc/'          # deqc binaries
bindatdir=  bindir +'dat/'              # dat files used by preproc

crextabdir= bindir+'tables/crex/'       # crex tables
bufrtabdir= bindir+'tables/bufr/'       # bufr tables,  ie on lxppdev, /gpfs/lxpp/lxppdev/p4/sapp/main/preproc/tables/bufr/000400.mod/
proc_bufrtables_db= True                # True to compose bufrtables path as bufrtabdir+DB.deqc.tables value; if False just use bufrtabdir as is ( must be a valid path !!!)

anaconda2='/usr/local/apps/anaconda2/bin/'
anaconda3='/usr/local/apps/anaconda3/bin/'
eccodes_lib='/usr/local/apps/eccodes/current/lib/python2.7/site-packages/'

ecflow_lib= '/usr/local/apps/ecflow/current/lib/python2.7/site-packages/'
ecf_port='3141'
ecf_home=ecfdir+'ecflow_server/'

acq_ecfs=               'symlink,tar,ecp'
acq_archive=            '' # set to 'copy' or 'symlink' incoming,valid  files under archive dir (see local.py) #obsolete
acq_ecfs_root='ectmp:/emos/oparch/sapp/msg/' # ecfs root path for incoming messages (provided ds has ecp or ectar option)

### Data/Metadata Retention rules (on datasources or deqc or extitems)
retention={}  
retention['egrr_gts']=2 # days
retention['edzw_gts']=2 # days

retention['OCEA']=2 # days


####################################

#retention['GRST0001']=6 #  refers to DB/metadata retention, else add 'file' to specify outbox FS retention days
retention['GRST0001','file']=2 # outbox file n.days, metadata fallback to retention['default',4]  
retention['IASB0001','file']=1
retention['IASI0001','file']=1
retention['IAFB0001','file']=1
retention['IASA0001','file']=1
retention['SMOS0001','file']=1
retention['CRIT0001','file']=1

# fsitem type    1: gts. 2:nogts, 3:report, 4:ext
retention['default',1]=2 # gts days
retention['default',2]=2 # nongts days
retention['default',3]=2 # bufr reports days
retention['default',4]=1 # extraction days
retention['default',5]=1 # extraction days

# for these inboxes we want to apply retention to DB (fsitem) but apply max_inbox_ret_days to file retention ON FS 
# if you want to keep files in the inbox for long time (ie aeolus) DO NOT have ds in this list
force_max_inbox_ret_days_list=('egrr_gts','edzw_gts','ukmo_fc','ukmo_hc','sron_gosat_ch4','bremen_gosat_co2','oi_v2sst','crexnilu')
max_inbox_ret_days=    7       # max n. days to keep a file in any inbox (this overrides retention setting)
data_ret_days=         2       # default data retention in n. of days (obsolete)

################################################################################

### monitoring adjustments
rep_itv_adj_factor= 1.5   # multipl factor for mon thresholds -> 1.5 adds 50% to DB value
ing_itv_adj_factor= 1     # multipl factor for mon thresholds -> 2 adds 100% to DB value
mon_adj_factor_skip_list=('CGST',)      #list of deqc,conv that don't need mon thresholds adj factors
mon_check_apps_list=('proc_disp','acq_scan','mysqld_safe','supervisord','ecflow_serv','ecflow_logsvr','runserver',) # apps to be checked
ecf_check_apps_list=('supervisord','mysql_master','mysql_slave','ecflow_server','ecflow_log','acq_scanner','proc_dispatcher','django_web')
mon_alert_list=('CGST','GRST','SYNO','TEMP','edzw_gts','sst_ci','egrr_gts',) # list of ds,conv,deqc that are return CRITICAL level error in mon/track and may require immediate on call
mail_on_state_change=   '(CAEO|AEOL|CA2C|aeolus_).*' # regex to enable monitor.py *track mail on node state change
mon_check_db=           False   # set to enable db checks

mon_mail_list=          ('macz@localhost',)   # list of recipients for monitor warns/notifications 
mon_mail_list=          ('macz@localhost',)   # list of recipients for monitor warns/notifications 

mon_mail_sender=        'macz@localhost'      # monitor warns/notifications sender 
mon_load_events=        ('wmo1','clu_ps_check','acq_check','proc_check')         # events to be tracked into event table 
ecf_load_events=        ('ext_check','clu_ps_check')      # ecflow monitored events

###workers
acq_max_workers=        1       # Max numbers of parallel acq workers to be forked: workers perform indexing by moving files from data into ingested subdir. 
proc_max_workers=       3     # Max numbers of parallel Proc workers to be forked: compete to process ingested message DB records by updating their status to 'assigned' 

### fname filtering
acq_ds_fname_in_regex={} # restart scanner to read new config !
acq_ds_fname_in_regex['edzw_gts']='Z_.*' # old gts fname  edzw.*
acq_ds_fname_in_regex['hrp']='qw.*' # new fname will be 'um.*'


proc_no_stdbuf=False   # set to enable stdbuf filter and  proc_no_stdbuf_list (False on vsapp)
proc_skip_deqc_list=() # ('GRIB','GFDB') deqcs to be skipped during load jobs

### deqc env vars
deqc_env={}
deqc_env["IACX"]=("WAIT_TIME=45",)
# adaptation for Sentinel5p SO2 different h values
deqc_env["D5S0"]=("ENV_HEIGHT=0",)
deqc_env["D5S1"]=("ENV_HEIGHT=1",)
deqc_env["D5S7"]=("ENV_HEIGHT=7",)
deqc_env["D5SF"]=("ENV_HEIGHT=15",)

proc_cope_list=  () # run COPE pipeline for these deqc at proc time
proc_cope_odbload= False
ext_cope_deqc_list= ('ACMR','AIRC','AIRS','ALTI','ALWS','AMDA','AMDW','AMSA','AMSB','AMSE','AMSG','AMSU','AMV3','AMV8','ARP1',
	'ASEL','ASLB','ASR3','ASR8','ATAP','ATEU','ATMS','ATOV','AUTO','AVHA','AVHB','AVHM','AVHN','B002','B003','B004','B005',
	'B006','B012','B06Y','BSSH','BSSY','BTEM','BTEY','BUOY','BUYY','CMWN','CNOW','COMV','CORI','CRIT','CRYO','CSRG','EASA','EGOM','EMER',
	'EMIP','EMSG','ERA2','ESCI','ESCK','EUWV','FY3A','FY3B','FY3H','FY3I','FY3T','G2TO','GCAR','GNOS','GO15','GOCS','GOES','GOGA','GPM4','GPMI',
	'GRAB','HIMA','HIRB','HIRS','IAS1','IAS2','IAS3','IAS4','IN3D','J2EO','J2NB','JASO','MASR','MET7','META','MHSA','MHSB','MHSE',
	'MLOZ','MODW','MONW','MTSA','NOMI','OMNP','OCEA','OSCA','PGPS','PILO','RADA','RADO','SAPH','SBU8','SBUV','SHIP','SMIU','SSBT','SYNO','SMOS',
	'TEMP','TOZO','TRM7','USRR','VIRS',
    'HIR1','HIR2','AMS1','AMS2','AMS3','AMS4','AMS5','AMS6','AMS7','AMS8','MHS1','MHS2','MHS3','MHS4','MHS5','MHS6','MHS7',) # disabled surf_anal stuff: S4V3:165 (S4KN) , GRST:26, USRR:125 , storm:TRO1,B007:31 (stype not in odbgov)

ext_cope_stype_list=(1,3,9,11,13,19,21,22,23,26,28,31,49,53,54,55,57,60,87,89,91,95,96,101,102,103,106,109,110,
	111,112,121,122,123,125,127,129,138,139,140,141,142,143,144,145,146,147,149,154,155,156,165,170,172,176,178,180,
	181,182,189,190,201,202,203,206,210,211,212,213,214,216,217,218,224,240,250)
proc_deqc_stype_check_groups={}
#proc_deqc_stype_check_groups['BSSH',170]=20 # to tackle issue with north korean station vs add_bias

### Routing
acq_bufr_template_index=True	#set to read undexpandedDescriptors from input BUFR messages
acq_dropsonde_regex=''# or '61616.+AF3'
acq_route_deqc_in_regex=  '.*'        # regex for deqc to be ROUTED -> what deqcs we want to index (eg 'OCEA')
reroute={}  ### when multiple DEQC have to be associated to a single msg
reroute['META']=['META','AUTO']
reroute['B004']=['B004','ACMR']
reroute['AMDA']=['AMDA','AMDW']
reroute['BUYY']=['BUYY','BUY2']
#reroute['egrr_gts','311010']='AMDW' #a dded this since IUAX01 EDZW carries both B004 and AMDW data
#reroute['edzw_gts','311010']='AMDW' #a dded this since IUAX01 EDZW carries both B004 and AMDW data
#reroute['BSSH']=['BSSH','BSSY']
#reroute['SYNO']=['SYNO','SYN1']  using deqc_route now
#reroute['SYNO']=['SYN1','SYN2']  used to compare two different versions of SYNO deqc (precipitation fix)

master_node_cmd='echo 0' # cmd exit code has to return 0 for master nodes

############ DB #################
# master
host, port, user, passwd, db="vsapp02",5707,"msandbox","msandbox","sapp_oper" 

# slave   
rhost, rport, ruser, rpasswd, rdb="localhost",5708,"msandbox","msandbox","sapp_oper" 

#extraction
ext_m30= 'split_safe'   # set to 'split_safe|split_quick' to enable minus30 split extraction mode, 'owrite' to run same extraction at t0-30 and t0 (overwriting files), 'off' to skip t0-30 ext.
                        # ext_m30=='split_safe' sets min_ingdate so that part2 only contains files arrived in the t0-30,t0 interval
                        # ext_m30=='split_quick' does not add min_ingdate constraint -> part2 may contain reports ingested before t0-30 (hence duplicated)

ext_from_happ={}  ### when multiple DEQC have to be associated to a single msg
ext_from_happ['BICE0001']='pp1'
ext_fallback_in_regex='(GRST|GST4).+(DC|DA).+DAT'    # if ext is empty and regex on fn_del passes, try to link last non empty extraction (req for OSTIA/GRST)

#extraction stype:station filter, regex defines ident to be blocked for a given reporr subtype
ext_stype_ident_out_regex={}
#ext_stype_ident_out_regex[170]='470[1234567].' # block north korea bufr synops
ext_cope_dump_rid=          False   # set to enable pickle dump of report ids used in same name ext file
ext_write_max_block_size=   1024*1024*100 # flush ext buffer if size greater than this 

############ ECFS archiving ###########
### for main cluster (ie sappa) use db config (ecp option). 
### for backup_clu, to avoid double ecp, ignore db and ecp only what defined by ext_ecp_in_regex nad acq_ecp_in_list exceptions

ext_ecp_in_regex='NONE'         #'(MWTS|ALTI).+(DC|DA).+DAT' # regex to tag an extracted file for ecfs copy (see sapp_cmd.py ecfs_ext_ecp() ). Alt use  DB.extraction.options='ecp'
ext_ecp_mode='db'
ext_ecp_test_suffix=() #add ext names (first 4 chars) to be copied as .TEST (instead of .DAT), ie to ecp sappb TEST data alongside sappa .DAT operational
acq_ecp_in_list=('NONE',)  # () list of datasource substrings to tag an ingested file for ecfs copy (see sapp_cmd.py ecfs_ext_ecp() ). Alt use   DB.datasource.options='ecp'
acq_ecp_mode='db'

#sapp cluestr
#if cluster == main_clu:
#    ext_ecp_mode='db' 
#    acq_ecp_mode='db'
#else:
#    ext_ecp_mode='regex'       # csv list of options: db:use the ecp flag in extraction table, regex: use the ext_ecp_in_regex 
#    acq_ecp_mode='list'        # csv list of options: db:use the ecp flag in datasource table, list: use the acq_ecp_in_list

############ scp/backup to external servers #######################
backup_repo=     ''
acq_scp_data=    ''    # set to scp backup incoming data to alt/backup host inbox 
acq_scp_data_list=   ()# ('edzw_gts',)

#repro
repro_source_list=('gts_repro',) # ie ('egrr_gts',)
