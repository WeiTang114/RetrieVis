from flask import request, render_template, flash, redirect, \
    url_for, Blueprint, g, Flask
from retrievis import app
from glob import glob
import os

blueprint = Blueprint('yo', __name__) 
account_db = connectdb.connect()

@blueprint.route('/')
def index():
    res_paths = glob(app.config['RESULT_DIR'] + '/*.txt')
    res_files = [os.path.basename(f) for f in resultpaths]
    return render_template('index.html', res_files=res_files)
 

