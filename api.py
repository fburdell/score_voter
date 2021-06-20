from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import psycopg2 as pg
import sqlalchemy as sa
import math

params = {
    'phoenix_keys' : '/home/frank/Insync/frank@pahdcc.com/Google Drive/frank/hdcc_frank/program/data/projects/fenv/keys.txt',
    'pg_host':'localhost',
    'pg_user':'frank',
    'pg_password':'frank',
    'pg_port':5432
}


class Phoenix:

    def __init__(self):
        self.keys = '/home/frank/Insync/frank@pahdcc.com/Google Drive/cycle_20/program/data/projects/fenv/keys.txt'
        self.client = bigquery.Client.from_service_account_json(self.keys)
        self.credentials = service_account.Credentials.from_service_account_file(self.keys)
        self.downloads_path = r"C:\Users\Owner\Downloads"

    def exe(self, query):
        return self.client.query(query)

    def get_result(self, query):
        return self.exe(query).result()

    def get_df(self, query):
        return self.get_result(query).to_dataframe()

    def send_df(self, df, destination_table, project_id, if_exists): 
        df.to_gbq(destination_table=destination_table,
            project_id=project_id,
            if_exists=if_exists,
            credentials=self.credentials)

    def iter_phoenix(self, table): 
        i = self.client.list_rows(table) 
        page = next(i.pages)
        rows = list(page)
        total = i.total_rows
        token = i.next_page_token

class iPhoenix(Phoenix): 
    """
    provides iterator class for stepping through large bq table into local memory
    """

    def __init__(self, table, chunksize): 
        Phoenix.__init__(self) 
        self.table = table
        self.chunksize = chunksize
        self.c = self.client.list_rows(
                table=self.table,
                page_size=chunksize)
        self.cols = [x.name for x in self.c.schema]

    def __iter__(self): 
        for row in self.c: 
            yield row

    def i_send(self, df, destination_table, project_id, if_exists, chunksize, progress_bar): 
        df.to_gbq(destination_table=destination_table,
            project_id=project_id,
            if_exists=if_exists,
            credentials=self.credentials, 
            chunksize=chunksize,
            progress_bar=progress_bar)

class Postgres:

    def __init__(self, database):
        self.database = database
        self.user = 'frank'
        self.password = 'frank'
        self.host = 'localhost'
        self.port = 5432

    def pg_con(self): 
        return pg.connect(database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port)
    
    def sa_con(self): 
        return sa.create_engine(f'postgresql://{self.user}:{self.password}@localhost/{self.database}').connect()





