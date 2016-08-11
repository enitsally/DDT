from sqlalchemy import create_engine, exc
import logging
import urllib


class Connector:
    def __init__(self, conn_info):
        self.dialect = conn_info.get('dialect')
        self.driver = conn_info.get('driver')
        self.host = conn_info.get('host')
        self.port = conn_info.get('port')
        self.uid = conn_info.get('uid')
        self.upw = conn_info.get('upw')
        self.db = conn_info.get('db')

    def get_connection(self):
        error_msg = ''
        # Connection for Netezza using SQLalchemy
        if self.dialect == 'netezza':
            odbc_connection = "DRIVER={" + self.driver + "}; SERVER=" + self.host + "; PORT=" + self.port + "; DATABASE=" + self.db + "; UID=" + self.uid + "; PWD=" + self.upw + ";"
            params = urllib.quote_plus(odbc_connection)
            try:
                engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))
                conn = engine.connect()
                return conn
            except exc.DBAPIError as err:
                logging.error("Invalidated connection:{}".format(err.message))
                error_msg = err.message
        elif self.dialect == 'redshift':
            odbc_connection = "{}://{}:{}@{}:{}/{}".format(self.driver, self.uid, self.upw, self.host, self.port, self.db)
            try:
                engine = create_engine(odbc_connection)
                conn = engine.connect()
                return conn
            except exc.DBAPIError as err:
                logging.error("Invalidated connection:{}".format(err.message))
                error_msg = err.message
        else:
            logging.error("No connection dialect is matched in the system, for dialect '{}'".format(self.dialect))

        return error_msg

    def connection_test(self):
        result = self.get_connection()
        if type(result) == str:
          return {'status': False, 'message': result}
        else:
          return {'status': True, 'message': None}
