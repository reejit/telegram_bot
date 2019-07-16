import requests
import random

class PandoraBot():
    """ Clase para interactuar con bots de la pagina https://pandorabots.com"""
    
    def __init__(self, botid='e397abf70e345a0e'):
        self.botcust2 = self.gen_rnd() #'b1a3b932de49faeb'
        self.bot_id   = botid


        self.url = 'https://kakko.pandorabots.com/pandora/talk?botid={}&skin=mobile'.format(self.bot_id)
        return None

    
    def gen_rnd(self, seed=None, bites=8):
        random.seed(seed)
        hex_str = hex(random.randint(1+int((bites-1)*'ff', 16), int(bites*'ff', 16)))[2:] 
        return hex_str

        
    def parse_resp(self, text, verbose=False):
        chat_v = []
        for t in text.split('<B>You:</B> ')[1:]:
            a, b = t.split('<br> <B>Mitsuku:</B> ')

            a = a.strip()
            b = b.split('<br> <br>')[0]

            if '</P>' in b:
##                print('stripping!!!')
                b = b.split('</P>')[-1].strip()
                
            chat_v.append( (a,b) )

            if verbose:
                print('you:', a)
                print('mitsuko:', b)
                print()

        return chat_v


    def ask(self, text):
        r = requests.post(self.url, data={'botcust2':self.botcust2, 'message':text})
        self.chat_v = self.parse_resp( r.text )
        if len(self.chat_v) > 0:
            ret_text = self.chat_v[0][-1]
        else:
            ret_text = "sorry, I don't have an anwer"
        
        return ret_text

        
    def get_chat(self, verbose=True):
        if verbose:
            for a, b in self.chat_v:
                print('you:    ', a)
                print('mitsuko:', b)
                print()
            
        return self.chat_v


if __name__ == '__main__':

    mk = PandoraBot()
    for i in range(10):
        text = input(' >>> ')
        print(' >>>', mk.ask(text))

    



    
    
