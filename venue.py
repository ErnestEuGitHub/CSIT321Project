from flask import Flask, render_template, session, request, flash, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def venue():
    return render_template('venuetest.html')