# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Import core packages
import os

# Import Flask
from flask import Flask
import pymysql

# Inject Flask magic
app = Flask(__name__)

app.secret_key = "aoishnaviariur9fi43jjfm"

dbConn = pymysql.connect(
    host="116.62.160.40",
    port=3306,
    user="misy410group07",
    database="misy410group07",
    password="@Z8KL9PxVqgWGvnRe",
    cursorclass=pymysql.cursors.DictCursor,
)

cursor = dbConn.cursor()

# Import routing to render the pages
from app import views
