#!/usr/local/bin/python -u
# Copyright 2005-2016 ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction

#  Settings for acq,proc,ext SAPP python components

import collections

import logging
from const import *
from local import *

#################
# Misc
#################
check_settings_change = True    # settings.py runtime check and reload (if changed). check performed at the end of each session.
mon_gfps_max_perc=      85 # max perc of /sapp disk usage; above this threshold a warning is raised 
db_retries=     3       # Max n. of attempts to retry a failed sql transaction (ie due to deadlock)
db_sql_dump=    False   # to dump sql run by db_exec

#################
## Logging
#################
# Basic logging configuration; LogRecord attributes also available to formatter: %(fileName)s %(funcName)s %(lineno)d  %(processName)s %(lineno)d
# console handler logging level: INFO, file handler level: DEBUG
acq_loglevel=       logging.DEBUG
proc_loglevel=      logging.DEBUG
ext_loglevel=       logging.DEBUG
def_loglevel=       logging.DEBUG
log_fh_change=      True      # True to create a new logfile when size greater than log_max_size
log_uniq=           False     # True to filter repeated instances of same log msg (within a session) ! may filter out useful "repeated" msgs ie progress reports (xx done, yy failed ,... ) 
log_max_size=       10*1024   # max log size in KB before rotating, used if log_fh_change is set
db_sql_dump=        False   # to dump sql run by db_exec

####################################################################################
## Acquisition / Archiving
###################################################################################

### Admin
acq_split=              False   # to split inbox sources amongst workers (by source id)
acq_walkfs_test=        False   # if True acq walks datadir only to print filenames and skip any other task
acq_fork_itv=           1       # interval in secs between successive forks, for staggered fork at startup (to reduce move lock errors)
acq_msgdate_th_min=     30      # Tolerance in minutes for gts "msgdate in the future" warning 
acq_rlearn=             True    # Enable Route learn (for selected datasourced like gts ones having 'rlearn' in options field)
acq_uncompress_all=     False   # uncompress any compressed file without need of datasource 'unc' option         
acq_ext_uncompress_list=('.bz','.bz2','.gzip','.z','.zip','.gz')  # uncompress extensions (case insensitive)
acq_uncompress_keep=    True    # keep a copy of files to be uncompressed into ingested dir (to allow recovery)
acq_addts=              True    # set to enable adding tstamp to fnames during ingestion (if datasource has otpions 'addts' )
acq_gts_min_size=       60      # min GTS msg size to be checked for nil 
acq_empty_wait=         180     # wait time in secs for an emtpy file to be written, before being moved to errdir
acq_check_empty=        True    # Set to move empty (0 bytes) files into error dir
acq_max_size=			4294967295 # 4GB as we use INT for offset/size fields in DB ... alt use BIGINT
# if True, move error/ingested/archived files into data folder, to be resubmitted to acq.scanning
acq_resubmit_error=     False
acq_resubmit_ingested=  False

### User
acq_walk_dir_max_yield= 1000    # if not 0, is the max n. of files to be returned by filewalker ** for each ** datasource 
acq_get_bufrtype=       True    # retrieve dataCategory,dataSubCategory bufr key (for tt=I* and to perform B0xx deqc routing)
acq_poll_itv=           20      # polling interval in secs between scanning sessions (and forking); if set to 0, just exit at the end of scan

# acq SKIP filters: regex on input sources,filenames,  in_: include condition , ex_: exclude condition
# if check fails, file STAYS in original dir and is not moved into error dir -> rescanned in following session 
acq_fname_ex_regex=     '^\.|.tmp$' # .* or .tmp file could be incomplete,running FTP transfers ...  skip
acq_fname_in_regex=     '.*'        # include fname pattern
acq_source_in_regex=    '.*'      # include source pattern (example of "negative form" see "^((?!REPRO).)*$"
acq_mod_date_in_regex=  '.*'        # include file mod.date pattern  ('%Y-%m-%d %H:%M:%S')

###########################################################################################
## Processing/Reprocessing
###########################################################################################

### Admin
proc_noparallel_list=   ('TEMP','SHIP','PILO','B004','ACMR','AMDA','AIRC','ARP1','BUOY','OCEA','CREX') # DEQCs that cannot run in parallel mode (ie cause they write to a shared index dat file like *MERGE* or *POS*)
proc_grib_list=         ('GRIB','GFDB','GFD1','GRIS') # GRIB deqcs
proc_skip_dbload_list=  ('EURN','CA2C') # non BUFR,GRIB output, skip dbload
proc_delay_start_list=	('CAEO',) # staggered start (delay 2 secs) for CAEO to avoid REP_2B fname clash
proc_no_stdbuf_list=    ('CRLG','CAB6','CAT6') # disable stdbuf for these conv/deqcs 
proc_saveblob_list=     ()      # 'all' or list of DEQC for which we want to save report/bufr into DB as blob (TBC)
proc_lock_timeout=      120     # lock timeout for deqc in  proc_noparallel_list
proc_mode=          'systematic'# systematic (live data processing), repro ( ie working on _ECFSREPRO )
proc_remote_exec=   'local'     # 'local','remote_only' or 'remote_and_local': run remote processing on HP cluster (bilbo) and retrieve it as hp.out.bufr into workdir for cmp purpouse  
proc_sub_poll_itv=  .0001       # sleep interval to check stdout on Popen subprocess in submit job ... don't go above 0.001 secs (it becomes critical if deqc out has >10000 lines)
proc_cleanworkdir=  False       # clean temp work dir when processing finished (completed or not)
proc_msg_cont=      False       # future: eval/decode/analyze message vs report parameters 
proc_check_cccc=    False       # To enable checks on CCCC conditions (taken from DEQC table)
proc_data_symlink=  True        # Use symlink to datafiles (to have portable workdirs)
proc_check_file_avail= True     # set to skip creating job for non existing files (ie old ones) and delete references to them from DB (fsitem)
proc_msg_dump=      False       # for debug, to have msgs in params.txt extracted into workdir as m.1 , m.2 , ..., m.n 
proc_min_year=      1950        # discard messages or reports with year(repdate) older than this
proc_check_temp_merge= True     # to enable check of TEMP merge files
proc_temp_merge_max_size= 1000*1000*1000 # TEMP merge files auto check , max size (1 GB, normally up to 50 MB)
proc_sanity_check='/usr/local/apps/eccodes/current/bin/bufr_count' # BUFR sanity check cmd , exit code must be 0 if bufr is OK. set to '' to skip
proc_unpack_check_cmd='/usr/local/apps/eccodes/current/bin/bufr_dump' # BUFR unpack check cmd , exit code must be 0 if bufr is OK. set to '' to skip
proc_unpack_check_deqc_list=('TEMP',) # list of deqcs for which we try an unpack before loading 

# optional bufr param decode
decode_param={}
#decode_param['SYN1']=['totalPrecipitationPast3Hours','totalPrecipitationPast6Hours','totalPrecipitationPast12Hours','totalPrecipitationPast24Hours']

### User
proc_deqc_job_limit= 10000     # Max num. of messages (fname+offset) considered for each DEQC when creating jobs queue (-> SQL limit)     
proc_deqc_job_limit_no_par= 100 # Use this limit for no_par/agg_limit:1 deqcs (TEMPs) to avoid session hogging due to too many individ msgs to be (re)processed sequentially.
proc_poll_itv=         20      # interval to wait once jobs queue is empty (processing finished) before fetching new jobs
proc_end_itv=         5      # interval to wait for workers to finish at the end of each session 
proc_recover_list=  (2,-5)  # was(2,-5) , set to list of status to be restored to "assigned" in order to restart processing ie "assigned,error"

# regex for messages to be considered in load jobs sql
proc_deqc_in_regex=     '.*'
proc_source_in_regex=   '.*'
proc_ttaaii_in_regex=   '.*'    # NB deqc independent
proc_cccc_in_regex=     '.*'    # NB deqc independent ( for deqc depend. setting use proc_check_cccc + DEQC.filter regex)
proc_work_prefix=       ''      # to easily find custom processing in workdir 

############################################################################################
## Extraction
############################################################################################

# Admin (do not change)
ext_order_by_repdate=       ('ATMS0001',) #'USRR0001'
ext_skip_dup=               "md5,bbb,merge,key" # csv string of criteria used to identify duplicated reports within an ext_item. Set to "" to extract ALL reports (no dupl filter)    
ext_skip_dup_deqc_list=     ('GRIB2007','GRIS2007')       # skip dupl filtering for following ext_items or deqcs
ext_skip_bbb_check_list=    ('AIRC','B004','ACMR','AMDA','TAMD') # for these decoders we want to skip the gts dupl filter when md5data is different
ext_skip_md5_check_list=    ('AAEN','ABEN','MHEN','MHSE','FY3A','FY3B','FY3C','ATEU','ATOV','ATAP','SMIS','SMIU','SMIN','AVHN','SMOS','AMSE','ASEH','ASEL','J2EO','J2NB') # for these (sat) deqc we don't want to extract reports that have same key but diferent mdf5 only due to minor data changes is subcentre
ext_merge_list=             ('TEMP','PILO') # add BTEM if you want biggest report only  in ; DAPP-46 filter out merge parts and only deliver the merged bufr (biggest size) TODO move to DB, deqc table
# list of deqc providing point/station observations (orig_id is not used as satellite id)
ext_station_deqc_list=      ('WAVB','CREX','SYNO','BSSH','BSSY','BSSW','BSUS','BTEY','SHIP','OCEA','META','AUTO','PILO','B002','B006','B06Y','TEMP','AIRC','ACMR','PGPS','AMDA','B004','BUOY','BUYY','BUUS','ARGO','SOIL','BTEM','CNOW','STUK','SYN1','ARP1','AMDW','TAMD','SNOW','TSNO','UHMC','CREY','TEAM','AMDY') 

ext_trunc_secs_deqc_list=   () # ('AIRC',) # for these deqc force repdate secs to 00 to avoid duplicate extractions (deqc adds deqc according to arrivale time -> 2 reps from egrr, edzw for AIRC ..)
ext_use_blob=               0   # Use reports' blob from DB when available (rather than read/seek report from FS)
ext_tracking=               False   # Set to check DB (delivery of Reports (rid) within Extractions (eid)) to avoid duplicate delivery
ext_write_empty=            True    # Set to create (zero sized) files even when no reports is extracted
ext_padding=                True    # to add zero padding at the end of EACH extracted report  ... needed by mars client
ext_max_padding_size=       2       # this is used in read_join for cope ext , to have single read for conecutive bufr data
ext_cope_itv=               10      # minutes between cope extractions and ext floor ( 10 -> ext windows are [0,10]. [10,20], ...)

# User
ext_overwrite=              True    # Set to force ovewrite of extracted files and del_reports (when re-running same ext)
ext_write_files=            True    # Set to have extraction files written to FS
ext_insert_rep_delivery=    ('da1') # list of ext_family ids (lowercase) to be tracked into report_delivery (da1 should be enough)
ext_insert_stats=           True    # Set to update DB (extraction stats)
ext_check_stats=            True    # Set to check last 10 days stats to trigger warning if ext_sapp count is out of range (+-20%)
ext_split_sep=              ','     # Separator for ext sel list; if you have ',' in your sql, use ':'
