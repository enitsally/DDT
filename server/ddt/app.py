from flask import Flask, jsonify, request, session, render_template, redirect
from flask_cors import CORS, cross_origin
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
SYS_PATTERN_NAME = 'sys_patterns'

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

@app.route('/getPatternSummary', methods=['GET', 'POST'])
def getpatternsummary():
  logging.info('API: /getPatternSummary, method: getpatternsummary()')
  input_data = json.loads(request.data)
  time_range = input_data['time_range']
  start_time = input_data['start_date']
  end_time = input_data['end_date']
  result = obj.get_pattern_summary(SYS_PATTERN_NAME, time_range, start_time, end_time, [], [])
  return jsonify({'status': result})

@app.route('/getSearchedPatternSummary', methods=['GET', 'POST'])
def getsearchedpatternsummary():
  logging.info('API: /getSearchedPatternSummary, method: getsearchedpatternsummary()')
  input_data = json.loads(request.data)
  start_time = input_data['start_date'] if input_data['start_date'] == '' else datetime.strptime(
    input_data['start_date'][:10], "%Y-%m-%d")
  end_time = input_data['end_date'] if input_data['end_date'] == '' else datetime.strptime(input_data['end_date'][:10],
                                                                                           "%Y-%m-%d") + timedelta(
    days=1)
  key_info = input_data['conn_keys']

  conn_key= []
  for key in key_info:
    conn_key.append(key.get('conn_key'))

  pattern_type = input_data['pattern_selected']

  result = obj.get_pattern_summary(SYS_PATTERN_NAME, '', start_time, end_time, conn_key, pattern_type)
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
    file_descr = request.form['descr']

    file_name = file.filename
    file_id = obj.upload_temp(file)

    if file_id is not None:
        return jsonify({'status': True, 'descr': str(file_descr), 'fileName': file_name, 'objectId': str(file_id)})
    else:
        return jsonify({'status': False, 'descr': str(file_descr), 'fileName': file_name, 'objectId': None})

@app.route('/clearAllAttachFile', methods = ['GET', 'POST'])
def clearallattachfile():
  logging.info('API: /clearAllAttachFile, method: clearallattachfile()')
  if request.method == 'POST':
    objectId = request.data
    chk = obj.delete_temp(objectId)
    return jsonify({'status': chk})

  return jsonify({'status': False})


@app.route('/getSystemUser',methods=['GET','POST'])
def getsystemuser():
  logging.info('API: /getSystemUser, method: getsystemuser()')
  result = obj.get_user_usergroup_list(USER_COLLECTION_NAME, USER_GROUP_COLLECTION_NAME)
  return jsonify({'status': result})

@app.route('/clearAllDoc',methods=['GET','POST'])
def clearalldoc():
  logging.info('API: /clearAllDoc, method: clearalldoc()')
  result = obj.clear_all_doc()
  return jsonify({'status': result})

@app.route('/saveQueryPattern', methods=['GET','POST'])
def savequerypattern():
  logging.info('API: /saveQueryPattern, method: savequerypattern()')

  if request.method == 'POST':
    timestamp = datetime.now()
    input_data = json.loads(request.data)
    attach_list = [] if input_data.get('attach_list') is None else input_data['attach_list']
    conn_key = '' if input_data.get('conn_key') == '' else input_data['conn_key']['conn_key']
    creation_user = input_data['creation_user']
    pattern_descr = '' if input_data.get('pattern_descr') is None else input_data['pattern_descr']
    pattern_text = '' if input_data.get('pattern_text') is None else input_data['pattern_text']
    pattern_type = '' if input_data.get('pattern_type') is None else input_data['pattern_type']
    user_open_list = [] if input_data.get('user_open_list') is None else input_data['user_open_list']
    condition_subject_area = [] if input_data.get('condition_list') is None else input_data['condition_list']
    selection_subject_area = [] if input_data.get('selection_list') is None else input_data['selection_list']

    for attach in attach_list:
      attach['upload_time'] = timestamp

    pattern_profile = {
      'pattern_descr': pattern_descr,
      'pattern_text': pattern_text,
      'pattern_type': pattern_type,
      'created_user': creation_user,
      'created_date': timestamp,
      'updated_date': timestamp,
      'connection_key': conn_key,
      'user_open_list': user_open_list,
      'attach_list': attach_list,
      'condition_subArea': condition_subject_area,
      'selection_subArea': selection_subject_area
    }

    pattern_id = obj.save_json_to_collection(pattern_profile, SYS_PATTERN_NAME)

  else:
    pattern_id = None
  return jsonify({'status': pattern_id})

@app.route('/deletePattern', methods=['GET','POST'])
def deleteapattern():
  logging.info('API: /deletePattern, method: deleteapattern()')
  if request.method == 'POST':
    input_data = json.loads(request.data)
    pattern_id = input_data['id']
    operate_user = input_data['user']
    result = obj.del_pattern(pattern_id, operate_user)
    return jsonify({'status': result})

@app.route('/testSQLPattern', methods=['GET','POST'])
def testsqlpattern():
  logging.info('API: /testSQLPattern, method: testsqlpattern()')
  if request.method == 'POST':
    pattern_id = request.data
    result = obj.test_sql_pattern(pattern_id)
    return jsonify({'status': result})

@app.route('/testSQLPatternDraft', methods=['GET','POST'])
def testsqlpatterndraft():
  logging.info('API: /testSQLPatternDraft, method: testsqlpatterndraft()')
  if request.method == 'POST':
    input_data = json.loads(request.data)
    result = obj.test_sql_pattern_draft(input_data)
    return jsonify({'status': result})

if __name__ == "__main__":
  # logging.config.fileConfig('logging.conf')
  app.run(debug=True)
