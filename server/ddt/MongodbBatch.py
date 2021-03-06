import json
from os import listdir
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
import pymongo
import gridfs
from DBFactory import Connector
from DBMetaData import DBMetaData
import sqlalchemy

import logging

logging.basicConfig()
logging.getLogger("datadiscovery.demo").setLevel(logging.DEBUG)

support_dialect = ['netezza', 'sqlsever', 'redshift', 'mysql']

CON_COLLECTION_NAME = 'connection'
MD_COLLECTION_NAME = 'meta_data'
USER_COLLECTION_NAME = 'sys_users'
USER_GROUP_COLLECTION_NAME = 'sys_users_group'
SYS_COLLECTION_NAME = 'sys_conf'
SYS_PATTERN_NAME = 'sys_patterns'


class mongodbbatch:
  def __init__(self, host="localhost", port="27017", db="DDDB"):
    conn_str = "mongodb://{}:{}".format(host, port)
    client = MongoClient(conn_str)
    if db in client.database_names():
      logging.warning("Database '{}' initiation message, database exits.".format(db))

    else:
      logging.warning("Database '{}' initiation message, create new database.".format(db))

    self.db = client[db]
    # try:
    #     self.db.authenticate('map', 'map', source= db, mechanism='SCRAM-SHA-1')
    # except pymongo.errors.OperationFailure as e:
    #     logging.error("Error Code {}: {}".format(e.code, e.details.get('errmsg')))

  def get_db(self):
    return self.db

  def get_collection(self):
    return self.db.collection_names(False)

  def import_connection_json(self, connection_collection_name, json_file_path):
    timestamp = datetime.now()
    if connection_collection_name in self.db.collection_names():
      logging.warning("Collection '{}' initiation message, collection exits.".format(connection_collection_name))
    else:
      logging.warning(
        "Collection '{}' initiation message, create new collection.".format(connection_collection_name))
      self.db.create_collection(connection_collection_name)

    json_files = [x for x in listdir(json_file_path) if x.endswith('.json')]

    for json_name in json_files:
      json_key = os.path.splitext(json_name)[0]
      with open("{}/{}".format(json_file_path, json_name)) as json_file:
        json_data = json.load(json_file)
        if json_key not in json_data:
          logging.error(
            "JSON file '{}', format doesn't match, the key should be as same as json file name.".format(
              json_name))
          continue
        else:
          json_data['updated_date'] = timestamp
          check = self.db[connection_collection_name].find_one({json_key: {'$exists': True}})
          try:
            if check is None:
              self.db[connection_collection_name].insert(json_data)
              logging.info("Key '{}' not exists, insert new one.".format(json_key))

            else:

              json_data[json_key]['version'] = 1 if check[json_key].get('version') is None else check[
                                                                                                  json_key].get(
                'version') + 1
              self.db[connection_collection_name].find_one_and_replace({json_key: {'$exists': True}},
                                                                       json_data)
              logging.info(
                "Key '{}' exists, update record and change updated-date and version.".format(json_key))

          except pymongo.errors.ConnectionFailure as cf:
            logging.error("ConnectionFailure:{}".format(cf))
          except pymongo.errors.DuplicateKeyError as dk:
            logging.error("DuplicatedKeyError:{}".format(dk))
          except pymongo.errors.OperationFailure as e:
            logging.error("Error Code {}: {}".format(e.code, e.details.get('errmsg')))

  def save_connection_json(self, connection_collection_name, json_file_id, file_name, file_size, conn_key):
    status_msg = ''
    fs = gridfs.GridFS(self.db)
    object_ID = ObjectId(json_file_id)
    if fs.exists(object_ID):
      json_data = json.load(fs.get(object_ID))
      timestamp = datetime.now()
      if connection_collection_name in self.db.collection_names():
        logging.warning("Collection '{}' initiation message, collection exits.".format(connection_collection_name))
      else:
        logging.warning(
          "Collection '{}' initiation message, create new collection.".format(connection_collection_name))
        self.db.create_collection(connection_collection_name)

      json_data['updated_date'] = timestamp
      json_data['file_name'] = file_name
      json_data['file_size'] = file_size
      json_data['file_id'] = json_file_id

      check = self.db[connection_collection_name].find_one({conn_key: {'$exists': True}})
      try:
        if check is None:
          self.db[connection_collection_name].insert(json_data)
          status_msg = "Key '{}' not exists, insert new one.".format(conn_key)
          logging.info(status_msg)

        else:

          json_data[conn_key]['version'] = 1 if check[conn_key].get('version') is None else check[
                                                                                              conn_key].get(
            'version') + 1
          self.db[connection_collection_name].find_one_and_replace({conn_key: {'$exists': True}},
                                                                   json_data)
          status_msg = "Key '{}' exists, update record and change updated-date and version.".format(conn_key)
          logging.info(status_msg)

        return {'status': True, 'message': status_msg}

      except pymongo.errors.ConnectionFailure as cf:
        logging.error("ConnectionFailure:{}".format(cf))
      except pymongo.errors.DuplicateKeyError as dk:
        logging.error("DuplicatedKeyError:{}".format(dk))
      except pymongo.errors.OperationFailure as e:
        logging.error("Error Code {}: {}".format(e.code, e.details.get('errmsg')))
    else:
      status_msg = "Object ID: {} for connection ID: {} doesn't exist in GridFS system.".format(json_file_id, conn_key)
      logging.error(status_msg)
    return {'status': False, 'message': status_msg}

  def import_md_json(self, md_collection_name, connection_collection_name, json_file_path):

    if md_collection_name in self.db.collection_names():
      logging.warning("Collection '{}' initiation message, collection exits.".format(md_collection_name))
    else:
      logging.warning("Collection '{}' initiation message, create new collection.".format(md_collection_name))
      self.db.create_collection(md_collection_name)

    if connection_collection_name not in self.db.collection_names():
      logging.error("Collection '{}' error message, no collection exists.".format(connection_collection_name))
      return

    json_files = [x for x in listdir(json_file_path) if x.endswith('_md.json')]

    for json_name in json_files:
      json_key = os.path.splitext(json_name)[0][:-3]
      with open("{}/{}".format(json_file_path, json_name)) as json_file:
        json_data = json.load(json_file)
        if json_key != json_data.get('connection_key'):
          logging.error(
            "JSON file '{}', format doesn't match, connection_key should be the first part of json file name, with end sufix like '_md.json'.".format(
              json_name))
          continue

        check = self.db[connection_collection_name].find_one({json_key: {'$exists': True}})
        if check is None:
          logging.error(
            "No connection is setup in the system for json file '{}', with the connection key '{}'".format(
              json_name, json_key))
          continue
        else:
          dialect = check[json_key].get('dialect')
          if dialect.lower() in support_dialect:
            conn = Connector(check[json_key]).get_connection()

            md_json = DBMetaData(dialect, conn, json_data).export_md_json()
            check = self.db[md_collection_name].find_one({'connection_key': md_json.get('connection_key')})
            md_json['version'] = 1 if check is None or check.get('version') is None else check.get(
              'version') + 1
            self.db[md_collection_name].find_one_and_replace(
              {'connection_key': md_json.get('connection_key')}, md_json, upsert=True)

          else:
            logging.error("DB Connection trying failed, the dialect '{}' is not supported".format(dialect))
            continue

  def list_datasource(self, connection_collection_name):

    result = list(self.db[connection_collection_name].find({}, {'_id': 0, 'updated_date': 0}))
    return [{k: x.get(k).get('desc')} for x in result for k in x]

  def list_metadata(self, md_collection_name, connection_key):
    result = self.db[md_collection_name].find({'connection_key': connection_key})

  def get_login(self, user_collection_name, user_name, user_password):
    result = self.db[user_collection_name].find_one({'user_name': user_name})
    if result is None:
      return None
    elif result.get('user_password') != user_password:
      return 'Failed'
    else:
      return result.get('user_role')

  def upload_temp(self, tempFile):
    fs = gridfs.GridFS(self.db)
    file_id = fs.put(tempFile)
    return file_id

  def delete_temp(self, file_id):
    object_ID = ObjectId(file_id)
    fs = gridfs.GridFS(self.db)
    try:
      fs.delete(object_ID)
      message = "Delete succeed."
      status = True

    except pymongo.errors.OperationFailure as e:
      logging.error(e.details.get('errmsg'))
      message = e
      status = False
    return status


  def check_connection_exit(self, connection_collection_name, conn_key):

    check = self.db[connection_collection_name].find_one({conn_key: {'$exists': True}})
    if check is not None:
      return True
    else:
      return False

  def get_connection_summary(self, connection_collection_name, time_range, start_time, end_time, conn_keys):
    result = []
    if start_time == '' and end_time == '':
      lt_time = datetime.now()
      if time_range == '1':
        gt_time = datetime.now() + timedelta(days=-365)
      elif time_range == '6':
        gt_time = datetime.now() + timedelta(days=-183)
      elif time_range == '3':
        gt_time = datetime.now() + timedelta(days=-93)
      else:
        gt_time = '*'
    else:
      gt_time = start_time
      lt_time = end_time
    logging.info('start_time:'.format(start_time))
    logging.info('end_time:'.format(end_time))
    if gt_time == '*' and len(conn_keys) == 0:
      conn_list = list(self.db[connection_collection_name].find({}).sort("updated_date", -1))
    elif len(conn_keys) == 0:
      conn_list = list(
        self.db[connection_collection_name].find({'updated_date': {'$lt': lt_time, '$gt': gt_time}}).sort(
          "updated_date", -1))
    elif gt_time == '*':
      conn_list = []
      for key in conn_keys:
        chk = self.db[connection_collection_name].find_one({key: {'$exists': True}})
        if chk is not None:
          conn_list.append(chk)
    else:
      conn_list = []
      for key in conn_keys:
        chk = self.db[connection_collection_name].find_one({"$and":[{'updated_date': {'$lt': lt_time, '$gt': gt_time}}, {key: {'$exists': True}}]})
        if chk is not None:
          conn_list.append(chk)

    for conn in conn_list:
      tmp = {}
      for k in conn:
        if type(conn.get(k)) is dict:
          tmp['conn_key'] = k
          tmp['desc'] = conn.get(k).get('desc')
          tmp['version'] = conn.get(k).get('version')
          tmp['detail'] = conn.get(k)
        else:
          tmp[k] = str(conn.get(k))
      result.append(tmp)
    return result

  def get_pattern_summary(self, pattern_collection_name, time_range, start_time, end_time, conn_keys, pattern_types):
    result = []
    if start_time == '' and end_time == '':
      lt_time = datetime.now()
      if time_range == '1':
        gt_time = datetime.now() + timedelta(days=-365)
      elif time_range == '6':
        gt_time = datetime.now() + timedelta(days=-183)
      elif time_range == '3':
        gt_time = datetime.now() + timedelta(days=-93)
      else:
        gt_time = '*'
    else:
      gt_time = start_time
      lt_time = end_time
    logging.info('start_time:'.format(start_time))
    logging.info('end_time:'.format(end_time))
    if gt_time == '*' and len(conn_keys) == 0 and len(pattern_types) == 0:
      pattern_list = list(self.db[pattern_collection_name].find({}).sort("updated_date", -1))
    elif gt_time == '*' and len(conn_keys) == 0 and len(pattern_types) > 0:
      pattern_list = list(self.db[pattern_collection_name].find({'pattern_type': {'$in': pattern_types}}).sort("updated_date", -1))
    elif gt_time == '*' and len(conn_keys) > 0 and len(pattern_types) == 0:
      pattern_list = list(self.db[pattern_collection_name].find({'connection_key': {'$in': conn_keys}}).sort("updated_date", -1))
    elif gt_time == '*' and len(conn_keys) > 0 and len(pattern_types) > 0:
      pattern_list = list(self.db[pattern_collection_name].find({'connection_key': {'$in': conn_keys}, 'pattern_type': {'$in': pattern_types}}).sort("updated_date", -1))
    elif len(conn_keys) == 0 and len(pattern_types) == 0:
      pattern_list = list(
        self.db[pattern_collection_name].find({'updated_date': {'$lt': lt_time, '$gt': gt_time}}).sort(
          "updated_date", -1))
    elif len(conn_keys) > 0 and len(pattern_types) == 0:
      pattern_list = list(
        self.db[pattern_collection_name].find({'updated_date': {'$lt': lt_time, '$gt': gt_time}, 'connection_key': {'$in': conn_keys}}).sort(
          "updated_date", -1))
    elif len(conn_keys) == 0 and len(pattern_types) > 0:
      pattern_list = list(
        self.db[pattern_collection_name].find({'updated_date': {'$lt': lt_time, '$gt': gt_time}, 'pattern_type': {'$in': pattern_types}}).sort(
          "updated_date", -1))
    elif len(conn_keys) > 0 and len(pattern_types) > 0:
      pattern_list = list(
        self.db[pattern_collection_name].find({'updated_date': {'$lt': lt_time, '$gt': gt_time}, 'pattern_type': {'$in': pattern_types}, 'connection_key': {'$in': conn_keys}}).sort(
          "updated_date", -1))

    for pattern in pattern_list:
      pattern['_id'] = str(pattern.get('_id'))

    return pattern_list


  def del_connection_key(self, connection_collection_name, conn_key):

    status = False
    fs = gridfs.GridFS(self.db)
    check = self.db[connection_collection_name].find_one({conn_key: {'$exists': True}})
    if check is not None:
      object_ID = ObjectId(check.get('file_id'))
      if fs.exists(object_ID):
        try:
          fs.delete(object_ID)
          self.db[connection_collection_name].delete_one({conn_key: {'$exists': True}})
          message = "Delete succeed."
          status = True
        except pymongo.errors.OperationFailure as e:
          logging.error(e.details.get('errmsg'))
          message = e
      else:
        message = "Connection Key : {} exist, but GridFS file not exist.".format(conn_key)
    else:
      message = "Connection Key : {} doesn't exist.".format(conn_key)

    return {'status': status, 'message': message}

  def get_connection_key(self, connection_collection_name, conn_key):
    conn = self.db[connection_collection_name].find_one({conn_key: {'$exists': True}})

    if conn is None:
      return None
    else:
      for k in conn:
        if type(conn.get(k)) is dict:
          return conn.get(k)
        else:
          continue


  def get_connection_short(self, connection_collection_name):
    result = []
    conn_list = list(self.db[connection_collection_name].find({}))
    for conn in conn_list:
      for k in conn:
        if type(conn.get(k)) is dict:
          tmp = k
      result.append(tmp)
    return result

  def get_connection_full(self, connection_collection_name):
    result = []
    conn_list = list(self.db[connection_collection_name].find({}))
    for conn in conn_list:
      for k in conn:
        if type(conn.get(k)) is dict:
          tmp = {'conn_key': k, 'desc': conn.get(k).get('desc')}
      result.append(tmp)
    return result


  def get_pattern_type(self, sys_collection_name):
    result = []
    patter_type = self.db[sys_collection_name].find_one({'pattern_type':{'$exists': True}})
    result = patter_type.get('pattern_type')
    return result

  def get_user_usergroup_list(self, sys_user, sys_user_group):
    result = []
    user_list = list(self.db[sys_user].find({}, {'_id': 0, 'user_name': 1}))
    user_group_list = list(self.db[sys_user_group].find({}, {'_id': 0, 'group_name': 1}))
    for user in user_list:
      tmp = {"name": user.get('user_name'), "type": "User"}
      result.append(tmp)

    for user_group in user_group_list:
      tmp = {"name": user_group.get('group_name'), "type": "Group"}
      result.append(tmp)

    return result

  def get_stored_connection_file_id(self, sys_collection_name):
    result = []
    connection_file_id = list(self.db[sys_collection_name].find({}, {'_id': 0, 'file_id': 1}))
    for file in connection_file_id:
      result.append(str(file.get('file_id')))

    return result

  def get_stored_attach_file_id(self, sys_collection_name):
    result = []
    attach_file_id = list(self.db[sys_collection_name].find({'attach_list': {'$exists': True}}, {'_id': 0, 'attach_list.file_id': 1}))

    for file in attach_file_id:
      attach_list = file.get('attach_list')
      for t in attach_list:
        result.append(t.get('file_id'))
    return result

  def clear_all_doc(self):
    deleted_file_id = []
    fs = gridfs.GridFS(self.db)
    # get saved file id from connection collection
    saved_connection_id = self.get_stored_connection_file_id(CON_COLLECTION_NAME)
    saved_attachment_id = self.get_stored_attach_file_id(SYS_PATTERN_NAME)

    saved_object_ID = saved_connection_id + saved_attachment_id

    for f in fs.find():
      object_id = f._file.get('_id')
      str_object_id = str(object_id)
      if str_object_id not in saved_object_ID:
        self.delete_temp(object_id)
        deleted_file_id.append(str_object_id)

    return deleted_file_id

  def save_json_to_collection(self, json, collection):
    result = self.db[collection].insert_one(json)
    pattern_id = str(result.inserted_id)


    return pattern_id

  def del_pattern(self, pattern_id, operate_user):
    chk = self.db[SYS_PATTERN_NAME].find_one({'_id': ObjectId(pattern_id)})
    if chk is not None:
      if chk.get('created_user') == operate_user:
        status = True
        mgs = "Pattern deleted."
        attach_list = chk.get('attach_list')
        for attach in attach_list:
          self.delete_temp(attach.get('file_id'))
        self.db[SYS_PATTERN_NAME].delete_one({'_id': ObjectId(pattern_id)})
      else:
        status = False
        mgs = "You are not the owner of this pattern, permission denied."
    else:
      status = False
      mgs = "Pattern doesn't exist."

    return {'status': status, 'mgs': mgs}

  def test_sql_pattern(self, pattern_id):
    chk = self.db[SYS_PATTERN_NAME].find_one({'_id': ObjectId(pattern_id)})
    status = False
    mgs = 'Query test passed.'
    text = ''

    if chk is not None:
      if chk.get('pattern_type') is None or chk.get('pattern_type') != 'SQL':
        mgs = "Your pattern is not the SQL pattern, system couldn't test it."
      elif chk.get('pattern_text') is None or chk.get('pattern_text') == '':
        mgs = "Your pattern text is empty, system couldn't test it."
      elif chk.get('connection_key') is None or chk.get('connection_key') == '':
        mgs = "Your pattern is not set up for one validated data source connection, system couldn't test it. "
      else:
        text = chk.get('pattern_text')
        conn_key = chk.get('connection_key')
        if chk.get('condition_subArea') is not None and len(chk.get('condition_subArea')) > 0:
          condition = chk.get('condition_subArea')
          text = self.create_condition(text, condition)
        if chk.get('selection_subArea') is not None and len(chk.get('selection_subArea')) > 0:
          selection = chk.get('selection_subArea')
          text = self.create_selection(text, selection)

      if len(text) > 0:
        if text[len(text) - 1:] == ';':
          text = text[:len(text) - 1]

        sql = text + ' limit 1;'

        conn_info = self.get_connection_key(CON_COLLECTION_NAME, conn_key)
        db = Connector(conn_info)
        conn = db.get_connection()
        try:
          conn.execute(sql)
        except sqlalchemy.exc.StatementError, exc:
          status = False
          mgs = exc.message
        finally:
          conn.close()
    else:
      mgs = "Pattern doesn't exist."
    return {'status': status, 'mgs': mgs}

  def test_sql_pattern_draft(self, input_data):

    status = False
    mgs = 'Query test passed.'
    text = ''

    if input_data is not None:
      if input_data.get('pattern_type') is None or input_data.get('pattern_type') != 'SQL':
        mgs = "Your pattern is not the SQL pattern, system couldn't test it."
      elif input_data.get('pattern_text') is None or input_data.get('pattern_text') == '':
        mgs = "Your pattern text is empty, system couldn't test it."
      elif input_data.get('conn_key') is None or input_data.get('conn_key') == '':
        mgs = "Your pattern is not set up for one validated data source connection, system couldn't test it. "
      else:
        text = input_data.get('pattern_text')
        conn_key = input_data.get('conn_key').get('conn_key')
        if input_data.get('condition_list') is not None and len(input_data.get('condition_list')) > 0:
          condition = input_data.get('condition_list')
          text = self.create_condition(text, condition)
        if input_data.get('selection_list') is not None and len(input_data.get('selection_list')) > 0:
          selection = input_data.get('selection_list')
          text = self.create_selection(text, selection)

      if len(text) > 0:
        if text[len(text) - 1:] == ';':
          text = text[:len(text) - 1]
        sql = text + ' limit 1;'

        conn_info = self.get_connection_key(CON_COLLECTION_NAME, conn_key)

        db = Connector(conn_info)
        conn = db.get_connection()
        if type(conn) == str:
          mgs = conn
        else:
          try:
            conn.execute(sql)
          except sqlalchemy.exc.StatementError, exc:
            status = False
            mgs = exc.message
          finally:
            conn.close()
    else:
      mgs = "Pattern doesn't exist."
    return {'status': status, 'mgs': mgs}

  def get_pattern_summary_by_user(self, user):
    group_list = self.get_user_group(user)
    group_list.append(user)
    result = list(self.db[SYS_PATTERN_NAME].find({'user_open_list.name': {'$in': group_list}, 'pattern_type': 'SQL'}))
    for r in result:
      r['_id'] = str(r.get('_id'))

    return result

  def test_sql_query(self, input_data):
    status = False
    mgs = 'Query test passed.'
    text = ''

    if input_data is not None:
      text = input_data.get('query_text')
      conn_key = input_data.get('conn_key')

      if len(text) > 0:
        if text[len(text) - 1:] == ';':
          text = text[:len(text) - 1]
        sql = text + ' limit 1;'

        conn_info = self.get_connection_key(CON_COLLECTION_NAME, conn_key)

        db = Connector(conn_info)
        conn = db.get_connection()
        if type(conn) == str:
          mgs = conn
        else:
          try:
            conn.execute(sql)
          except sqlalchemy.exc.StatementError, exc:
            status = False
            mgs = exc.message
          finally:
            conn.close()
    else:
      mgs = "Query doesn't have text."
    return {'status': status, 'mgs': mgs}

  def create_sql_by_pattern(self,text, condition, selection):
    if text is not None and text != "":
      text = self.create_condition(text, condition)
      text = self.create_selection(text, selection)

      return text

  def create_condition(self, text, inputs):
    if len(inputs) > 0:
      for input in inputs:
        name = input.get('name')
        value = input.get('value')
        # do replace condition with the input values

        condition_name = name[1:]
        cond_type = condition_name.split('_')[0]
        if value is None:
          if cond_type == 'str':
            text = text.replace(name, "''")
          elif cond_type == 'int':
            text = text.replace(name, "1")
          elif cond_type == 'list':
            text = text.replace(name, "'',''")
          elif cond_type == 'boolean':
            text = text.replace(name, "0")
        else:
          # need action from value
          if cond_type == 'str':
            text = text.replace(name, "'{}'".format(value))
          elif cond_type == 'int':
            text = text.replace(name, value)
          elif cond_type == 'list':
            text = text.replace(name, ','.join(["'{}'".format(x) for x in value.split(',')]))
          elif cond_type == 'boolean':
            text = text.replace(name, "1" if value else "0")


    if text[len(text)-1:] == ';':
      text = text[:len(text)-1]

    return text

  def create_selection(self, text, inputs):
    selected_column = []
    if len(inputs) > 0:
      text_first_part = self.find_between(text.lower(), 'select', 'from')
      text_rest_part = self.find_rest(text.lower(), 'from')
      col_list = [a.lower() for a in text_first_part.split(',')]

      for input in inputs:
        name = input.get('col_name')
        value = input.get('nick_name')
        selected = input.get('value')
        if (selected is None or selected) :
          selected_column.append('{} AS {}'.format(name, value))

      str_col = ','.join(selected_column)
      text = 'select  {} from {} '.format(str_col,text_rest_part)

    return text

  def get_user_group(self, user):
    group_list = [k.get('group_name') for k in self.db[USER_GROUP_COLLECTION_NAME].find({'members': user}, {'_id': 0, 'group_name': 1})]
    return group_list

  def get_pattern_summary_by_user(self, user):
    group_list = self.get_user_group(user)
    group_list.append(user)
    result = list(self.db[SYS_PATTERN_NAME].find({'user_open_list.name': {'$in': group_list}, 'pattern_type': 'SQL'}))
    for r in result:
      r['_id'] = str(r.get('_id'))

    return result


  def find_between(self, s, first, last):
    try:
      start = s.index(first) + len(first)
      end = s.index(last, start)
      return s[start:end]
    except ValueError:
      return ""

  def find_rest(self, s, first):
    try:
      start = s.index(first) + len(first)
      return s[start:]
    except ValueError:
      return ""

# def main():
#     obj = mongodbbatch(host="172.18.60.20", port="27017", db="DDDB")
#     fs = gridfs.GridFS(obj.get_db())
#     result = obj.get_user_group('yue.ming@wdc.com')
#     print result




if __name__ == '__main__':
    main()
