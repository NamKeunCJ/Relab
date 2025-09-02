import psycopg2
import hashlib
from datetime import datetime, timedelta
import threading
import time
import requests # elementos para datos davis
# hidrica.py
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import math

# Crear un Blueprint para las rutas hídricas
carga_bp = Blueprint('carga', __name__, static_folder='static',template_folder='templates')

@carga_bp.route('/inicio')
def inicio():

    return "Inicio cargas"