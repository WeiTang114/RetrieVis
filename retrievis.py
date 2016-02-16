from flask import Flask, send_file, request
from sys import argv
from flask import request, render_template, flash, redirect, \
    url_for, Blueprint, g, Flask
from glob import glob
import os
import re

assert len(argv)==2, 'Usage: python retrievis.py <result dir>' 

app = Flask('ForwardMail')
app.config['LOGFILE'] = './retrievis.log'
app.config['RESULT_DIR'] = argv[1]

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

@app.route('/results')
def show_results():
    res_file = request.args.get('resultfile')
    print res_file
    queryimg, res_imgs = parse_resfile(res_file)
    return render_template('results.html', queryimg=queryimg, res_imgs=res_imgs)

def parse_resfile(res_file):
    res_file = os.path.join(app.config['RESULT_DIR'], res_file)

    with open(res_file, 'r') as f:
        lines = filter(lambda l: l.strip(), f.readlines())

    queryimg = lines[0]
    res_imgs = lines[1:]

    print queryimg
    return queryimg, res_imgs


app.run('0.0.0.0', debug=True)
