from flask import render_template, request, flash, session, url_for, redirect

from database import dbConnect
from sqlalchemy import text
from general import *

def sysAdminHome():
    navtype = 'sysAdmin'
            
    return render_template('sysAdminHome.html', navtype=navtype)