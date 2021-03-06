from flask import Flask, send_file, request
from sys import argv
from flask import request, render_template, flash, redirect, \
    url_for, Blueprint, g, Flask
from glob import glob
import os
import re
import argparse

# assert len(argv)==2, 'Usage: python retrievis.py <result dir>' 

app = Flask('ForwardMail')
app.config['LOGFILE'] = './retrievis.log'
app.config['RESULT_DIR'] = '' 

@app.route('/')
def index():
    res_paths = glob(app.config['RESULT_DIR'] + '/*.txt')
    res_files = sorted([os.path.basename(f) for f in res_paths], key=_get_sortkey)
    return render_template('index.html', res_files=res_files)
 

## return keys of filenames:
##   1. prefix
##   2. number 1
##   3. number 2 ...
##  eg. result_1.txt is before  result_2.txt  (1 < 2)
##      abc.txt      is before  result.txt    (a < r)
##      res_1_3.txt  is before  res_1_5.txt   (3 < 5)
def _get_sortkey(filename):
    numbers = [int(s) for s in re.findall('\d+', filename)]

    # all chars before any number in filename
    prefix = re.match('^((?![0-9]).)*', filename).group(0)

    return [prefix] + numbers


@app.route('/results/image')
@app.route('/image')
def get_image():
    imgpath = request.args.get('file')
    ext = imgpath.split('.')[-1] or 'png' # default type as png
    return send_file(imgpath, mimetype='image/'+ext)

@app.route('/queryimg')
def get_queryimg():
    res_file = request.args.get('resultfile')
    queryimg = parse_resfile(res_file, want_result=False)
    ext = queryimg.split('.')[-1] or 'png' # default type as png
    return send_file(queryimg, mimetype='image/'+ext)
    

@app.route('/results')
def show_results():
    res_file = request.args.get('resultfile')
    print res_file
    queryimg, res_imgs = parse_resfile(res_file)
    return render_template('results.html', queryimg=queryimg, res_imgs=res_imgs)

def parse_resfile(res_file, want_query=True, want_result=True):
    res_file = os.path.join(app.config['RESULT_DIR'], res_file)

    with open(res_file, 'r') as f:
        l = f.readline().strip()
        while not l:
            l = f.readline().strip()
        queryimg = l

        if want_result:
            res_imgs = filter(lambda l: l.strip(), f.readlines())

    if want_query and want_result:
        return queryimg, res_imgs
    elif want_query:
        return queryimg
    elif want_result:
        return resultimg


def flaskrun(app, default_host='0.0.0.0', 
                  default_port='5000'):
    """
    Takes a flask.Flask instance and runs it. Parses 
    command-line flags to configure the app.
    """

    # Set up the command-line args
    parser = argparse.ArgumentParser()
    parser.add_argument('resultdir', metavar='resultdir', 
                      help='results list directory.')
    parser.add_argument('-H', '--host',
                      help='Hostname of the Flask app ' + \
                           '[default %s]' % default_host,
                      default=default_host)
    parser.add_argument('-P', '--port',
                      help='Port for the Flask app ' + \
                           '[default %s]' % default_port,
                      default=default_port)

    # Two args useful for debugging purposes, but 
    # a bit dangerous so not exposed in the help message.
    parser.add_argument('-d', '--debug',
                      action='store_true', dest='debug',
                      help=argparse.SUPPRESS)

    args = parser.parse_args()
    
    if args.resultdir:
        app.config['RESULT_DIR'] = args.resultdir
    else:
        print 'no result dir set!'
        exit(-1)

    app.run(
        debug=args.debug,
        host=args.host,
        port=int(args.port)
    )

flaskrun(app)
