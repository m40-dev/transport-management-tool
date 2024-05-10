import pyodbc, copy, re
import urllib

class DatabaseConnection(object):
    def __init__(self, application, connection_parameters={}):

        super(DatabaseConnection, self).__init__()
        self.application=application
        self.connection_parameters = connection_parameters
        self.db_session = None
        self.db_cursor = None
        self.table_info = {}
        self.column_info = {}
        self.table_relations = {}
        self.child_table_relations = {}
        
    def connect_db(self):
        # Some other example server values are
        # ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
        connection_string = self.get_db_connection_string()
        if connection_string:
            connection = pyodbc.connect(connection_string)
        
            if connection:
                self.db_session = connection
                self.db_cursor = connection.cursor()
                return True
        return False
    
    def get_db_connection_string(self):
        # 'DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=no;UID='+username+';PWD='+ password
        connection_string = None
        EncryptConnection = self.connection_parameters.get("EncryptConnection", True)
        
        if EncryptConnection:
            EncryptConnection = "yes"
        else:
            EncryptConnection = "no"

        ServerAddress = self.connection_parameters.get("ServerAddress", None)
        DatabaseName = self.connection_parameters.get("DatabaseName", None)
        SQLUserName = self.connection_parameters.get("SQLUserName", None)
        SQLPassword = self.connection_parameters.get("SQLPassword", None)

        SQLPassword = SQLPassword.replace("}", '}}')

        if ServerAddress and DatabaseName and SQLUserName and SQLPassword:
            connection_string = "DRIVER={ODBC Driver 18 for SQL Server};" \
                f"SERVER={ServerAddress};" \
                f"DATABASE={DatabaseName};" \
                f"ENCRYPT={EncryptConnection};" \
                f"UID={SQLUserName};" \
                'PWD={' + SQLPassword + '};' \
                "App={" + self.application.application_name + "}" 
            if EncryptConnection.upper() == "NO":
                connection_string += ';TrustServerCertificate=yes'

        return connection_string

    def get_connection_string(self):
        # "Data Source=<Database server>;Initial Catalog=<Database name>;User ID=<Database user>;Password=<Password>"
        connection_string = None
        EncryptConnection = self.connection_parameters.get("EncryptConnection", True)
        
        if EncryptConnection:
            EncryptConnection = "yes"
        else:
            EncryptConnection = "no"

        ServerAddress = self.connection_parameters.get("ServerAddress", None)
        DatabaseName = self.connection_parameters.get("DatabaseName", None)
        SQLUserName = self.connection_parameters.get("SQLUserName", None)
        SQLPassword = self.connection_parameters.get("SQLPassword", None)

        SQLPassword = SQLPassword.replace("}", '}}')

        if ServerAddress and DatabaseName and SQLUserName and SQLPassword:
            connection_string = f'Data Source={ServerAddress};Initial Catalog={DatabaseName};User ID={SQLUserName};Password=' + '{' + SQLPassword + '}'
            if EncryptConnection.upper() == "NO":
                connection_string += ';TrustServerCertificate=yes'
        return connection_string
        


    def get_authentication_string(self):

        authentication_string = None

        ApplicationUserName = self.connection_parameters.get("ApplicationUserName", None)
        ApplicationPassword = self.connection_parameters.get("ApplicationPassword", None)

        if ApplicationUserName and ApplicationPassword:
            authentication_string = f'Module="DialogUser";User="{ApplicationUserName}";Password="{ApplicationPassword}"'
        return authentication_string

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
        self.load_table_data()
        self.load_column_data()

    def load_table_data(self):
        query = "select * from DialogTable order by TableName"
        query_result = self.run_db_query(query)

        for row in query_result:
            self.table_info[row.TableName] = row

    def load_column_data(self):
        query = "select DialogTable.TableName, DialogColumn.ColumnName from DialogColumn join DialogTable on DialogColumn.UID_DialogTable=DialogTable.UID_DialogTable"
        query_result = self.run_db_query(query)

        for row in query_result:
            if row.TableName not in self.column_info.keys():
                self.column_info[row.TableName] = [row.ColumnName.upper()]
            else:
                self.column_info[row.TableName].append(row.ColumnName.upper())

    def string_list_to_sql(self, input_string):
        sql_list = f"'{input_string.strip()}'"
        if "," in input_string:
            input_list = [x.strip() for x in input_string.split(",")]
            input_list = list(filter(None, input_list))
            sql_list = "'" + "', '".join(input_list) + "'"
        return sql_list

    def date_to_sql(self, date):
        return date.toString("yyyy-MM-dd")

    def run_global_query(self, min_date=None, system_users=None, include_partial_results=False):
        data_rows = {}
        
        if not min_date and not system_users:
            return data_rows

        system_user_where_clause = ""
        min_date_where_clause = ""
        if system_users:
            system_users_list = self.string_list_to_sql(system_users)
            system_user_where_clause = f"xuserinserted in ({system_users_list}) or xuserupdated in ({system_users_list})"
        
        if min_date:
            str_date = self.date_to_sql(min_date)
            min_date_where_clause = f"xdateinserted >= '{str_date}' or xdateupdated >= '{str_date}'"

        for table_name, table_columns_list in self.column_info.items():
            has_min_date_columns = False
            has_sys_user_columns = False
            query = None

            if "XDATEINSERTED" in table_columns_list and "XDATEUPDATED" in table_columns_list:
                has_min_date_columns = True
                
            if "XUSERINSERTED" in table_columns_list and "XUSERUPDATED" in table_columns_list:
                has_sys_user_columns = True

            if min_date and has_min_date_columns and (not system_users or include_partial_results):
                query = f"select * from {table_name} where ({min_date_where_clause}) order by xdateupdated desc, xdateinserted desc"

            if system_users and has_sys_user_columns and (not min_date or include_partial_results):
                query = f"select * from {table_name} where ({system_user_where_clause})"
                if has_min_date_columns:
                    query += " order by xdateupdated desc, xdateinserted desc"

            if min_date and system_users and has_min_date_columns and has_sys_user_columns:
                query = f"select * from {table_name} where ({min_date_where_clause}) and ({system_user_where_clause}) order by xdateupdated desc, xdateinserted desc"
            # print(table_name, query)
            if query:
                query_result = self.run_db_query(query)
                if len(query_result) > 0:
                    data_rows[table_name] = query_result
        return data_rows

    def get_change_labels(self, list_all=False):
        query = "select * from DialogTag where isClosed=0 order by Ident_DialogTag asc"
        if list_all:
            query = "select * from DialogTag order by Ident_DialogTag asc"
        query_result = self.run_db_query(query)
        return query_result

    def get_objects_by_change_label(self, change_label_uid):
        objectkeys = self.get_tagged_object_keys(change_label_uid)
        return self.get_objects_by_xobjectkey(objectkeys)

    def get_objects_by_xobjectkey(self, objectkey_list):
        data_rows = {}
        for objectkey in objectkey_list:
            objectkey = objectkey.strip()
            table_name = self.get_objectkey_table(objectkey)
            if table_name is not None:
                query = f"select * from {table_name} where XObjectKey = '{objectkey}'"
                query_result = self.run_db_query(query)
                if len(query_result) > 0:
                    if table_name not in data_rows.keys():
                        data_rows[table_name] = query_result
                    else:
                        data_rows[table_name] += query_result
        return data_rows

    def get_tagged_object_keys(self, change_label_uid):
        # Get ObjectKeys of the tagged Items
        object_keys = []
        data_rows = []
        query = f"select ObjectKey from DialogTaggedItem where UID_DialogTag in ('{change_label_uid}')"
        query_result = self.run_db_query(query)

        if len(query_result) > 0:
            data_rows += query_result

        # Get ObjectKeys of the tagged changes
        query = f"select ObjectKey from QBMTaggedChange where UID_DialogTag in ('{change_label_uid}')"
        query_result = self.run_db_query(query)

        if len(query_result) > 0:
            data_rows += query_result

        for db_row in data_rows:
            raw_objectkey = db_row.ObjectKey
            if raw_objectkey not in object_keys:
                object_keys.append(raw_objectkey)

        return object_keys

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
                # "Relation": row.Relation,
                "Relation": 0,
                "ChildTable": row.ChildTable,
                "ChildColumn": row.ChildColumn,
                "InitialRelationState": row.Relation
                }

            if row.ParentTable not in self.table_relations.keys():
                self.table_relations[row.ParentTable] = [relation]

            if relation not in self.table_relations[row.ParentTable]:
                self.table_relations[row.ParentTable].append(relation)
            
            if row.ChildTable not in self.child_table_relations.keys():
                self.child_table_relations[row.ChildTable] = [relation]
                
            if relation not in self.child_table_relations[row.ChildTable]:
                self.child_table_relations[row.ChildTable].append(relation)

    def get_table_display_pattern(self, table_name):
        table_info = self.table_info.get(table_name, None)
        if table_info is not None:
            return table_info.DisplayPattern
        return None
    
    def get_object_display_name(self, table_name, db_object):
        display_pattern = self.get_table_display_pattern(table_name)
        if display_pattern:
            return self.parse_object_display(db_object, display_pattern)

        if "XObjectKey" in self.get_object_columns(db_object):
            return f"Object without display - {db_object.XObjectKey}"
        
        return "Object without display"
        
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

    def get_table_extension(self, table_name):
        initial_relations = self.table_relations.get(table_name, None)
        
        if initial_relations is None:
            return {}
        
        relation_data = self.set_relation_data_type(initial_relations, "ParentRelation")
        return {table_name: relation_data}

    def set_relation_data_type(self, initial_relations, relation_type):
        relation_data = copy.deepcopy(initial_relations)
        for relation in relation_data:
            relation["RelationType"] = relation_type
        return relation_data

    def get_table_initial_relations(self, table_name, extended_view=False):
        initial_relations = self.child_table_relations.get(table_name, None)
        if initial_relations is None:
            return {}

        relation_data = self.set_relation_data_type(initial_relations, "ChildRelation")
        #convert list of table relations into dict 
        initial_relations = {table_name: relation_data}

        if not extended_view:
            return initial_relations

        relation_tables = []
        extended_relations = self.table_relations.get(table_name, None)
        
        if not extended_relations:
            return initial_relations

        for relation in extended_relations:
            child_table = relation.get("ChildTable", None)
            if child_table is not None:
                if child_table != table_name and child_table not in relation_tables:
                    relation_tables.append(child_table)
            
        for relation_table in relation_tables:
            new_table_relations = self.child_table_relations.get(relation_table, None)

            if new_table_relations is not None and relation_table not in initial_relations.keys():
                initial_relations[relation_table] = self.set_relation_data_type(new_table_relations, "ChildRelation")
        
        relations_sorted = dict(sorted(initial_relations.items()))
        return relations_sorted

    def extend_table_relations(self, current_relations, new_relations):
        current = current_relations

        new = new_relations
        if new is None:
            return current
        
        for relation in new:
            check = next((current_item for current_item in current 
                          if current_item["ParentTable"] == relation["ParentTable"] 
                          and current_item["ChildTable"] == relation["ChildTable"]), 
                          None)
            if check is None:
                current.append(relation)
            else:
                continue
        return current

    def get_objectkey_table(self, input_string):
        table_name = None
        regex = r"<T>(.*?)</T>"
        if input_string is not None:
            match = re.search(regex, input_string)
            if match:
                table_name = match.group(1)
        return table_name