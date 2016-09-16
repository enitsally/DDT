from flask import Flask, jsonify, request, session, render_template, redirect
from flask.ext.cors import CORS, cross_origin
from MongodbBatch import mongodbbatch
from DBFactory import Connector
from datetime import datetime
from datetime import timedelta
import json
import os
import pymongo
import logging
import logging.config

# logging.config.fileConfig('logging.conf')

CON_COLLECTION_NAME = 'connection'
MD_COLLECTION_NAME = 'meta_data'
USER_COLLECTION_NAME = 'sys_users'
USER_GROUP_COLLECTION_NAME = 'sys_users_group'
SYS_COLLECTION_NAME = 'sys_conf'

app = Flask(__name__, static_url_path='')
app.secret_key = 'ddt key'

# MongdoDB instance for connection and operations
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
  user_map = {'A': 'Admin', 'U': 'User'}

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


@app.route('/checkConnJsonFile', methods=['GET', 'POST'])
def checkconnjsonfile():
  logging.info('API: /checkConnJsonFile, method: checkconnjsonfile()')
  if request.method == 'POST':
    file = request.files['file']

    file_name = file.filename
    if file_name.split('.')[1] == 'json':
      json_content = json.load(file)
      format_status = True

      if len(json_content) == 1:
        key = json_content.keys()[0]
        db = Connector(json_content.get(key))
        conn = db.connection_test()
        conn_status = conn.get('status')

        exist_status = obj.check_connection_exit(CON_COLLECTION_NAME, key)
    else:
      format_status = False
      conn_status = False
      exist_status = False
    if format_status & conn_status:
      file.seek(0)
      file_id = obj.upload_temp(file)
    else:
      file_id = ''
      key = ''

    return jsonify({'status': {'format': format_status, 'conn': conn_status, 'file_name': file_name,
                               'file_id': str(file_id), 'error_msg': conn.get('message'), 'conn_key': key,
                               'key_exist': exist_status}})


@app.route('/testConnectionKey', methods=['GET', 'POST'])
def testconnectionkey():
  logging.info('API: /testConnectionKey, method: testconnectionkey()')
  if request.method == 'POST':
    conn_key = request.data
    conn_info = obj.get_connection_key(CON_COLLECTION_NAME, conn_key)
    if conn_info is None:
      conn_status = False
      error_msg = "System don't have such key: {}".format(conn_key)
    else:
      db = Connector(conn_info)
      conn = db.connection_test()
      conn_status = conn.get('status')
      error_msg = conn.get('message')

    return jsonify({'status': {'conn': conn_status, 'error_msg': error_msg}})


@app.route('/saveConnJsonFile', methods=['GET', 'POST'])
def saveconnjsonfile():
  logging.info('API: /saveConnJsonFile, method: saveconnjsonfile()')
  status = []
  if request.method == 'POST':
    input_data = json.loads(request.data)
    for input in input_data:
      file_name = input['file_name']
      file_id = input['file_id']
      file_size = input['file_size']
      conn_key = input['conn_key']
      result = obj.save_connection_json(CON_COLLECTION_NAME, file_id, file_name, file_size, conn_key)

      tmp = {'conn_key': conn_key, 'status': result.get('status'), 'message': result.get('message')}
      status.append(tmp)

  return jsonify({'status': status})


@app.route('/getConnectionSummary', methods=['GET', 'POST'])
def getconnectionsummary():
  logging.info('API: /getConnectionSummary, method: getconnectionsummary()')
  input_data = json.loads(request.data)
  time_range = input_data['time_range']
  start_time = input_data['start_date']
  end_time = input_data['end_date']
  result = obj.get_connection_summary(CON_COLLECTION_NAME, time_range, start_time, end_time, [])
  return jsonify({'status': result})


@app.route('/getConnectionShort')
def getconnectionshort():
  logging.info('API: /getConnectionShort, method: getconnectionshort()')
  result = obj.get_connection_short(CON_COLLECTION_NAME)
  return jsonify({'status': result})

@app.route('/getConnectionFull')
def getconnectionfull():
  logging.info('API: /getConnectionFull, method: getconnectionfull()')
  result = obj.get_connection_full(CON_COLLECTION_NAME)
  return jsonify({'status': result})


@app.route('/deleteConnectionKey', methods=['GET', 'POST'])
def deleteconnectionkey():
  logging.info('API: /deleteConnectionKey, method: deleteconnectionkey()')
  conn_key = request.data
  result = obj.del_connection_key(CON_COLLECTION_NAME, conn_key)
  return jsonify({'status': result})


@app.route('/getSearchedConnectionSummary', methods=['GET', 'POST'])
def getsearchedconnectionsummary():
  logging.info('API: /getSearchedConnectionSummary, method: getsearchedconnectionsummary()')
  input_data = json.loads(request.data)
  start_time = input_data['start_date'] if input_data['start_date'] == '' else datetime.strptime(
    input_data['start_date'][:10], "%Y-%m-%d")
  end_time = input_data['end_date'] if input_data['end_date'] == '' else datetime.strptime(input_data['end_date'][:10],
                                                                                           "%Y-%m-%d") + timedelta(
    days=1)
  conn_key = input_data['conn_keys']

  result = obj.get_connection_summary(CON_COLLECTION_NAME, '', start_time, end_time, conn_key)
  return jsonify({'status': result})

@app.route('/getPatternType', methods=['GET', 'POST'])
def getpatterntype():
  logging.info('API: /getPatternType, method: getpatterntype()')
  result = obj.get_pattern_type(SYS_COLLECTION_NAME)
  return jsonify({'status': result})

@app.route('/checkPatternTextFile', methods=['GET', 'POST'])
def checkpatterntextfile():
  logging.info('API: /checkPatternTextFile, method: checkpatterntextfile()')
  if request.method == 'POST':
    file = request.files['file']
    file_name = file.filename
    file.seek(0)
    txtContent = file.read()
    return jsonify({'status': txtContent})

@app.route('/checkPatternAttachedFile', methods=['GET', 'POST'])
def checkpatternattachedfile():
  logging.info('API: /checkPatternAttachedFile, method: checkpatternattachedfile()')
  if request.method == 'POST':
    file = request.files['file']

    file_name = file.filename
    if file_name.split('.')[1] == 'json':
      json_content = json.load(file)
      format_status = True

      if len(json_content) == 1:
        key = json_content.keys()[0]

    return jsonify({'status': key})

@app.route('/getSystemUser',methods=['GET','POST'])
def getsystemuser():
  logging.info('API: /getSystemUser, method: getsystemuser()')
  result = obj.get_user_usergroup_list(USER_COLLECTION_NAME, USER_GROUP_COLLECTION_NAME)
  return jsonify({'status': result})


if __name__ == "__main__":
  # logging.config.fileConfig('logging.conf')
  app.run(debug=True)
