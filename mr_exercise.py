import re
from dbs_handler import DB_Handler

corpus_d = {'on_start':
"""Welcome to MrExerciseBot.
MrExerciseBot is here to help you record your daily exercise rutine.
MrExerciseBot can understand natural lenguaje, even voice messeges.

To start you must provide some information about you.""",
            }
                          

def States():
    ON_START      = 0
    PERSONAL_INFO = 1

    
    def __init__(self):
        self.internal_state = -1
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
        
    

class MrExerciseBot():
    """ Main class for the bot """
    
    def __init__(self, user_id='12354', dbs_path='./dbs', verbose=True):
        """ Starts a new bot
            db_name: usually will be an chat_id
            """

        self.user_id = user_id
        self.dbs_path = dbs_path
        self.verbose = verbose

        # Starts a new handler for the DB corresponding to this user.
        self.dbh = DB_Handler(dbs_path=self.dbs_path,
                              db_name=self.user_id,
                              verbose=self.verbose)

        # Object States, for acount Bot States
        self.state = States()
        self.load_priv_data()
        
        if self.priv_data is None:
            # There is not private data about the user,
            # The bot must go to States.PERSONAL_INFO
            self.state.set_state(States.PERSONAL_INFO)
        else:
            # Return to the last state left by the user
            self.state.set_state(self.priv_data['state'])
            
        
        return None

    
    def load_priv_data(self):
        """ Loads private data from user's db
            """
        
        self.priv_data = self.dbh.get_private_data()
        
        if self.priv_data is None:
            if self.verbose:
                print(" - MrExerciseBot, load_priv_data: there isn't any private data for the user_id: {} yet.".format(self.user_id))

        return self.priv_data


    def save_priv_data(self):
        """ Saves the private data to user's db
            """
        self.dbh.set_private_data( self.priv_data )
        
        return None
    
    def retrieve_personal_info(self, q=''):
        self.state = States.PERSONAL_INFO
        if q == '':
            pass
        return None
        
        
    def on_start(self):
        to_resp_v = []
        to_resp_v.append( corpus_d['on_start'] )

        self.state = States.ON_START
        return 

        
        
    def query(self, q):
        pass

        
        
if __name__ == '__main__':
    bot = MrExerciseBot()
    

    



    
    
