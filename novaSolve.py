#!/usr/bin/env python2

#Amendments by Jim Hunt
#   Note: ammendments marked by <jim>...</jim>
#   V1 (23/11/2016)
#       Add "Pretty" format to JSON outputs
#       Add Get and Output Calibration option
#       Add set camera sensor pixel size option (must be set if Focal Length output required)
#       Add calculation of image focal length(mm)
#       Add Log levels (0=none, 1=brief, 2=full (default=0))
#       Add ability to set options from a settings.json file
#       Add RA and DEC conversion from deg to ddmmss
#       Rationalise Option names
#       Remove sdss and galex plot options because we don't have astrometry.util
#   V2.1.9  (10/04/2018)
#       Add Graphical User Interface

from __future__ import print_function
import os
import sys
import time
import base64
import optparse
import threading
from urllib2 import urlopen
from urllib2 import Request
from urllib2 import HTTPError
from urllib2 import URLError
from urllib import urlencode
from urllib import quote
from exceptions import Exception
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application  import MIMEApplication
from email.encoders import encode_noop
import json
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *
import signal, traceback

version = "V2.1.9"

def json2python(data):
    try:
        return json.loads(data)
    except:
        pass
    return None
python2json = json.dumps

class MalformedResponse(Exception):
    pass
class RequestError(Exception):
    pass

class Client(object):
    default_url = 'http://nova.astrometry.net/api/'

    def __init__(self,
                 apiurl = default_url):
        self.session = None
        self.apiurl = apiurl

    def get_url(self, service):
        writeLog(2, "get_url", "start process")
        writeLog(2, "get_url", "end process")
        return self.apiurl + service

    def send_request(self, service, args={}, file_args=None):
        '''
        service: string
        args: dict
        '''
        writeLog(2,"send_request", "start process")

        if self.session is not None:
            args.update({ 'session' : self.session })

#        writeLog(0, "proc",'Python:', args)
#        json = python2json(args)
#        writeLog(0, "proc",'Sending json:', json)
#        url = self.get_url(service)
#        writeLog(0, "proc",'Sending to URL:', url)
        json = python2json(args)
        url = self.get_url(service)
        writeLog(0, "send_request",'Sending request')
        writeLog(1, "send_request",'Python: ' + str(args))
        writeLog(1, "send_request",'Sending json: ' + str(json))
        writeLog(1, "send_request",'Sending to URL: ' + str(url))
        if opt.gui:
            gui_up_stat("sending: " + url)

        # If we're sending a file, format a multipart/form-data
        if file_args is not None:
            m1 = MIMEBase('text', 'plain')
            m1.add_header('Content-disposition', 'form-data; name="request-json"')
            m1.set_payload(json)

            m2 = MIMEApplication(file_args[1],'octet-stream',encode_noop)
            m2.add_header('Content-disposition',
                          'form-data; name="file"; filename="%s"' % file_args[0])

            mp = MIMEMultipart('form-data', None, [m1, m2])

            # Make a custom generator to format it the way we need.
            from cStringIO import StringIO
            from email.generator import Generator

            class MyGenerator(Generator):
                def __init__(self, fp, root=True):
                    Generator.__init__(self, fp, mangle_from_=False,
                                       maxheaderlen=0)
                    self.root = root
                def _write_headers(self, msg):
                    # We don't want to write the top-level headers;
                    # they go into Request(headers) instead.
                    if self.root:
                        return
                    # We need to use \r\n line-terminator, but Generator
                    # doesn't provide the flexibility to override, so we
                    # have to copy-n-paste-n-modify.
                    for h, v in msg.items():
                        print(('%s: %s\r\n' % (h,v)), end='', file=self._fp)
                    # A blank line always separates headers from body
                    print('\r\n', end='', file=self._fp)

                # The _write_multipart method calls "clone" for the
                # subparts.  We hijack that, setting root=False
                def clone(self, fp):
                    return MyGenerator(fp, root=False)

            fp = StringIO()
            g = MyGenerator(fp)
            g.flatten(mp)
            data = fp.getvalue()
            headers = {'Content-type': mp.get('Content-type')}

        else:
            # Else send x-www-form-encoded

#            data = {'request-json': json}
#            print('Sending form data:', data)
#            data = urlencode(data)
#            print('Sending data:', data)
            data = {'request-json': json}
            writeLog(1, "send_request",'Form data: ' + str(data))
            data = urlencode(data)
            writeLog(1, "send_request",'Sending data: ' + str(data))

            headers = {}

        request = Request(url=url, headers=headers, data=data)

        f = urlopen(request, timeout=opt.url_timeout)
        txt = f.read()

#            print('Got json:', txt)
#            result = json2python(txt)
#            print('Got result:', result)
#            stat = result.get('status')
#            print('Got status:', stat)
        result = json2python(txt)
        writeLog(1, "send_request",'Got json: '+ str(txt))
        writeLog(1, "send_request",'Got result: ' + str(result))
        stat = result.get('status')
        writeLog(0, "send_request",'Got status: ' + str(stat))
        if opt.gui:
            if stat == None:
                stat = "waiting in queue"
            gui_up_stat("image: " + stat)
        if stat == 'failure':
            if opt.gui:
                stat = "image: solve failed"
                gui_up_stat(stat)
            raise RequestError(stat)
        if stat == 'error':
            errstr = result.get('errormessage', '(none)')
            if opt.gui:
                gui_up_stat('error: message from server - ' + errstr)
            raise RequestError('server error message: ' + errstr)
        writeLog(0, "send_request","return result: " + str(result))
        writeLog(2, "send_request", "end process")
        return result

    def login(self, apikey):
        writeLog(2, "login", "start process")
        args = { 'apikey' : apikey }
        result = self.send_request('login', args)
        gui_up_stat("login success as " + str(result.get('message')))
        sess = result.get('session')
        writeLog(1, "login",'got session: ' + str(sess))
        writeLog(2, "login", "end process")

        if not sess:
            if opt.gui:
                gui_up_stat('error: no session identifier received from server')
            raise RequestError('no session in result')
        self.session = sess
        writeLog(2, "login", "end process")

    def _get_upload_args(self, **kwargs):
        writeLog(2, "_get_upload_args", "start process")
        args = {}
        for key,default,typ in [('allow_commercial_use', 'd', str),
                                ('allow_modifications', 'd', str),
                                ('publicly_visible', 'y', str),
                                ('scale_units', None, str),
                                ('scale_type', None, str),
                                ('scale_lower', None, float),
                                ('scale_upper', None, float),
                                ('scale_est', None, float),
                                ('scale_err', None, float),
                                ('center_ra', None, float),
                                ('center_dec', None, float),
                                ('radius', None, float),
                                ('downsample_factor', None, int),
                                ('tweak_order', None, int),
                                ('crpix_center', None, bool),
                                # image_width, image_height
                                ]:
            if key in kwargs:
                val = kwargs.pop(key)
                val = typ(val)
                args.update({key: val})
            elif default is not None:
                args.update({key: default})

#        print('Upload args:', args)
        writeLog(1, "_get_upload_args",'return args: ' + str(args))
        writeLog(2, "_get_upload_args", "end process")
        return args

    def url_upload(self, url, **kwargs):
        writeLog(2, "url_upload", "start process")
        args = dict(url=url)
        args.update(self._get_upload_args(**kwargs))
        result = self.send_request('url_upload', args)
        writeLog(2, "url_upload",'return result: ' + str(result))
        writeLog(2, "url_upload", "end process")
        return result

    def upload(self, fn, **kwargs):
        writeLog(2, "upload", "start process")
        args = self._get_upload_args(**kwargs)
        f = open(fn, 'rb')
        result = self.send_request('upload', args, (fn, f.read()))
        writeLog(2, "upload",'return result: ' + str(result))
        writeLog(2, "upload", "end process")
        return result

    def submission_images(self, subid):
        result = self.send_request('submission_images', {'subid':subid})
        return result.get('image_ids')

#    def overlay_plot(self, service, outfn, wcsfn, wcsext=0):
#        from astrometry.util import util as anutil
#        wcs = anutil.Tan(wcsfn, wcsext)
#        params = dict(crval1 = wcs.crval[0], crval2 = wcs.crval[1],
#                      crpix1 = wcs.crpix[0], crpix2 = wcs.crpix[1],
#                      cd11 = wcs.cd[0], cd12 = wcs.cd[1],
#                      cd21 = wcs.cd[2], cd22 = wcs.cd[3],
#                      imagew = wcs.imagew, imageh = wcs.imageh)
#        result = self.send_request(service, {'wcs':params})
#        print('Result status:', result['status'])
#        plotdata = result['plot']
#        plotdata = base64.b64decode(plotdata)
#        open(outfn, 'wb').write(plotdata)
#        print('Wrote', outfn)

#    def sdss_plot(self, outfn, wcsfn, wcsext=0):
#        return self.overlay_plot('sdss_image_for_wcs', outfn,
#                                 wcsfn, wcsext)

#    def galex_plot(self, outfn, wcsfn, wcsext=0):
#        return self.overlay_plot('galex_image_for_wcs', outfn,
#                                 wcsfn, wcsext)
#<\jim>

    def my_jobs(self):
        result = self.send_request('myjobs/')
        return result['jobs']

    def job_status(self, job_id, justdict=False):
        result = self.send_request('jobs/%s' % job_id)
        if justdict:
            return result
        stat = result.get('status')
        if stat == 'success':

            result = self.send_request('jobs/%s/calibration' % job_id)            
            writeLog(0, "job_status",'Calibration:')
            writeLog(0, "job_status",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
            result = self.send_request('jobs/%s/tags' % job_id)
            writeLog(0, "job_status",'Tags:')
            writeLog(0, "job_status",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
            result = self.send_request('jobs/%s/machine_tags' % job_id)
            writeLog(0, "job_status",'Machine Tags:')
            writeLog(0, "job_status",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
            result = self.send_request('jobs/%s/objects_in_field' % job_id)
            writeLog(0, "job_status",'Objects in field:')
            writeLog(0, "job_status",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
            result = self.send_request('jobs/%s/annotations' % job_id)
            writeLog(0, "job_status",'Annotations:')
            writeLog(0, "job_status",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
            result = self.send_request('jobs/%s/info' % job_id)

        return stat

    def annotate_data(self,job_id):
        """
        :param job_id: id of job
        :return: return data for annotations
        """
        result = self.send_request('jobs/%s/annotations' % job_id)
        return result

    def sub_status(self, sub_id, justdict=False):
        result = self.send_request('submissions/%s' % sub_id)
        if justdict:
            return result
        return result.get('status')

    def jobs_by_tag(self, tag, exact):
        exact_option = 'exact=yes' if exact else ''
        result = self.send_request(
            'jobs_by_tag?query=%s&%s' % (quote(tag.strip()), exact_option),
            {},
        )
        return result

    def calibrate_data(self,job_id):
        result = self.send_request('jobs/%s/calibration' % job_id)
        return result

    def tags_data(self,job_id):
        result = self.send_request('jobs/%s/tags' % job_id)
        return result

    def machine_tags_data(self,job_id):
        result = self.send_request('jobs/%s/machine_tags' % job_id)
        return result

    def objects_in_field_data(self,job_id):
        result = self.send_request('jobs/%s/objects_in_field' % job_id)
        return result

    def deg2HMS(self, ra='', dec='', round=False):
        RA, DEC, rs, ds = '', '', '', ''
        if dec:
            if str(dec)[0] == '-':
                ds, dec = '-', abs(dec)
            deg = int(dec)
            decM = abs(int((dec-deg)*60))
            if round:
                decS = int((abs((dec-deg)*60)-decM)*60)
            else:
                decS = (abs((dec-deg)*60)-decM)*60
            DEC = '{0}{1}d {2}m {3}s'.format(ds, deg, decM, decS)

        if ra:
            if str(ra)[0] == '-':
                rs, ra = '-', abs(ra)
            raH = int(ra/15)
            raM = int(((ra/15)-raH)*60)
            if round:
                raS = int(((((ra/15)-raH)*60)-raM)*60)
            else:
                raS = ((((ra/15)-raH)*60)-raM)*60
            RA = '{0}{1}h {2}m {3}s'.format(rs, raH, raM, raS)

        if ra and dec:
            return (RA, DEC)
        else:
            return RA or DEC

def gui_sel_upload():
    sel_upload =  tkFileDialog.askopenfilename(title = "Select file", filetypes = (("image files",("*.jpg","*.fit", "*.fits", "*.gif", "*.png")),("all files","*.*")))
    if sel_upload:
        entry["upload"].delete(first=0,last=999)
        entry["upload"].insert(0, sel_upload)
        entry["solved_id"].delete(first=0,last=999)

#gui routine to copy calibrate filename into selected 'to' field
def gui_use_cal_fn(ent):
    entry[ent].delete(first=0,last=999)
    entry[ent].insert(0,entry["calibrate"].get())

#gui routine to select a results file for display
def gui_sel_file():
    sel_result_file =  tkFileDialog.askopenfilename(title = "Select file", filetypes = (("Result files",("*.json", "*.txt")),("all files","*.*")))
    if sel_result_file:
        entry["gui_result_file"].delete(first=0,last=999)
        entry["gui_result_file"].insert(0, sel_result_file)

def gui_show_file():
    global solving_state, result
    if solving_state:
        return
    filename = entry["gui_result_file"].get()
    if os.path.exists(filename) == True:
        editArea = gui_gen_win()
        #read file and write into window
        with open(filename,'r') as f:
            for sText in f:
                editArea.insert(INSERT, sText)

def gui_quit():
    global solving_state, result

    if not solving_state:
        sys.exit()

def gui_solve():
    global solving_state, result
    
    if solving_state:
        return
    else:
        solving_state = True

    opt.alog_level = int(entry["alog_level"].get())
    opt.upload = entry["upload"].get()
    opt.apikey = entry["apikey"].get()
    opt.public = entry["public"].get()
    opt.log_to = entry["log_to"].get()

    if entry["solved_id"].get() != "":
        opt.solved_id = entry["solved_id"].get()
    else:
      opt.solved_id = None

    if entry["sensor_size"].get() != "":
        opt.sensor_size = float(entry["sensor_size"].get())
    else:
        opt.sensor_size = None

    if entry["calibrate"].get() != "":
        opt.calibrate = entry["calibrate"].get()
        if os.path.exists(opt.calibrate):
             os.remove(opt.calibrate)
    else:
        opt.calibrate = None

    if entry["annotate"].get() != "":
        opt.annotate = entry["annotate"].get()
        if os.path.exists(opt.annotate):
             os.remove(opt.annotate)
    else:
        opt.annotate = None

    if entry["tags"].get() != "":
        opt.tags = entry["tags"].get()
        if os.path.exists(opt.tags):
             os.remove(opt.tags)
    else:
        opt.tags = None

    entry["gui_status"].delete(first=0,last=999)
    entry["gui_ra"].delete(first=0,last=999)
    entry["gui_ra_hhmmss"].delete(first=0,last=999)
    entry["gui_dec"].delete(first=0,last=999)
    entry["gui_dec_ddmmss"].delete(first=0,last=999)
    entry["gui_width"].delete(first=0,last=999)
    entry["gui_width_ddmmss"].delete(first=0,last=999)
    entry["gui_height"].delete(first=0,last=999)
    entry["gui_height_ddmmss"].delete(first=0,last=999)
    entry["gui_focal_length"].delete(first=0,last=999)
    entry["gui_radius"].delete(first=0,last=999)
    entry["gui_pixscale"].delete(first=0,last=999)
    entry["gui_orientation"].delete(first=0,last=999)
    entry["gui_parity"].delete(first=0,last=999)

    #setup and start the plate solving thread
    solveThread = threading.Thread(target=platesolve)
    solveThread.start()

def platesolve():

    global solving_state, result

    try:
        #show opt settings to run with
        if opt.alog_level > 2:
            opt_log_set("opt settings to solve with:")

        #clean up old log files
        if os.path.exists(opt.log_to):
             os.remove(opt.log_to)

        if opt.apikey is None:
            parser.print_help()
            writeLog(0, "platesolve","")
            writeLog(0, "platesolve",'You must either specify --apikey or set AN_API_KEY')
            sys.exit(-1)

        args = {}
        args['apiurl'] = opt.server
        c = Client(**args)
        c.login(opt.apikey)

#        if opt.upload or opt.upload_url:
        if (opt.upload or opt.upload_url) and not opt.solved_id:
            if opt.alog_level > 2:
                writeLog(0, "platesolve","process: upload or upload_url")

    #        if opt.wcs or opt.kmz or opt.newfits or opt.annotate:
            if opt.wcs or opt.kmz or opt.newfits or opt.annotate or opt.calibrate or opt.gui:
                opt.wait = True

            kwargs = dict(
                allow_commercial_use=opt.allow_commercial,
                allow_modifications=opt.allow_mod,
                publicly_visible=opt.public)
            if opt.scale_lower and opt.scale_upper:
                kwargs.update(scale_lower=opt.scale_lower,
                              scale_upper=opt.scale_upper,
                              scale_type='ul')
            elif opt.scale_est and opt.scale_err:
                kwargs.update(scale_est=opt.scale_est,
                              scale_err=opt.scale_err,
                              scale_type='ev')
            elif opt.scale_lower or opt.scale_upper:
                kwargs.update(scale_type='ul')
                if opt.scale_lower:
                    kwargs.update(scale_lower=opt.scale_lower)
                if opt.scale_upper:
                    kwargs.update(scale_upper=opt.scale_upper)

            for key in ['scale_units', 'center_ra', 'center_dec', 'radius',
                        'downsample_factor', 'tweak_order', 'crpix_center',]:
                if getattr(opt, key) is not None:
                    kwargs[key] = getattr(opt, key)
            if opt.parity is not None:
                kwargs.update(parity=int(opt.parity))

            if opt.upload:
                upres = c.upload(opt.upload, **kwargs)
            if opt.upload_url:
                upres = c.url_upload(opt.upload_url, **kwargs)

            stat = upres['status']
            if stat != 'success':
                writeLog(0, "platesolve",'Upload failed: status ' + str(stat))
                writeLog(0, "platesolve",str(upres))
                sys.exit(-1)

            opt.sub_id = upres['subid']

        if opt.wait:
            writeLog(2, "platesolve","process: wait (p1)")
            if opt.solved_id is None:
                if opt.sub_id is None:
                    writeLog(0, "platesolve","Can't --wait without a submission id or job id!")
                    sys.exit(-1)

                while True:
                    stat = c.sub_status(opt.sub_id, justdict=True)

                    writeLog(1, "platesolve",'Got status: ' + str(stat))

                    jobs = stat.get('jobs', [])
                    if len(jobs):
                        for j in jobs:
                            if j is not None:
                                break
                        if j is not None:
                            writeLog(0, "platesolve",'Selecting job id:'+ str(j))
                            opt.solved_id = j
                            break
                    writeLog(2, "platesolve","sleep: 5")
                    time.sleep(5)

            while True:
                stat = c.job_status(opt.solved_id, justdict=True)

    #            writeLog(0, "proc",'Got job status:', stat)
                writeLog(1, "platesolve",'Got job status: ' + str(stat))

                if stat.get('status','') in ['success']:
                    success = (stat['status'] == 'success')
                    break
                time.sleep(5)

        if opt.solved_id:
            writeLog(2, "platesolve","process: solve_id")
            if opt.gui:
                entry["solved_id"].delete(first=0,last=999)
                entry["solved_id"].insert(0, opt.solved_id)
            # we have a jobId for retrieving results
            retrieveurls = []
            if opt.wcs:
                # We don't need the API for this, just construct URL
                url = opt.server.replace('/api/', '/wcs_file/%i' % opt.solved_id)
                retrieveurls.append((url, opt.wcs))
            if opt.kmz:
                url = opt.server.replace('/api/', '/kml_file/%i/' % opt.solved_id)
                retrieveurls.append((url, opt.kmz))
            if opt.newfits:
                url = opt.server.replace('/api/', '/new_fits_file/%i/' % opt.solved_id)
                retrieveurls.append((url, opt.newfits))

            for url,fn in retrieveurls:

                writeLog(0, "platesolve",'Retrieving file from: ' + url + ' to: ' + str(fn))
                f = urlopen(url, timeout=opt.url_timeout)
                txt = f.read()
                w = open(fn, 'wb')
                w.write(txt)
                w.close()
                writeLog(1, "platesolve",'Wrote to:' + str(fn))

            if opt.gui or opt.calibrate:
                writeLog(2, "platesolve","process: gui or calibrate")
                result = c.calibrate_data(opt.solved_id)
                result['ra_hhmmss'] = c.deg2HMS(ra=result['ra'])
                result['dec_ddmmss'] = c.deg2HMS(dec=result['dec'])
                result['width'] = result['width_arcsec'] / 3600
                result['height'] = result['height_arcsec'] / 3600
                result['width_ddmmss'] = c.deg2HMS(dec=result['width'])
                result['height_ddmmss'] = c.deg2HMS(dec=result['height'])

                if opt.sensor_size:
                #Focal Length(mm) = 206.264806 x Pixel Size(micons) / Pixel Scale
 #                   result['focal_length'] = 206.264806 * opt.pixel_size * opt.multiplier / float(result['pixscale'])
                    #focal_length = 57.3 * sensor size (mm) / width
                    result['focal_length'] = 57.3 * opt.sensor_size / float(result['width']) * opt.multiplier
                else:
                    result['focal_length'] = "sensor size required"

                if opt.gui:
                    writeLog(2, "platesolve","process: gui")
                    entry["gui_ra"].insert(0,str(result['ra']))
                    entry["gui_ra_hhmmss"].insert(0,str(result['ra_hhmmss']))
                    entry["gui_dec"].insert(0,str(result['dec']))
                    entry["gui_dec_ddmmss"].insert(0,str(result['dec_ddmmss']))
                    entry["gui_width"].insert(0,str(result['width']))
                    entry["gui_width_ddmmss"].insert(0,str(result['width_ddmmss']))
                    entry["gui_height"].insert(0,str(result['height']))
                    entry["gui_height_ddmmss"].insert(0,str(result['height_ddmmss']))
                    entry["gui_focal_length"].insert(0,str(result['focal_length']))
                    entry["gui_radius"].insert(0,str(result['radius']))
                    entry["gui_pixscale"].insert(0,str(result['pixscale']))
                    entry["gui_orientation"].insert(0,str(result['orientation']))
                    entry["gui_parity"].insert(0,str(result['parity']))
                    gui_up_stat("image: solved")

                if opt.calibrate:
                    writeLog(2, "platesolve","process: calibrate")
                    if opt.calibrate == "log":
                        writeLog(0, "platesolve",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                    else:
                        with open(opt.calibrate,'a') as f:
                            f.write(json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                        writeLog(0, "platesolve",'Wrote Calibrations to: ' +  str(opt.calibrate)) 

            if opt.annotate:
                if opt.alog_level > 2:
                    writeLog(0, "platesolve","process: annotate")
                result = c.annotate_data(opt.solved_id)
                if opt.annotate == "log":
                    writeLog(0, "platesolve",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                else:
                    with open(opt.annotate,'a') as f:
                        f.write(json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                    writeLog(0, "platesolve",'Wrote Annotations to: ' + str(opt.annotate))
                if opt.gui:
                    gui_up_stat("image: solved")


            if opt.tags:
                writeLog(0, "platesolve","process: tags")
                result = c.tags_data(opt.solved_id)
                if opt.tags == "log":
                    writeLog(0, "platesolve",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                else:
                    with open(opt.tags,'a') as f:
                        f.write(json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                    writeLog(0, "platesolve",'Wrote Tags to ' + opt.tags)
                if opt.gui:
                    gui_up_stat("image: solved")

            if opt.machine_tags:
                writeLog(2, "platesolve","process: machine_tags")
                result = c.machine_tags_data(opt.solved_id)
                if opt.machine_tags == "log":
                    writeLog(0, "platesolve",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                else:
                    with open(opt.machine_tags,'a') as f:
                        f.write(json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                    writeLog(0, "platesolve",'Wrote Machine Tags to: ' + str(opt.machine_tags))
                if opt.gui:
                    gui_up_stat("image: solved")

            if opt.objects_in_field:
                writeLog(2, "platesolve","process: objects_in_field")
                result = c.objects_in_field_data(opt.solved_id)
                if opt.objects_in_field == "log":
                    writeLog(0, "platesolve",json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                else:
                    with open(opt.objects_in_field,'a') as f:
                        f.write(json.dumps(result,sort_keys=True,indent=4, separators=(',', ': ')))
                    writeLog(0, "platesolve",'Wrote Objects In Field to: ' + str(opt.objects_in_field))
                if opt.gui:
                    gui_up_stat("image: solved")

        if opt.wait:
            writeLog(2, "platesolve","process: wait (p2)")
            # behaviour as in old implementation
            opt.sub_id = None
            writeLog(2, "platesolve","end process: wait (p2)")

        if opt.sub_id:
            writeLog(2, "platesolve","process: sub_id")
            writeLog(0, "platesolve",str(c.sub_status(opt.sub_id)))
            if opt.alog_level > 2:
                writeLog(2, "platesolve","end process: sub_id")

        if opt.job_id:
            writeLog(2, "platesolve","process: job_id")
            writeLog(0, "platesolve",str(c.job_status(opt.job_id)))

        if opt.jobs_by_tag:
            writeLog(2, "platesolve","process: jobs_by_tag")
            tag = opt.jobs_by_tag
            writeLog(0, "platesolve",str(c.jobs_by_tag(tag, None)))
            
        if opt.jobs_by_exact_tag:
            writeLog(2, "platesolve","process: jobs_by_exact_tag")
            tag = opt.jobs_by_exact_tag
            writeLog(0, "platesolve",c.jobs_by_tag(tag, 'yes'))

        if opt.my_jobs:
            writeLog(2, "platesolve","process: my_jobs")
            jobs = c.my_jobs()
            writeLog(0, "platesolve",json.dumps(jobs,sort_keys=True,indent=4, separators=(',', ': ')))

        solving_state = False

    except:
        solve_Error(sys.exc_info())

#Routine to handle  Errors not handled elswhere
#Ensures that even if there is a programming error the app can report it in the log.

def solve_Error(errorData):

    writeLog(0, "solve_Error","Exception Error:")
    
    for crashVal in errorData:
        writeLog(0, "solve_Error","Error:  " + str(crashVal))

    for frame in traceback.extract_tb(errorData[2]):
        fname, lineno, fn, text = frame
    writeLog(0, "solve_Error","Error:  <traceback line: " + str(lineno) + ">")
    writeLog(0, "solve_Error","Error:  <traceback module: " + str(fn) + ">")
    writeLog(0, "solve_Error","Error:  <traceback text: " + str(text) + ">")

    if opt.gui:
        gui_up_stat("Error (check log):  " + str(errorData[1]) )

def opt_log_set(txt):
    writeLog(2, "opt_log_set", "start process: " + str(txt))
    writeLog(2, "opt_log_set",txt)
    for x in sorted(opt.__dict__):
        writeLog(2, "opt_log_set","    " + x + " = " + str(opt.__dict__[x]))
    writeLog(2, "opt_log_set", "end process")

#Routine to write Log file
#   This routine writes out the logs to:
#   the console (opt.log_to = "console") or a logfile (opt.log_to = "filename")
def writeLog(lvl, proc, strVal):
    if opt.alog_level > lvl:

        timeNow = time.localtime()
        tmpTime = time.strftime('%Y%m%d %H%M%S',timeNow)

        proc = proc.ljust(14)

        tmpStr = tmpTime + " " + proc + "> " + str(strVal)

        if  opt.log_to == "console" or opt.log_to is None:
            print(tmpStr)
        else:
            with open(opt.log_to,'a') as f:
                f.write(tmpStr + "\n")

#routine to set defaults
#if set_opt is true then set all opt to default
#if set_opt is false then only set an opt array value if not already set
def opt_set_def(set_opt):
    writeLog(2, "opt_set_def", "start process: " + str(set_opt))
#    if opt.gui and opt.calibrate is None:
#        opt.calibrate = "log"
    if set_opt:
        opt.upload = None
        opt.solved_id = None
        opt.apikey = None
        opt.sensor_size = None
        opt.calibrate = None
        opt.annotate = None
        opt.tags = None
        opt.machine_tags = None
        opt.objects_in_field = None

    if opt.alog_level is None or set_opt:
        opt.alog_level = 2
    if opt.log_to is None or set_opt:
        opt.log_to = "console"
    if opt.url_timeout is None or set_opt:
        opt.url_timeout = 45
    if opt.multiplier is None or set_opt:
        opt.multiplier = 1.0
#    if opt.server is None or set_opt:
#        opt.server = Client.default_url
    if opt.public is None or set_opt:
        opt.public = "y"
#    if opt.allow_mod is None or set_opt:
#        opt.allow_mod = "d"
    #there is no default for apikey, but look elsewhere
    if opt.apikey is None or set_opt:
        # try the environment
        opt.apikey = os.environ.get('AN_API_KEY', None)

    writeLog(2, "opt_set_def", "start process")

def gui_up_stat(upd):
    writeLog(2, "upd_status",'start process' + str(upd))
    #ps_gui.update_idletasks()
    writeLog(2, "upd_status",'end process')

#a gui routine to do a nothing frame/button!!
def gui_donothing():
    filewin = Toplevel(ps_gui)
    button = Button(filewin, text="Do nothing button")
    button.pack()

#a gui routine to set initial entry values
#def gui_set_entry():
    # writeLog(2, "gui_set_entry", "start process")

    # gui_set_val("alog_level", opt.alog_level, False)
    # gui_set_val("log_to", opt.log_to, False)

    # gui_set_val("apikey", opt.apikey, True)
    # gui_set_val("upload", opt.upload, True)
    # gui_set_val("solved_id", opt.solved_id, True)
    # gui_set_val("calibrate", opt.calibrate, True)
    # gui_set_val("annotate", opt.annotate, True)
    # gui_set_val("tags", opt.tags, True)
    # gui_set_val("sensor_size", opt.sensor_size, True)

    # if opt.public.lower() == "y":
    #     entry["public"] .set("y")
    # else:
    #     entry["public"] .set("n")

    # writeLog(2, "gui_set_entry", "end process")

#gui routine to optionally clear, then set entry() value
#def gui_set_val(e,o,chk):

#     writeLog(2, "gui_set_val", "start process: " + str(e) + " = " + str(o) + ", check: " + str(chk))
#     entry[e].delete(first=0,last=999)
#     if chk:
#         if o is not None:
#             entry[e].insert(0,o)
#     else:
#         entry[e].insert(0,o)
#     writeLog(2, "gui_set_val", "end process")

#a gui routine to delete all entries in the gui
def gui_file_new():
    writeLog(2, "gui_file_new", "start process")
    opt_set_def(True)
    gui_set_entry()
    writeLog(2, "gui_file_new", "end process")

#a gui routine to open and read a settings file in JSON format
def gui_file_open():
    writeLog(2, "gui_file_open", "start process")

    filename =  tkFileDialog.askopenfilename(filetypes=(("JSON files","*.json"),("all files","*.*")))
    if filename == "":
        return
    with open(filename,'r') as f:
        settings_json = json.load(f)
    writeLog(1, "gui_file_open", "Opening settings file: " + filename)
    writeLog(1, "gui_file_open",json.dumps(settings_json,sort_keys=True,indent=4, separators=(',', ': ')))
    #check each entry in settings.json is a valid option
    opt_set_def(True)
    for x in sorted(settings_json):
        if x in opt.__dict__:
            opt.__dict__[x] = settings_json[x]
    gui_set_entry()
    writeLog(2, "gui_file_open", "end process")

#a gui routine to save a settings file in JSON format
def gui_file_save(type):
    writeLog(2, "gui_file_save", "start process: " + str(type))

    settings_json = {}

#    #Save all set settings (except "gui" option)
#    if opt.alog_level > 2:
#        writeLog(0, "proc","Save all set settings (except 'gui' option)")
#    for x in sorted(opt.__dict__):
#        if x != "gui":
#            if opt.__dict__[x] is not None:
#                if opt.alog_level > 2:
#                    writeLog(0, "proc","    save: "+ str(x) + " = " + str(opt.__dict__[x]))
#                settings_json[x] = opt.__dict__[x]

    #Update settings if changed in gui
    if opt.alog_level > 2:
        writeLog(2, "gui_file_save", "entry:")
        for x in sorted(entry):
            writeLog(2, "gui_file_save", "    " + str(x) + " = " + str(entry[x].get()))

    writeLog(1, "gui_file_save","save settings if set in gui:")
    y = parser._get_all_options()
    for x in sorted(entry):
        if entry[x].get() == "":
            if x in opt.__dict__:
                if x in settings_json:
                    del settings_json[x]
        else:
            y = parser.get_option("--" + str(x))
            if y is not None:
                writeLog(2, "gui_file_save","    save: "+ str(y))
                if y.type == "int":
                    settings_json[x] = int(entry[x].get())
                elif y.type == "float":
                    settings_json[x] = float(entry[x].get())
                else:
                    settings_json[x] = entry[x].get()

    #if a "save" menu command
    if type == "save":
        fo = open(nova_settings, "w")
    #else a "save as..." menu command
    else:
        fo = tkFileDialog.asksaveasfile(mode='w', defaultextension=".json", filetypes=(("JSON files","*.json"),("all files","*.*")))
        # asksaveasfile return `None` if dialog closed with "cancel".
        if fo is None:
            return
    writeLog(0, "gui_file_save","save following settings to: " + fo.name)
    writeLog(0, "gui_file_save",json.dumps(settings_json,sort_keys=True,indent=4, separators=(',', ': ')))
    fo.write(json.dumps(settings_json,sort_keys=True,indent=4, separators=(',', ': ')))
    fo.close()
    writeLog(2, "gui_file_save", "end process")

def gui_gen_win():
    writeLog(2,"gui_gen_win", "start process")
    filewin = Toplevel(ps_gui)
    filewin.geometry("755x540")
    frame1 = Frame(filewin, bg = '#ffffff', borderwidth=1, relief="sunken")
    frame1.pack(fill="both", expand=True)
    frame1.place(x=10,y=10)
    scrollbar = Scrollbar(frame1) 
    editArea = Text(frame1, width=89, height=32, wrap="word", yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0)
    editArea.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=editArea.yview)
    scrollbar.pack(side="right", fill="y")


    writeLog(2,"gui_gen_win", "return result: " + str(editArea))
    writeLog(2,"gui_gen_win", "end process")
    return editArea

def gui_help():
    editArea = gui_gen_win()
    for x in parser._get_all_options():
        editArea.insert(INSERT, str(x) + " = " + str(x.dest).upper() + "\n" + str(x.help) + "\n\n")

def gui_about():
    editArea = gui_gen_win()
    editArea.insert(INSERT,
        "This code is derived from the nova.astrometry.net example API code\n" + 
        "Many thanks go to them\n" +
        "\n" +
        "Special thanks go to Dustin Lang, of astrometry.net, for specifically modifying the API to return the image size parameters, " +
         "which enables the pixel size independant calculation of the image's Focal Length." +
        "\n\n" +
        "Jim Hunt"
        )

# Program start
if __name__ == '__main__':

    global solving_state, result

#    writeLog(0, "proc","Running with args %s"%sys.argv)

#    try:

    parser = optparse.OptionParser()

    parser.add_option('--gui', dest='gui',action='store_true', help='Open GUI; implies --calibrate')
    parser.add_option('--upload', dest='upload', help='Upload a file')
    parser.add_option('--solved_id', dest='solved_id', type=int,help='Retrieve result for solved job id instead of submitting new image')
    parser.add_option('--apikey', dest='apikey', help='API key for Astrometry.net web service; if not given will check AN_API_KEY environment variable')
    parser.add_option('--sensor_size', dest='sensor_size', type=float, help='Set camera sensor size (longest side in mm), enables image Focal Length calculation')

    parser.add_option('--calibrate', dest='calibrate', help='If entered, download resulting calibrations, if dest="log" then output to "write _to:" else save to given filename; implies --wait if --urlupload or --upload')
    parser.add_option('--annotate', dest='annotate', help='If entered, get information about annotations, if dest="log" then output to "write _to:" else save to given filename, JSON format; implies --wait if --urlupload or --upload')
    parser.add_option('--tags', dest='tags', help='Download resulting tags, if dest="log" then output to "write _to:" else save to given filename; implies --wait if --urlupload or --upload')
    parser.add_option('--machine_tags', dest='machine_tags', help='Download resulting machine_tags, if dest="log"  then output to "write _to:" else save to given filename; implies --wait if --urlupload or --upload')
    parser.add_option('--objects_in_field', dest='objects_in_field', help='Download resulting objects_in_field, if dest="log" then output to "write _to:" else save to given filename; implies --wait if --urlupload or --upload')

    parser.add_option('--alog_level', dest='alog_level', type=int, help='Set log level: 0=none, 1=brief, 2=full (default=0)')
    parser.add_option('--log_to', dest='log_to', help='Write log to:, if dest not set then output to console else save to given filename')

    parser.add_option('--server', dest='server', default=Client.default_url, help='Set server base URL (eg, %default)')

    parser.add_option('--wait', dest='wait', action='store_true', help='After submitting, monitor job status')
    parser.add_option('--wcs', dest='wcs', help='Download resulting wcs.fits file, saving to given filename; implies --wait if --urlupload or --upload')
    parser.add_option('--newfits', dest='newfits', help='Download resulting new-image.fits file, saving to given filename; implies --wait if --urlupload or --upload')
    parser.add_option('--kmz', dest='kmz', help='Download resulting kmz file, saving to given filename; implies --wait if --urlupload or --upload')
    parser.add_option('--urlupload', dest='upload_url', help='Upload a file at specified url')
    parser.add_option('--scale-units', dest='scale_units', choices=('arcsecperpix', 'arcminwidth', 'degwidth', 'focalmm'), help='Units for scale estimate')
    #parser.add_option('--scale-type', dest='scale_type',
    #                  choices=('ul', 'ev'), help='Scale bounds: lower/upper or estimate/error')
    parser.add_option('--scale-lower', dest='scale_lower', type=float, help='Scale lower-bound')
    parser.add_option('--scale-upper', dest='scale_upper', type=float, help='Scale upper-bound')
    parser.add_option('--scale-est', dest='scale_est', type=float, help='Scale estimate')
    parser.add_option('--scale-err', dest='scale_err', type=float, help='Scale estimate error (in PERCENT), eg "10" if you estimate can be off by 10%')
    parser.add_option('--center_ra', dest='center_ra', type=float, help='RA center')
    parser.add_option('--center_dec', dest='center_dec', type=float, help='Dec center')
    parser.add_option('--radius', dest='radius', type=float, help='Search radius around RA,Dec center')
    parser.add_option('--downsample_factor', dest='downsample_factor', type=int, help='Downsample image by this factor')
    parser.add_option('--parity', dest='parity', choices=('0','1'), help='Parity (flip) of image')
    parser.add_option('--tweak-order', dest='tweak_order', type=int, help='SIP distortion order (default: 2)')
    parser.add_option('--crpix-center', dest='crpix_center', action='store_true', default=None, help='Set reference point to center of image?')

#    parser.add_option('--sdss_wcs', dest='sdss_wcs', nargs=2, help='Plot SDSS image for the given WCS file; write plot to given PNG filename')
#    parser.add_option('--galex', dest='galex_wcs', nargs=2, help='Plot GALEX image for the given WCS file; write plot to given PNG filename')
#<\jim>
    parser.add_option('--sub_id', dest='sub_id', help='Get status of a submission')
    parser.add_option('--job_id', dest='job_id', help='Get status of a job')
    parser.add_option('--my_jobs', dest='my_jobs', action='store_true', help='Get all my jobs')
    parser.add_option('--jobs_by_exact_tag', dest='jobs_by_exact_tag', help='Get a list of jobs associated with a given tag--exact match')
    parser.add_option('--jobs_by_tag', dest='jobs_by_tag', help='Get a list of jobs associated with a given tag')

#    parser.add_option('--private', '-p', dest='public', action='store_const', const='n', default='y', help='Hide this submission from other users')
#    parser.add_option('--allow_mod_sa','-m', dest='allow_mod', action='store_const', const='sa', default='d', help='Select license to allow derivative works of submission, but only if shared under same conditions of original license')
#    parser.add_option('--no_mod','-M', dest='allow_mod', action='store_const', const='n', default='d', help='Select license to disallow derivative works of submission')
#    parser.add_option('--no_commercial','-c', dest='allow_commercial', action='store_const', const='n', default='d', help='Select license to disallow commercial use of submission')

    parser.add_option('--public', dest='public', action='store_const', const='n', help='Image publicly visible: y, n (default: y)')
    parser.add_option('--allow_mod', dest='allow_mod', action='store_const', const='sa', default='d', help='Allow derivative works of image: y, n, sa (share-alike i.e. only if shared under same conditions of original license( (default=sa)')
    parser.add_option('--allow_commercial', dest='allow_commercial', action='store_const', const='n', default='d', help='Allow commercial use of image: y, n (default:y)')

    parser.add_option('--url_timeout', dest='url_timeout', type=int,  help='Timeout for all comms actions in sec (default=45)')
    parser.add_option('--multiplier', dest='multiplier', type=float, help='Multiplier for correcting Focal Length (default=1)')

    opt,args = parser.parse_args()

#        if opt.alog_level > 2:
#        writeLog(0, "proc","Running with args: %s"%sys.argv)

    #Set defaults
    solving_state = False

    #prep some arrays
    entry = {}
    result = {}

    #Check for settings.json file and read into opt variables
    nova_settings = "nova_settings.json"
    if os.path.exists(nova_settings) == True:
        #read file
        fo = open(nova_settings, "r")
        settings_json = json.load(fo)
        fo.close()
        writeLog(2, "__main__", "Settings file '" + nova_settings + "' exists, so read it:")
        writeLog(2, "__main__",json.dumps(settings_json,sort_keys=True,indent=4, separators=(',', ': ')))
        #check each entry in settings.json is a valid option
        for x in sorted(settings_json):
            if x in opt.__dict__:
                #Command line takes precedence over settings.json
                #so only if option not already set by command line, set it from settings.json
                if opt.__dict__[x] is None:
                    opt.__dict__[x] = settings_json[x]
                    writeLog(1, "__main__","Set option from settings.json: --" + x + "=" + str(settings_json[x]))

    #set opt some defaults
    opt_set_def(False)

    #show opt settings to run with
    if opt.alog_level > 2:
        opt_log_set("opt settings to run with:")

    #clean up old log files
    if os.path.exists(opt.log_to):
         os.remove(opt.log_to)

    #setup and solve from gui Interface
    if  opt.gui:

        row_num = 0
        def_pady = 3
        line_len = 161

        ps_gui = Tk()
        ps_gui.title('novaSolve (nova.astrometry.net [' + version + "]")

        menubar = Menu(ps_gui)
        
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Upload", command=gui_sel_upload)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        
        settings = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings)
        settings.add_command(label="New", command=gui_file_new)
        settings.add_command(label="Open", command=gui_file_open)
        settings.add_command(label="Save", command=lambda: gui_file_save("save"))
        settings.add_command(label="Save as...", command=lambda: gui_file_save("save_as"))
        settings.add_separator()
        settings.add_command(label="Exit", command=quit)

        helpmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Help", command=gui_help)
        helpmenu.add_command(label="About...", command=gui_about)

        ps_gui.config(menu=menubar)

        Label(ps_gui, text="INPUT", font="TkHeadingFont", fg="blue").grid(row=row_num, column=0, sticky=W)
        Label(ps_gui, text="mandatory", font="TkHeadingFont", fg="blue").grid(row=row_num, column=1, sticky=W)

        row_num += 1
        Label(ps_gui, text="api key").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["apikey"] = Entry(ps_gui)
        entry["apikey"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        row_num += 1
        Label(ps_gui, text="file upload").grid(row=row_num, column=0, sticky=E)
        entry["upload"] = Entry(ps_gui, width=100)
        entry["upload"].grid(row=row_num, column=1, columnspan=5, sticky=W)
        Button(ps_gui, text='Select', command=gui_sel_upload).grid(row=row_num, column=6, padx=5)

        row_num += 1
        Label(ps_gui, text="        or use").grid(row=row_num, column=0, columnspan=5,sticky=W)

        row_num += 1
        Label(ps_gui, text="solved id*").grid(row=row_num, column=0, sticky=E)
        entry["solved_id"] = Entry(ps_gui)
        entry["solved_id"].grid(row=row_num, column=1, sticky=W)

        row_num += 1
        Label(ps_gui, text="optional", font="TkHeadingFont", fg="blue").grid(row=row_num, column=1, sticky=W)

        row_num += 1
        Label(ps_gui, text="calibrate to").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["calibrate"] = Entry(ps_gui,width=100)
        entry["calibrate"].grid(row=row_num, column=1, columnspan=3, sticky=W, pady=def_pady)

        row_num += 1
        Label(ps_gui, text="annotate to").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["annotate"] = Entry(ps_gui,width=100)
        entry["annotate"].grid(row=row_num, column=1, columnspan=3, sticky=W, pady=def_pady)

        Button(ps_gui, text='use cal fname', command=lambda: gui_use_cal_fn("annotate")).grid(row=row_num, column=6, columnspan=2, padx=5)

        row_num += 1
        Label(ps_gui, text="tags to").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["tags"] = Entry(ps_gui,width=100)
        entry["tags"].grid(row=row_num, column=1, columnspan=3, sticky=W, pady=def_pady)

        Button(ps_gui, text='use cal fname', command=lambda: gui_use_cal_fn("tags")).grid(row=row_num, column=6, columnspan=2, padx=5)

        row_num += 1
        Label(ps_gui, text="public").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["public"] = StringVar()
        checkbutton = Checkbutton(ps_gui, variable = entry["public"] , onvalue="y", offvalue="n").grid(row=row_num, column=1, sticky=W)

        Label(ps_gui, text="camera sensor size (mm)").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["sensor_size"] = Entry(ps_gui, width=5)
        entry["sensor_size"].grid(row=row_num, column=3,  sticky=W, pady=def_pady)

#        row_num += 1
#        Label(ps_gui, text="").grid(row=row_num, column=0, sticky=W)

        row_num += 1
        Label(ps_gui, text="log level").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["alog_level"] = Entry(ps_gui, width=2)
        entry["alog_level"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="log to").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["log_to"] = Entry(ps_gui,width=50)
        entry["log_to"].grid(row=row_num, column=3, columnspan=3, sticky=W, pady=def_pady)

        Button(ps_gui, text='Solve', fg="blue", command=gui_solve).grid(row=row_num, column=7, pady=def_pady, padx=6)

        #now set up entry values
        gui_set_entry()

        row_num += 1
        Label(ps_gui,text="_" * line_len).grid(row=row_num, column=0, columnspan=8, sticky=W)
 
        row_num += 1
        Label(ps_gui, text="OUTPUT", font="TkHeadingFont", fg="red").grid(row=row_num, column=0, sticky=W)

        row_num += 1
        Label(ps_gui,text="status").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_status"] = Entry(ps_gui, width=100)
        entry["gui_status"].grid(row=row_num, column=1, columnspan=5, sticky=W, pady=def_pady)

        row_num += 1
        Label(ps_gui, text="ra (d)").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_ra"] = Entry(ps_gui)
        entry["gui_ra"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="ra (hhmmss)").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["gui_ra_hhmmss"] = Entry(ps_gui)
        entry["gui_ra_hhmmss"].grid(row=row_num, column=3, sticky=W, pady=def_pady, ipadx=5)

        row_num += 1
        Label(ps_gui, text="dec (d)").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_dec"] = Entry(ps_gui)
        entry["gui_dec"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="dec (ddmmss)").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["gui_dec_ddmmss"] = Entry(ps_gui)
        entry["gui_dec_ddmmss"].grid(row=row_num, column=3, sticky=W, pady=def_pady, ipadx=5)

        row_num += 1
        Label(ps_gui, text="width (d)").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_width"] = Entry(ps_gui)
        entry["gui_width"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="width (ddmmss)").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["gui_width_ddmmss"] = Entry(ps_gui)
        entry["gui_width_ddmmss"].grid(row=row_num, column=3, sticky=W, pady=def_pady, ipadx=5)

        row_num += 1
        Label(ps_gui, text="height (d)").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_height"] = Entry(ps_gui)
        entry["gui_height"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="height (ddmmss)").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["gui_height_ddmmss"] = Entry(ps_gui)
        entry["gui_height_ddmmss"].grid(row=row_num, column=3, sticky=W, pady=def_pady, ipadx=5)

        row_num += 1
        Label(ps_gui, text="focal length (mm)").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_focal_length"] = Entry(ps_gui)
        entry["gui_focal_length"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="radius (d)").grid(row=row_num, column=2, sticky=E, pady=def_pady)
        entry["gui_radius"] = Entry(ps_gui)
        entry["gui_radius"].grid(row=row_num, column=3, sticky=W, pady=def_pady)

        row_num += 1
        Label(ps_gui, text="pixel scale (asec/p)").grid(row=row_num, column=0, sticky=E, pady=def_pady)
        entry["gui_pixscale"] = Entry(ps_gui)
        entry["gui_pixscale"].grid(row=row_num, column=1, sticky=W, pady=def_pady)

        Label(ps_gui, text="orientation (d)").grid(row=row_num, column=2, sticky=E , pady=def_pady)
        entry["gui_orientation"] = Entry(ps_gui)
        entry["gui_orientation"].grid(row=row_num, column=3,  sticky=W, pady=def_pady)

        row_num += 1
        Label(ps_gui, text="parity").grid(row=row_num, column=0, sticky=E , pady=def_pady)
        entry["gui_parity"] = Entry(ps_gui)
        entry["gui_parity"].grid(row=row_num, column=1,  sticky=W, pady=def_pady)

        row_num += 1
        Label(ps_gui, text="Show file").grid(row=row_num, column=0, sticky=E , pady=def_pady)
        entry["gui_result_file"] = Entry(ps_gui,width=100)
        entry["gui_result_file"].grid(row=row_num, column=1, columnspan=3, sticky=W, pady=def_pady)
        Button(ps_gui, text='Show', command=gui_show_file).grid(row=row_num, column=6, pady=4)
        Button(ps_gui, text='Select', command=gui_sel_file).grid(row=row_num, column=7, padx=5)


        row_num += 1
        Label(ps_gui,text="_" * line_len).grid(row=row_num, column=0, columnspan=8,  sticky=W)

        row_num += 1
        Label(ps_gui, text="* Note: if set 'solved id' will be used", fg="red").grid(row=row_num, column=1, columnspan=2, sticky=W)
        Button(ps_gui, text='Quit', command=gui_quit).grid(row=row_num, column=7, pady=def_pady)

        ps_gui.mainloop()

    else:
        #solve in command line mode
        platesolve()

#    except:
#        solve_Error(sys.exc_info())
