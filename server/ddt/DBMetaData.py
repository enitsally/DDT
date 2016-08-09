import logging
from sqlalchemy import exc
from datetime import datetime


class DBMetaData:
    def __init__(self, dialect, conn, objects):
        self.dialect = dialect
        self.conn = conn
        self.connection_key = objects.get('connection_key')
        self.data_object = objects.get('data_object')

    def export_md_json(self):
        md_list = []
        timestamp = datetime.now()

        # Netezza Database Connection
        if self.dialect in ('netezza', 'redshift'):
            for obj in self.data_object:
                name = obj.get('name')
                type = obj.get('type')
                schema = obj.get('schema')

                if name is None or type is None:
                    logging.error(
                        "Import for data object name or type is incorrect. Name: {}, Type: {}".format(name, type))
                    continue
                else:
                    if schema is not None:
                        sql_md = '''SELECT TABLE_CATALOG as table_catalog, TABLE_SCHEMA as table_schema
                                    FROM INFORMATION_SCHEMA.{}S
                                    WHERE TABLE_NAME = '{}' and TABLE_SCHEMA = '{}'
                                '''.format(type, name, schema)
                    else:
                        sql_md = '''SELECT TABLE_CATALOG as table_catalog, TABLE_SCHEMA as table_schema
                                    FROM INFORMATION_SCHEMA.{}S
                                    WHERE TABLE_NAME = '{}'
                                '''.format(type, name)

                    try:
                        mmd = self.conn.execute(sql_md)
                        md = mmd.first()

                        if md is None:
                            logging.error("NO object '{}, type '{}' exists in the meta data.".format(name, type))
                        else:

                            tmp = dict((k.lower(), v) for k, v in md.items())
                            tmp['name'] = name
                            tmp['type'] = type

                            sql = '''
                                SELECT COLUMN_NAME as column_name, DATA_TYPE as data_type
                                FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE  TABLE_NAME = '{}' AND TABLE_CATALOG = '{}' AND TABLE_SCHEMA = '{}'
                            '''.format(name, tmp.get('table_catalog'), tmp.get('table_schema'))

                            result = self.conn.execute(sql)
                            tmp['meta_data'] = []
                            for r in result:
                                tmp['meta_data'].append(dict(r.items()))
                            tmp['updated_date'] = timestamp
                            md_list.append(tmp)

                    except exc.DisconnectionError as de:
                        logging.error("Disconnection Error:{}".format(de))
                    except exc.OperationalError as oe:
                        logging.error("Operational Error: {}".format(oe))
                    except exc.ProgrammingError as pe:
                        print pe
                        logging.error("Programming Error: {}".format(pe))

            return {
                "connection_key": self.connection_key,
                "data_object": md_list,
                "updated_date": timestamp
            }
        # Other database connections
        else:
            return {}
