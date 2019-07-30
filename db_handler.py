import os, sys
import json
import numpy as np
import pandas as pd
import datetime

import time

class DB_Handler:

    def __init__(self, dbs_path='./dbs', db_name='12536', verbose=True):
        """ Creates an DB_Handler objet

            dbs_path: path to all dbs location
            db_name:  name for an specific db

            verbose: verbosity level
            """

        self.dbs_path = dbs_path
        self.db_name  = db_name
        self.db_path  = os.path.join(self.dbs_path, self.db_name)
        
        self.verbose = verbose

        # filename where the private data will be saved
        self.db_priv_filename = 'private.json'

        # filename where the all the records will be saved
        self.db_rec_filename  = 'records.csv'

        self.check_db_path()

        self.rec_df_columns = ['date', 'activity', 'time', 'act_mode']
        self.rec_df_types   = ['datetime64[ns]', 'str', 'float', 'int']
        
        return None

    def check_db_path(self):
        """ checks default folder structure.
            creates it if necessary.
            """

        
        
        if not os.path.exists(self.dbs_path):
            if self.verbose:
                print(' - DB_Handler.check_db_path: crating folder: {}'.format(self.dbs_path))
            os.mkdir(self.dbs_path)

        
        
        if not os.path.exists(self.db_path):
            if self.verbose:
                print(' - DB_Handler.check_db_path: crating folder: {}'.format(self.db_path))
            os.mkdir(self.db_path)
        


    def set_private_data(self, private_data_d={}):
        """ Saves provate data
            private_data_d: private data to be saved
            """

        self.check_db_path()
        
        priv_path = os.path.join(self.db_path, self.db_priv_filename)
        to_save = json.dumps(private_data_d)
        with open(priv_path, 'w') as f:
            if self.verbose:
                print(' - DB_Handler.set_private_data: writing file: {}'.format(priv_path))
            f.write(to_save)

        return None

    def get_private_data(self):
        """ returns private data
            """
        priv_path = os.path.join(self.db_path, self.db_priv_filename)
        
        if not os.path.exists( priv_path ):
            if self.verbose:
                print(' - DB_Handler.get_private_data: file not found: {}'.format(priv_path))
            return None

        with open(priv_path, 'r') as f:
            if self.verbose:
                print(' - DB_Handler.get_private_data: reading file: {}'.format(priv_path))
                
            fl = f.read()

        private_data_d = json.loads( fl )
        return private_data_d


    def get_rec_df(self):
        """ reads or creates and return an Pandas DataFrame as rec database
            """
        
        csv_path = os.path.join(self.db_path, self.db_rec_filename)
        if self.verbose:
            print(' - DB_Handler.get_rec_df: reading: {}'.format(csv_path))

        if os.path.exists(csv_path):
            rec_db = pd.read_csv(csv_path, index_col=0, parse_dates=[self.rec_df_columns[0]], dtype=dict(zip(self.rec_df_columns[1:], self.rec_df_types[1:])) )
        else:
            rec_db = pd.DataFrame()
            for col, c_type in zip(self.rec_df_columns, self.rec_df_types):
                rec_db[col] = pd.Series(dtype=c_type)
                
        return rec_db

            
    def set_rec_df(self, rec_db):
        """ reads or creates and return an Pandas DataFrame as rec database
            """
        
        self.check_db_path()
        csv_path = os.path.join(self.db_path, self.db_rec_filename)

        if self.verbose:
            print(' - DB_Handler.set_rec_df: saveing: {}'.format(csv_path))
            
        rec_db.to_csv(csv_path)
    
        return rec_db

    
    def add_record(self, date=None, activity='Unknown', time=0, act_mode=1):
        """ appends a record to rec_db.
            """
        time     = int(time)
        act_mode = int(act_mode)
        
        rec_df = self.get_rec_df()

        if date is None:
            date = pd.to_datetime( datetime.datetime.now() )
        else:
            date = pd.to_datetime( date )

        rec_df = rec_df.append({self.rec_df_columns[0]:     date,
                                self.rec_df_columns[1]: activity,
                                self.rec_df_columns[2]:     time,
                                self.rec_df_columns[3]: act_mode},
                               sort=False, ignore_index=True)
        if self.verbose:
            print(' - DB_Handler.add_record: after: \n {}'.format(rec_df))
            
        self.set_rec_df(rec_df)
        return rec_df
        

    def delete_db(self):
        """ deletes all db files.
            """

        if os.path.exists(self.db_path):
            for f in os.listdir(self.db_path):
                to_rm = os.path.join(self.db_path, f)
                if self.verbose:
                    print(' - DB_Handler.delete_db: deleting file: {}'.format(to_rm))
                os.remove(to_rm)
                
            if self.verbose:
                print(' - DB_Handler.delete_db: deleting folder: {}'.format(self.db_path))
            os.rmdir(self.db_path)

            # we must wait to the OS to prevent some errors
            time.sleep(0.1)
        return None

    def get_stats(self, last_n_days=5):
        """ return stats dict
            """
        stats_str = ''

        df = self.get_rec_df()
        df_f = df[df.date > datetime.datetime.now() - datetime.timedelta(days=last_n_days)]


        gs = df_f.groupby('activity')
        ret_v = []
        for k in gs.groups.keys():
            df_g = gs.get_group(k)
            #print(df_g)
            ret_v.append({'activity':str(k),
                          'mean_{}'.format( self.rec_df_columns[2]): df_g[self.rec_df_columns[2]].mean(),
                          'total_{}'.format(self.rec_df_columns[2]): df_g[self.rec_df_columns[2]].sum(),
                          'mean_{}'.format( self.rec_df_columns[3]): df_g[self.rec_df_columns[3]].sum(),
                          'n_records'                              : df_g[self.rec_df_columns[2]].count()} )
            
        return ret_v
        
if __name__ == '__main__':
    # Some tests
    
    dbh = DB_Handler(verbose=True)

    for i in range(1):
##        dbh.delete_db()
##        dbh.set_private_data({'nombre':'sergio'})
##        print(dbh.get_private_data())
##
##        dbh.set_private_data({'nombre':'sergioooo'})
##        print(dbh.get_private_data())

##        dbh.delete_db()
##        print(dbh.get_private_data())

##        dbh.delete_db()
        p = dbh.add_record()
        dbh.add_record('10-10-19')
        dbh.add_record('11-10-19')
        print(dbh.get_rec_df() )

        print(dbh.get_stats())


    
