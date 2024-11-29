from plugins.sqlite.table import SQLiteTable
from models.model_estado import Estado

class SQLiteEstados(SQLiteTable):
    
    def __init__(self, db_location):
        super().__init__(db_location)
        self.table_name = "estados"

    def create_table(self):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            estado TEXT,
            capital TEXT,
            regiao TEXT,
            populacao INTEGER
        );
        """
        self._conn.execute(create_table_query)
        
    def insert_df(self, df):
        objects = [Estado(**row.to_dict()) for _, row in df.iterrows()]
        
        query = f"""
        INSERT INTO {self.table_name} (estado, capital, regiao, populacao)
        VALUES (?, ?, ?, ?);
        """
        values = [(obj.estado, obj.capital, obj.regiao, obj.populacao) for obj in objects]
        self.executemany(query=query, values=values)
        
    def upsert_df(self, df):
        objects = [Estado(**row.to_dict()) for _, row in df.iterrows()]
        
        query = f"""
        INSERT INTO {self.table_name} (estado, capital, regiao, populacao)
        VALUES (?, ?, ?, ?);
        """
        
        existing_query = f"SELECT estado FROM {self.table_name}"
        existing_records = set(estado[0] for estado in self.execute(existing_query).fetchall())
        values = [
            (obj.estado, obj.capital, obj.regiao, obj.populacao)
            for obj in objects
            if obj.estado not in existing_records
        ]
        self.executemany(query=query, values=values)
        
    def read_all(self):
        query = f"""
        SELECT * FROM {self.table_name}
        """
        return self.read(query)