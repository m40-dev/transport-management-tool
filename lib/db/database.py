import pyodbc

class DatabaseConnection(object):
    def __init__(self, connection_parameters):

        super(DatabaseConnection, self).__init__()

        self.connection_parameters = connection_parameters

        self.db_session = None
        self.db_cursor = None

        self.connect_db()

    def connect_db(self):
        # Some other example server values are
        # server = 'localhost\sqlexpress' # for a named instance
        # server = 'myserver,port' # to specify an alternate port
        # server = 'tcp:myserver.database.windows.net' 
        # database = 'mydb' 
        # username = 'myusername' 
        # password = 'mypassword' 

        server = self.connection_parameters["server_address"]
        database = self.connection_parameters["database_name"]
        username = self.connection_parameters["user_name"]
        password = self.connection_parameters["user_password"]

        # ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
        connection = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=no;UID='+username+';PWD='+ password)
        
        if connection:
            self.db_session = connection
            self.db_cursor = connection.cursor()

    def disconnect_db(self):
        if self.db_cursor is not None:
            self.db_cursor.close()
        
        if self.db_session is not None:
            self.db_session.close()

    def run_db_query(self, string_query):
        if self.db_cursor is None or self.db_session is None:
            return False

        self.db_cursor.execute(string_query)

        data = self.db_cursor.fetchall()
        return data