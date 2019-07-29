import re
from db_handler import DB_Handler
from sentence_parser import Sentence_parser
from corpus import *


# States for the bot
class States:
    ON_START         = 0
    ON_PERSONAL_INFO = 1
    ON_ACTION_SELECT = 2
    ON_HELP          = 3
    ON_REC           = 4
    ON_STATS         = 5
    ON_DELETE        = 6
    ON_END           = 7
    
    ON_CANCEL        = 10

    
    def __init__(self):
        self.internal_state = self.ON_START
        self.i_step         = 0

    def set_state(self, state, i_state=0):
        self.internal_state = state
        self.i_step         = i_state
        return None
        
    def get_state(self):
        return self.internal_state, self.i_step

    def step(self):
        self.i_step += 1
        return None

    def step_back(self):
        self.i_step -= 1
        if self.i_step < 0:
            self.i_step = 0
            
        return None
        

    def __str__(self):
        return "<State[{}][{}]>".format(self.internal_state, self.i_step)

    def __repr__(self):
        return self.__str__()
        




class MrExerciseBot():
    """ Main class for the bot """
    
    def __init__(self, user_id='12354', dbs_path='./dbs', verbose=True):
        """ Starts a new bot
            db_name: usually will be an chat_id
            """

        self.user_id  = str(user_id)
        self.dbs_path = dbs_path
        self.verbose  = verbose

        # Starts a new handler for the DB corresponding to this user.
        self.dbh = DB_Handler(dbs_path=self.dbs_path,
                              db_name=self.user_id,
                              verbose=self.verbose)

        # Instantiate Sentence_parser object for natural lenguaje processing
        self.sp = Sentence_parser()
        
        # Object States, for acount Bot States
        self.state = States()

        # Load the private data if were found
        self.load_personal_info()
        
        return None

    
    def load_personal_info(self):
        """ Loads personal info from user's db
            """
        
        priv_data = self.dbh.get_private_data()
        
        if priv_data is None:
            if self.verbose:
                print(" - MrExerciseBot, load_personal_info: there isn't any private data for the user_id: {} yet.".format(self.user_id))

            self.personal_info_d = {'name':'',
                                    'default_sport':'',
                                    'last_state':States.ON_START,
                                    'complete':False}
        else:
            self.personal_info_d = priv_data
            self.state.set_state(self.personal_info_d['last_state'])

            
        return None


    def save_personal_info(self):
        """ Saves prersonal info to user's db
            """
        # Remembering the state not the step
        self.personal_info_d['last_state'] = self.state.get_state()[0]

        # Saveing the data
        self.dbh.set_private_data( self.personal_info_d )
        
        return None


    def on_start(self):
        to_resp_v = []

        self.state.set_state( States.ON_START )
        to_resp_v += self.query()
        
        return to_resp_v

        
    def exec_personal_info(self, q=''):
        """ Executes steps for personal info retrival """

        to_resp_v = []
        
        # Get the state and the i_step
        state, i_step = self.state.get_state()

        if i_step == 0:
            to_resp_v += corpus_d['personal_info'][i_step]
            self.state.step()
            
        elif i_step == 1:
            name = self.sp.find_name(q)
            if name:
                self.personal_info_d['name'] = name
                to_resp_v += corpus_d['personal_info'][i_step]
                self.state.step()
            else:
                to_resp_v += corpus_d['personal_info_err'][i_step]
                
            
        elif i_step == 2:
            default_sport = self.sp.find_exercise(q)

            if default_sport:
                self.personal_info_d['default_sport'] = default_sport
                to_resp_v += corpus_d['personal_info'][i_step]

                self.state.step()
            else:
                to_resp_v += corpus_d['personal_info_err'][i_step]


        elif i_step == 3:
            resp = self.sp.yes_no_question(q)
            
            if resp == True:
                # Personal info will be saved
                self.personal_info_d['complete'] = True
                self.save_personal_info()
                
                to_resp_v += corpus_d['personal_info'][i_step]

                self.state.set_state( States.ON_ACTION_SELECT )
                to_resp_v += self.query()
                
            elif resp == False:
                to_resp_v += corpus_d['personal_info_err'][i_step]
                self.state.step_back()
                
            else:
                to_resp_v += corpus_d['personal_info_err'][i_step+1]
            
                
        return to_resp_v


    def exec_rec(self, q=''):
        """ Executes steps for record a training"""

        to_resp_v = []
        
        # Get the state and the i_step
        state, i_step = self.state.get_state()

        if i_step == 0:
            to_resp_v += corpus_d['record'][i_step]
            self.to_record_d = {'date':None, 'activity':self.personal_info_d['default_sport'], 'time':0, 'act_mode':1}
            self.state.step()
            
        elif i_step == 1:
            use_default = self.sp.yes_no_question(q)
            
            if use_default == True:
                to_resp_v += corpus_d['record'][i_step+1]
                self.state.step()
                self.state.step()
                
            elif use_default == False:
                to_resp_v += corpus_d['record'][i_step]
                self.state.step()

            else:
                to_resp_v += corpus_d['record_err'][i_step]
                
            
        elif i_step == 2:
            sport = self.sp.find_exercise(q)

            if sport:
                self.to_record_d['activity'] = sport
                to_resp_v += corpus_d['record'][i_step]
                self.state.step()
            else:
                to_resp_v += corpus_d['record_err'][i_step]

        elif i_step == 3:
            self.to_record_d['time'] = int(q)
            to_resp_v += corpus_d['record'][i_step]
            self.state.step()
            
        elif i_step == 4:
            self.to_record_d['act_mode'] = int(q)
            to_resp_v += corpus_d['record'][i_step]

            self.dbh.add_record( **self.to_record_d)
            
            self.state.set_state( States.ON_ACTION_SELECT )

            # Personal info will be saved
            self.save_personal_info()
            to_resp_v += self.query()
        
        return to_resp_v

    
    def exec_action_select(self, q=''):
        """ Executes action select dialog. """

        to_resp_v = []
        
        # Get the state and the i_step
        state, i_step = self.state.get_state()

        if i_step == 0:
            to_resp_v += corpus_d['actions'][0]
            self.state.step()
        
        elif i_step == 1:
            if self.sp.find_v(q, action_select_keys_d['personal_info']):
                self.state.set_state(States.ON_PERSONAL_INFO)
                to_resp_v += self.query(q)
                
            elif self.sp.find_v(q, action_select_keys_d['help']):
                self.state.set_state(States.ON_HELP)
                to_resp_v += self.query(q)

            elif self.sp.find_v(q, action_select_keys_d['record']):
                self.state.set_state(States.ON_REC)
                to_resp_v += self.query(q)

            elif self.sp.find_v(q, action_select_keys_d['stats']):
                self.state.set_state(States.ON_STATS)
                to_resp_v += self.query(q)

            elif self.sp.find_v(q, action_select_keys_d['delete']):
                self.state.set_state(States.ON_DELETE)
                to_resp_v += self.query(q)
            else:
                to_resp_v += corpus_d['actions'][-1]
                        
        return to_resp_v
    

    def exec_delete(self, q=''):
        """ Deletes all dbs for the user """

        to_resp_v = []
        
        # Get the state and the i_step
        state, i_step = self.state.get_state()

        if i_step == 0:
            to_resp_v += corpus_d['delete'][i_step]
            self.state.step()

        elif i_step == 1:
            do_delete = self.sp.yes_no_question(q)
            
            if do_delete == True:
                to_resp_v += corpus_d['delete'][i_step]
                self.state.set_state(States.ON_END)
                self.dbh.delete_db()
                to_resp_v += self.query(q)
                
            elif do_delete == False:
                to_resp_v += corpus_d['delete'][i_step+1]
                self.state.set_state(States.ON_ACTION_SELECT)
                to_resp_v += self.query(q)

            else:
                to_resp_v += corpus_d['delete_err'][i_step]

        return to_resp_v
    

    def exec_help(self, q):
        to_resp_v = []

        to_resp_v += corpus_d['help'][0]
        self.state.set_state(States.ON_ACTION_SELECT)

        to_resp_v += self.query(q)
        
        return to_resp_v


    def exec_stats(self, q):
        to_resp_v = []

        stats_v = self.dbh.get_stats()

        if len(stats_v) == 0:
            to_resp_v += corpus_d['stats'][-1]
        else:
            to_resp_v += corpus_d['stats'][0]
            for stats_d in stats_v:
                to_resp_v.append( corpus_d['stats'][1][0].format(**stats_d) )


        self.state.set_state(States.ON_ACTION_SELECT)

        to_resp_v += self.query(q)
        
        return to_resp_v


    def exec_cancel(self, q):
        to_resp_v = []
        
        if self.personal_info_d['complete']:
            to_resp_v += corpus_d['cancel'][0]
            self.state.set_state(States.ON_ACTION_SELECT)
        else:
            to_resp_v += corpus_d['cancel_err'][0]
            self.state.set_state(States.ON_PERSONAL_INFO)
            
        to_resp_v += self.query()

        return to_resp_v


    def exec_end(self, q):
        to_resp_v = []

        to_resp_v += corpus_d['end'][0]

        return to_resp_v
        
    
    def query(self, q=''):
        to_resp_v = []

        # First of all let's find if there is a cancel state
        if self.sp.find_v(q, action_select_keys_d['cancel']):
            self.state.set_state(States.ON_CANCEL)


        state, i_step = self.state.get_state()
        if state == States.ON_START:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_START.')

            self.load_personal_info()
            if self.personal_info_d['complete']:
                to_resp_v += corpus_d['on_start'][0]
            else:
                to_resp_v += corpus_d['on_start'][0]
                to_resp_v += corpus_d['on_start'][1]

            if self.personal_info_d['complete']:
                self.state.set_state(States.ON_ACTION_SELECT)
            else:
                self.state.set_state(States.ON_PERSONAL_INFO)

            to_resp_v += self.query(q)
                
        elif state == States.ON_PERSONAL_INFO:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_PERSONAL_INFO.')

            to_resp_v += self.exec_personal_info(q)

        elif state == States.ON_ACTION_SELECT:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_ACTION_SELECT.')
                
            to_resp_v += self.exec_action_select(q)

        elif state == States.ON_HELP:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_HELP.')
                
            to_resp_v += self.exec_help(q)

        elif state == States.ON_REC:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_REC.')

            to_resp_v += self.exec_rec(q)

        elif state == States.ON_STATS:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_STATS.')

            to_resp_v += self.exec_stats(q)

        elif state == States.ON_DELETE:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_DELETE.')

            to_resp_v += self.exec_delete(q)
            
        elif state == States.ON_CANCEL:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_CANCEL.')

            to_resp_v += self.exec_cancel(q)

        elif state == States.ON_END:
            if self.verbose:
                print(' - MrExerciseBot, query: Selecting ON_END.')

            to_resp_v += self.exec_end(q)    
            
        else:
            to_resp_v += ['STATE NOT IMPLEMENTED: '+str(self.state)]

        # Reemplaze all the private data in the response
        for i in range(len(to_resp_v)):
            to_resp_v[i] = to_resp_v[i].format(**self.personal_info_d)

##        # last_state variable needs to be saved
##        self.save_personal_info()
        
        return to_resp_v

        
        
if __name__ == '__main__':
    bot = MrExerciseBot(verbose=False)
    
    def resp(r_v):
        for r in r_v:
            print(' BOT_msg >>>', r)
            print()

    
    resp(bot.on_start())

    while 1:
        q = input(' USR_msg >>> ')
        r_v = bot.query(q)
        resp(r_v)










    
    




