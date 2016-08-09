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

        # Connection for Netezza using SQLalchemy
        if self.dialect == 'netezza':
            odbc_connection = "DRIVER={" + self.driver + "}; SERVER=" + self.host + "; PORT=" + self.port + "; DATABASE=" + self.db + "; UID=" + self.uid + "; PWD=" + self.upw + ";"
            params = urllib.quote_plus(odbc_connection)
            try:
                engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(params))
                conn = engine.connect()
            except exc.DBAPIError as err:
                if err.connection_invalidated:
                    logging.error("Invalidated connection:{}".format(self.dialect))
                else:
                    raise

            return conn
        elif self.dialect == 'redshift':
            odbc_connection = "{}://{}:{}@{}:{}/{}".format(self.driver, self.uid, self.upw, self.host, self.port, self.db)
            try:
                engine = create_engine(odbc_connection)
                conn = engine.connect()
            except exc.DBAPIError as err:
                if err.connection_invalidated:
                    logging.error("Invalidated connection:{}".format(self.dialect))
                else:
                    raise

            return conn
        else:
            logging.error("No connection dialect is matched in the system, for dialect '{}'".format(self.dialect))

        return None

    def connection_test(self):
        if self.get_connection() is not None:
          return True
        else:
          return False
