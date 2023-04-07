import pyodbc


class DatabaseConnection(object):
    def __init__(self, connection_parameters):

        super(DatabaseConnection, self).__init__()

        self.connection_parameters = connection_parameters

        self.db_session = None
        self.db_cursor = None
        self.table_info = {}
        self.column_info = {}
        self.table_relations = {}
        self.child_table_relations = {}

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
    
    @property
    def is_connected(self):
        if self.db_session is not None:
            return True
        return False

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
    
    def get_transport_where_clause(self, table_name):
        where_clause = ""
        table_info = self.table_info.get(table_name, None)
        if table_info is not None:
            return table_info.TransportWhereClause
        return where_clause
    
    def get_db_object(self, table_name, query_dict, condition):
        where_clause = ""
        query_elements = []
        for column_name, column_value in query_dict.items():
            query_elements.append(f"{column_name} = '{column_value}' ")

        where_clause = condition.join(query_elements)
        string_query = f"select * from {table_name} where {where_clause}"

        if where_clause.strip() != "" and len(query_elements) > 0:
            return self.run_db_query(string_query)
    
    def get_object_columns(self, db_row):
        if isinstance(db_row, pyodbc.Row):
            columns = [column[0] for column in db_row.cursor_description]
            return columns
        return []
    
    def load_session_data(self):
        self.load_table_relations_data()
        self.load_column_data()
        self.load_table_data()

    def load_table_data(self):
        query = "select * from DialogTable order by TableName"
        query_result = self.run_db_query(query)

        for row in query_result:
            self.table_info[row.TableName] = row

    def load_column_data(self):
        query = "select * from DialogColumn order by Caption"
        query_result = self.run_db_query(query)

        for row in query_result:
            self.column_info[row.ColumnName] = row

    def load_table_relations_data(self):
        query = "select \
        BASE.Caption, \
        BASE.IsConnectedInTransport as 'Relation',\
        BASE.ParentTable,\
        Base.ParentColumn, \
        BASE.ChildTable,  \
        Base.ChildColumn  \
        from QBM_VQBMRelationALL BASE \
        --where isnull(BASE.IsConnectedInTransport, 0) > 0 \
        order by BASE.ParentTable, BASE.ChildTable asc"

        query_result = self.run_db_query(query)
        self.save_relation_data(query_result)

    def save_relation_data(self, query_result):
        for row in query_result:
            relation = {
                "Caption": row.Caption,
                "ParentTable": row.ParentTable, 
                "ParentColumn": row.ParentColumn, 
                "Relation": row.Relation,
                "ChildTable": row.ChildTable,
                "ChildColumn": row.ChildColumn,
                "InitialRelationState": row.Relation
                }

            if row.ParentTable not in self.table_relations.keys():
                self.table_relations[row.ParentTable] = [relation]

            if relation not in self.table_relations[row.ParentTable]:
                self.table_relations[row.ParentTable].append(relation)
            
            if row.ChildTable not in self.table_relations.keys():
                self.table_relations[row.ChildTable] = [relation]
                
            if relation not in self.table_relations[row.ChildTable]:
                self.table_relations[row.ChildTable].append(relation)

            if row.ChildTable not in self.child_table_relations.keys():
                self.child_table_relations[row.ChildTable] = [relation]
                
            if relation not in self.child_table_relations[row.ChildTable]:
                self.child_table_relations[row.ChildTable].append(relation)

    def get_table_display_pattern(self, table_name):
        table_info = self.table_info.get(table_name, None)
        if table_info is not None:
            return table_info.DisplayPattern
        return None
    
    def get_object_display_name(self, table_name, db_object_attrs):
        display_pattern = self.get_table_display_pattern(table_name)
        db_objects = self.get_db_object(table_name, db_object_attrs, "and")
        objects_display_name = []
        for db_object in db_objects:
            objects_display_name.append(self.parse_object_display(db_object, display_pattern))
        return " ".join(objects_display_name)

    
    def parse_object_display(self, db_object, display_pattern):
        object_display = display_pattern.upper()
        if "%" in display_pattern:
            for column_name in self.get_object_columns(db_object):
                if column_name.upper() in object_display:
                    column_value =  db_object.__getattribute__(column_name)
                    if column_value is None:
                        column_value = ""
                    object_display = object_display.replace(column_name.upper(), str(column_value))
            object_display = object_display.replace("%", "")
        return object_display