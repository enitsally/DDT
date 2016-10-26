import json
from os import listdir
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
import pymongo
import gridfs
import StringIO
from DBFactory import Connector
from DBMetaData import DBMetaData

import logging

logging.basicConfig()
logging.getLogger("datadiscovery.demo").setLevel(logging.DEBUG)

support_dialect = ['netezza', 'sqlsever', 'redshift', 'mysql']


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

  def get_stored_file_id(self, sys_collection_name):
    result = []
    connection_file_id = list(self.db[sys_collection_name].find({}, {'_id': 0, 'file_id': 1}))
    for file in connection_file_id:
      result.append(str(file.get('file_id')))

    return result

  def clear_all_doc(self,sys_collection_name):
    fs = gridfs.GridFS(self.db)
    saved_object_ID = self.get_stored_file_id(sys_collection_name)
    for f in fs.find():
      object_id = f._file.get('_id')
      str_object_id = str(object_id)
      if str_object_id in saved_object_ID:
        print "Import object id: ",str_object_id
      else:
        print "Delete object id:", str_object_id
        self.delete_temp(object_id)
    return True

  def save_json_to_collection(self, json, collection):
    result = self.db[collection].insert_one(json)
    pattern_id = str(result.inserted_id)

    return pattern_id

# def main():
#     obj = mongodbbatch(host="172.18.60.20", port="27017", db="DDDB")
#     fs = gridfs.GridFS(obj.get_db())
#     saved_object_ID = obj.get_stored_file_id('connection')
#     for f in fs.find():
#       object_id = f._file.get('_id')
#       str_object_id = str(object_id)
#       if str_object_id in saved_object_ID:
#         print "Import object id: ",str_object_id
#       else:
#         print "Delete object id:", str_object_id
#         obj.delete_temp(object_id)
#
#
#
#
#
# if __name__ == '__main__':
#     main()
