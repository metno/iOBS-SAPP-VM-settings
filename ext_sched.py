#!/usr/local/bin/python -u

# Copyright 2005-2016 ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction

import os, sys
import time, datetime
import argparse
import re
import shutil

# SAPP internal modules
import utils
import settings as cfg
if os.environ.get('SAPP_POSTCONF'):
    execfile(os.environ.get('SAPP_POSTCONF'))

"""
build ext criteria and datetimes
repdates: based on ymd and cycle
ingdates: based on most recent <itv> wide valid window 
"""

def calc_dates(ymd_date,fam,item,cycle,itv,shift=0):
    """ calculates report and ingestion intervals   """
    
    EXT_WINDOW= {
        # target,cycle -> exec_hh,cycle_hh, cycle_repdate_delta1, cycle_repdate_delta2, shift 
        ('MACC','00'):   ('07:00', 0,-3,+3, 0),
        ('MACC','06'):   ('18:45', 6,-3,+3, 0),      
        ('MACC','12'):   ('19:00',12,-3,+3, 0),
        ('MACC','18'):   ('06:45',18,-3,+3,-24),
        ('DA1','00'):   ('04:00', 0,-3,+3, 0), # run at 4 am, from: 0-3h -> 21h previous day, to 0+3h -> 3pm current day
        ('DA1','06'):   ('10:00', 6,-3,+3, 0),      
        ('DA1','12'):   ('16:00',12,-3,+3, 0),
        ('DA1','18'):   ('22:00',18,-3,+3, 0),
        ('MS1','00'):   ('02:00', 0,-2,+2, 0),
        ('MS1','03'):   ('05:00', 3,-2,+2, 0),
	('MS1','06'):   ('08:00', 6,-2,+2, 0),      
        ('MS1','09'):   ('11:00', 9,-2,+2, 0),
	('MS1','12'):   ('14:00',12,-2,+2, 0),
        ('MS1','15'):   ('17:00',15,-2,+2, 0),
	('MS1','18'):   ('20:00',18,-2,+2, 0),
        ('MS1','21'):   ('23:00',21,-2,+2, 0),
	('DC1','00'):   ('13:45', 0,-3,+3, 0),
        ('DC1','06'):   ('14:00', 6,-3,+3, 0),      
        ('DC1','12'):   ('01:45',12,-3,+3, -24), # run at 1.45 am, from 09h to 15h of prev day
        ('DC1','18'):   ('02:00',18,-3,+3, -24),
        ('OCEA','12'):  ('13:30',13,-cfg.retention['OCEA']*24,0, 0),
        ('GRIB','12'):  ('23:50',12,-1,+1, 0), # actually every 4 hours ... why ?
        ('GRIB','00'):  ('11:50', 0,-1,+1, 0), # actually every 4 hours ... why ?
    }

    # we need to shift window for SST/ICE daily datasets ...
    if item in ("GRST0001","GST40001","GSST0001","OSST0001","OSNE0001"):
        if int(cycle)==0:
            shift=-int(cycle)-36
        else:
            shift=-int(cycle)-12 
    elif item == "SSTG0001":
        shift=-int(cycle)-24
    elif item == "ICEG0001":
        if int(cycle)>=12:
            shift=-int(cycle)
        else:
            shift=-int(cycle)-24 
    elif item in ("S4KN0001","SNOW0001"):
        shift=-int(cycle)
        
    shift+= EXT_WINDOW[(fam,cycle)][4]   
       
    now=int(time.time())
    
    # for MS1 ext, check if start of ext time window (r1) is in the future -> go back one day
    if fam=='MS1' and datetime.datetime.fromtimestamp(now)<ymd_date + datetime.timedelta(hours=EXT_WINDOW[(fam,cycle)][1]+EXT_WINDOW[(fam,cycle)][2]+int(shift)):
        shift-=24
    
    if itv<=0:
        itv=30 # use a default
    i2=datetime.datetime.fromtimestamp(now-now%(itv*60))
    i1=i2-datetime.timedelta(minutes=itv)
       
    ymd_fname=ymd_date + datetime.timedelta(hours=EXT_WINDOW[(fam,cycle)][4])
    r0 = ymd_date + datetime.timedelta(hours=EXT_WINDOW[(fam,cycle)][1]+int(shift))
    r1 = ymd_date + datetime.timedelta(hours=EXT_WINDOW[(fam,cycle)][1]+EXT_WINDOW[(fam,cycle)][2]+int(shift))
    r2 = ymd_date + datetime.timedelta(hours=EXT_WINDOW[(fam,cycle)][1]+EXT_WINDOW[(fam,cycle)][3]+int(shift))
    if fam=='DA1':
        im30=r2+datetime.timedelta(minutes=30) # DA1: when using m30, ingestion dtime limit is 30 minutes after r2: ie DA00 -> (21,03) -> da00m30.ing<=03.30, da00.ing>03.30
    else:
        im30=datetime.datetime.fromtimestamp(now)-datetime.timedelta(minutes=30) # DC,MACC:  ingestion dtime limit is now-30
    dtimes=[d.strftime('%Y-%m-%d %H:%M:%S') for d in (i1,i2,r0,r1,r2)]
    return dtimes,i1,i2,r0,r1,r2,ymd_fname,im30


parser = argparse.ArgumentParser()
req = parser.add_argument_group('required arguments')
req.add_argument    ('--mode', required=True,            help='print|run, required')
req.add_argument    ('--start', required=True,           help='yyymmdd|today, required')
parser.add_argument ('--qname',  default='da',           help='query template yo use (see ext_dispatcher), def=da')
parser.add_argument ('--stop',  default='today',         help='yyymmdd|today, def=today')
parser.add_argument ('--step',  default=1, type=int,     help='in days, def=1')
parser.add_argument ('--cycles',  default='00,06,12,18', help='list of cycles hh, def=00,06,12,18')
parser.add_argument ('--family',  default='DA1',         help='ext family,  def=DA1')
parser.add_argument ('--shift',  default=0, type=int,    help='window shift in hours, ie -36, def=0')
#parser.add_argument ('--pp',     default='1',            help='happ package (for migration purposes, to become obsolete) def=1')
req.add_argument    ('--item',  required=True,           help='ext item ie BUFR0001|any, , required')
parser.add_argument ('--proc_itv', default=0, type=int,   help='procdate interval criteria, ie  0 (to skip) or 10|30|60 minutes, def=0')
req.add_argument    ('--m30', required=False, default=0, type=int, help='set to 0,1,2 -> 1:@min30, 2:@cutoff, 0:default (no min30)')
opts = parser.parse_args()

ymd1=opts.start  #ymd='20100225' # date when the sched was supposed to run  (not the YMD to appear in the fname !!!!)
if ymd1=="today":
    ymd1=time.strftime('%Y%m%d') 
ymd_date = datetime.datetime(int(ymd1[0:4]), int(ymd1[4:6]), int(ymd1[6:8]), 0, 0, 0 )

ymd2=opts.stop #ymd='20100225'
if ymd2=="today":
    ymd2=time.strftime('%Y%m%d')
ymd2_date = datetime.datetime(int(ymd2[0:4]), int(ymd2[4:6]), int(ymd2[6:8]), 0, 0, 0 )

ext_exe=cfg.scriptdir+'ext_dispatcher.py'

# check ecp option !!!
# activate ecfs_copy if ecp option in extraction definition  and ....  
sql="""SELECT count(*) as ecp FROM extraction WHERE ext_family='%s' and ext_item='%s' and options like '%%ecp%%' and active=1"""%(opts.family,opts.item) 
_ret, rows = utils.db_query(sql)
ecfs_copy=int(rows[0]['ecp'])
      
ret=0
while ymd_date<=ymd2_date:
    for cycle in  opts.cycles.split(','):
        if opts.qname=='da' or opts.qname=='msbkup' or opts.qname=='ocea' or opts.qname=='grib':
            ymd=ymd_date.strftime('%Y%m%d')
            (i1,i2,r0,r1,r2),di1,di2,dr0,dr1,dr2,ymd_fname,im30 =calc_dates(ymd_date,opts.family,opts.item,cycle,opts.proc_itv,opts.shift)    
            qpar="""E.ext_family="%s" AND E.hh LIKE "%%%s%%" AND R.repdate > "%s" AND R.repdate <= "%s" """%(opts.family,cycle,r1,r2)

            if opts.item !='any':
                qpar+="""AND E.ext_item="%s" """%(opts.item)
                if opts.family!='MS1':
                    ext_out='%s%s%s.%s'%(opts.item,dr0.strftime('%Y%m%d'),cycle,opts.family)
                else:
                    ext_out='%s%s%s'%(opts.item,dr0.strftime('%Y%m%d'),cycle)                    
            else:
		ext_out='any%s%s'%(dr0.strftime('%Y%m%d'),cycle)
            if opts.proc_itv>0:
                ext_out='%s_%s_%s_%s.%s'%(opts.item,ymd,di1.strftime('%Y%m%d%H%M') ,di2.strftime('%Y%m%d%H%M'),opts.family)    
                qpar+= """ AND RFS.ingdate > "%s" AND RFS.ingdate <= "%s" """%(i1,i2)
            
            if opts.item in ("GRST0001","GST40001","GSST0001","OSST0001","OSNE0001"):
                ext_out='%s%s%s.%s'%(opts.item,ymd_fname.strftime('%Y%m%d'),cycle,opts.family)                                                       
            
            if 'split' in cfg.ext_m30 and opts.m30>0:
                print "ext_m30 setting is ON (%s), running part %d of the extraction ...."%(cfg.ext_m30,opts.m30)  
                if opts.m30==1:
                    ext_out+='.1.DAT'
                    qpar+=""" AND E.options LIKE "%%m30%%" """
                    if 'DA1' in opts.family:
                        qpar+=""" AND RFS.ingdate <= "%s" """%im30
                elif opts.m30==2:
                    ext_out+='.DAT'
                    if cfg.ext_m30=='split_quick':
                        qpar+= """ AND RFS.ingdate > "%s" """%im30
            else:
                ext_out+='.DAT' 
                                                  
            if cfg.ext_m30=='owrite':
                print "ext_m30 setting == 'owrite', extraction will overwrite existing files ..."
            elif cfg.ext_m30=='off' and opts.m30==1:
                print "ext_m30 setting is off, skipping minus30 extraction ...."
                sys.exit(0)              
  
        if ecfs_copy>0 and ( ('db' in cfg.ext_ecp_mode) or ('regex' in cfg.ext_ecp_mode and re.search(cfg.ext_ecp_in_regex, ext_out) ) ):
            ecfs_copy=1
        else:
            ecfs_copy=0   
        
        ext_cmd="""%s --run --qname=%s --out=%s --m30=%d --ecp=%d --qpar='%s' """%(ext_exe,opts.qname,ext_out,opts.m30,ecfs_copy,qpar)
        if cfg.ext_m30=='split_safe' and opts.m30==2:
            ext_cmd+="""--min_procdate='%s'"""%im30 # NB this won't be applied if m30 option is not set at ext_item level 
        if opts.mode=='run':
            print "running: %s"%ext_cmd
            ret=os.system(ext_cmd)
            if opts.item=="BTEM0001":  #to remove soundings with too many levels that make bufrdc toools crash
                ret=os.system('/sapp/local/bin/recover_bufr.sh %s'%ext_out)    
            print "ret: %s"%ret
        elif opts.mode=='print':
            print ext_cmd
        
    ymd_date+=datetime.timedelta(opts.step)     

try: # copy extractions to cope outbox
    if re.search(cfg.ext_cope_in_regex, ext_out):
        shutil.copy(ext_out, cfg.outputdir+'cope/'+ext_out)   
except Exception:
    print "ext_cope_in_regex error"

if int(ret) != 0:
    sys.exit(1)
