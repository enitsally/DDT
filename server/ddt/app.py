from flask import Flask, jsonify, request, session, render_template, redirect
from flask.ext.cors import CORS, cross_origin
from MongodbBatch import mongodbbatch
import json
import os
import pymongo
import logging
import logging.config

# logging.config.fileConfig('logging.conf')

CON_COLLECTION_NAME = 'connection'
MD_COLLECTION_NAME = 'meta_data'
USER_COLLECTION_NAME = 'sys_users'

app = Flask(__name__, static_url_path='')
app.secret_key = 'ddt key'

obj = mongodbbatch(host="172.18.60.20", port="27017", db="DDDB")

CORS(app)

@app.route('/')
def root():
  return app.send_static_file('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  logging.info('API: /login, method: login()')
  input_data = json.loads(request.data)
  var_username = input_data['username']
  var_password = input_data['password']
  login_status = obj.get_login(USER_COLLECTION_NAME, var_username, var_password)
  user_map = {'A': 'Admin', 'U':'User'}

  if login_status is None:
    status = False
    message = 'User not exist.'
  elif login_status == 'Failed':
    status = False
    message = 'User name or password failed.'
  else:
    status = True
    message = 'User login succeed.'
    login_status = user_map.get(login_status) if user_map.get(login_status) is None else user_map.get(login_status)
  return jsonify(
    {'status': status, 'role': login_status, 'msg': message, 'user': {'id': var_username, 'role': login_status}})

@app.route('/logout')
def logout():
    logging.info('API: /logout, method: logout()')
    session.pop('logged_in', None)
    status = "You are logged out."
    return jsonify({'status': status})

@app.route('/uploadConnJsonFile', methods=['GET', 'POST'])
def uploadConnJsonFile():
    logging.info('API: /uploadConnJsonFile, method: uploadConnJsonFile()')
    if request.method == 'POST':
      file = request.files['file']
      file_id = obj.upload_temp(file)
      result = {
        'file_name': file.filename,
        'file_id': str(file_id)
      }

      return jsonify({'status': result})

if __name__ == "__main__":
  # logging.config.fileConfig('logging.conf')
  app.run(debug=True)
