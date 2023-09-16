import psycopg2


class Database:
    def __init__(self, host: str = "localhost",
                 port: str = "5432",
                 dbname: str = "postgres",
                 user: str = "postgres",
                 password: str = "postgres"):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.conn = psycopg2.connect(f'host={host} port={port} dbname={dbname} '
                                     f'user={user} password={password}')
        self.cursor = self.conn.cursor()

    def get_tables(self) -> list[str]:
        with self.conn:
            sql = """SELECT table_name FROM information_schema.tables
                     WHERE table_schema = 'public'
                     AND table_type = 'BASE TABLE'"""
            self.cursor.execute(sql)
            return [tpl[0] for tpl in self.cursor.fetchall()]

    def get_values(self, table_name: str) -> list[tuple]:
        with self.conn:
            try:
                main_sql = f"SELECT * FROM {table_name};"
                self.cursor.execute(main_sql)
                return self.cursor.fetchall()
            except Exception as e:
                print(e)
                return [()]

    def add_values(self, table_name: str, **kwargs) -> bool:
        with self.conn:
            f_names = ",".join(kwargs.keys())
            main_sql = f"INSERT INTO {table_name}({f_names}) VALUES {','.join(['?'*len(kwargs)])},{tuple(kwargs.values())};"
            try:
                self.cursor.execute(main_sql)
                self.conn.commit()
                return True
            except Exception as e:
                print(e)
                return False

    def update_values(self, table_name: str, **kwargs) -> bool:
        with self.conn:
            main_sql = f"UPDATE {table_name} SET {kwargs['update']} = {kwargs['update_value']} WHERE {kwargs['con']} " \
                       f"= {kwargs['con_value']};"
            try:
                self.cursor.execute(main_sql)
                return True
            except Exception as e:
                print(e)
                return False

    def clear_values(self, table_name: str) -> bool:
        with self.conn:
            main_sql = f"DELETE FROM {table_name};"
            try:
                self.cursor.execute(main_sql)
                self.conn.commit()
                return True
            except Exception as e:
                print(e)
                return False

# nickname user_id comment is_violent
