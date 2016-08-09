import json
from os import listdir
import os
from pymongo import MongoClient
from datetime import datetime
import pymongo
import gridfs
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

        result = list(self.db[connection_collection_name].find({}, {'_id': 0, 'updated_date':0}))
        return [{k: x.get(k).get('desc')} for x in result for k in x]

    def list_metadata(self, md_collection_name, connection_key):
        result = self.db[md_collection_name].find({'connection_key':connection_key})

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

# def main():
#     obj = mongodbbatch(host="172.18.60.20", port="27017", db="DDDB")
#     db = obj.get_db()
#     print db
#     # obj.import_connection_json("connection", "json/connection")
#     # obj.import_md_json("meta_data", "connection", "json/metadata")
#     print obj.list_datasource("connection")
#
#
# if __name__ == '__main__':
#     main()
