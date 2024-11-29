import sqlite3
import pandas as pd
from typing import List, Tuple

class SQLiteTable():
    
    def __init__(self, db_location) -> None:
        self._conn = sqlite3.connect(db_location)
        
    def executemany(self, query:str, values: List[Tuple]):
        """
        Executa query SQL em massa

        :param query: comando SQL, normalmente do tipo INSERT
        :param values: tupla de valores que serão iseridos na tabela
        """
        try:
            self._conn.executemany(query, values)
            self.commit()
        except:
            self.rollback()
            
    def read(self, query: str, **pd_kwargs) -> pd.DataFrame:
        """
        Executa query SQL

        :param query: comando SQL, normalmente do tipo SELECT
        :returns: Pandas DataFrame com o resultado da consulta
        """
        return pd.read_sql(query, self._conn, **pd_kwargs)
    
    def commit(self):
        """
        Conclui transação SQL
        """
        self._conn.commit()

    def rollback(self):
        """
        Restaura estado antes da transação SQL
        """
        self._conn.rollback()
         
    def __enter__(self):
        self.create_table()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print('finishing connection')
        self._conn.close()
        if exc_type is not None:
            print(f'exc_type : {exc_type}')
        if exc_tb is not None:
            print(f'exc_tb   : {exc_tb}')