import os, sys
import time
import json
import logging


from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from mitsuku import PandoraBot as BotHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TelegramBot(Updater):
    def __init__(self, token='YourTelegramBotToken', proxy_url=None, t2s_obj=None, make_log=False, log_folder='./logs', verbose=True):
        """ Instancia un servidor para manejar bots a partir usando telegram.
            Cada chat id, tiene su propio bot del timpo Bot.
            La componente t2s_obj debe realizar la conversión de voz a texto. """
            
        # Diccionarios de para los bots, a cada bot se le asigna un ID definido por el chat_idsdds
        self.bots_box = {}

        # Conversor de voz a texto utilizado.
        self.t2s_obj  = t2s_obj
        
        # Si quiero que imprima por pantalla
        self.verbose  = verbose

        # Si quiero que deje un log
        self.make_log = make_log

        # Directorio para realizar el log
        self.log_folder = log_folder
        
        # Inicializo el módulo Updater con el token y el proxy si es necesario.
        if proxy_url is not None:
            super().__init__(token=token,
                             request_kwargs={'proxy_url': proxy_url})
        else:
            super().__init__(token=token)

        self.dispatcher = self.dispatcher
                             
        start_handler = CommandHandler('start', self.on_start)
        self.dispatcher.add_handler(start_handler)

        self.text_handler = MessageHandler(Filters.text, self.on_txt_msg)
        self.dispatcher.add_handler(self.text_handler)
        
        self.voice_handler = MessageHandler(Filters.voice, self.on_voice_msg)
        self.dispatcher.add_handler(self.voice_handler)
        
        return None


    def get_bot_by_chat_id(self, chat_id, force_start=False):
        if force_start or (chat_id not in self.bots_box.keys()):
            bot = BotHandler()
            self.bots_box[chat_id]  = bot
        else:
            bot = self.bots_box[chat_id]
            
        return bot


    def get_all_chat_ids(self):
        return list( self.bots_box.keys() )
    

    def on_start(self, bot, update):
        chat_id = update.message.chat_id

        print(' Empezando chat con:', chat_id)

        get_bot(chat_id, force_start=True)
        bot.send_message(chat_id=update.message.chat_id, text="Empezando nuevo chat con Mitsuku, say something in ENGLISH!!!! :")
        return None
    

    def voice2text(self, ogg_filename=''):
        max_retry = 2

        while max_retry > 0:
            try:
                msg = self.t2s_obj.opusfile_to_text(ogg_filename)
                max_retry = 0
            except Exception as e:
                print(' Hubo un error al analizar el archivo {}, tratando nuevamente !!!'.format(ogg_filename), file=sys.stderr)
                max_retry -= 1
                msg = ''
                
        return msg



    def get_save_dir(self, chat_id=12345):
        working_folder = os.path.join(self.log_folder, '{}'.format(chat_id))
        
        if not os.path.exists(working_folder):
            if not os.path.exists(self.log_folder):
                if self.verbose:
                    print(' - get_save_dir: Creating folder: "{}"'.format(self.log_folder) )
                os.mkdir(self.log_folder)
            
            if self.verbose:
                print(' - get_save_dir: Creating folder: "{}"'.format(working_folder) )
                
            os.mkdir(working_folder)

        return working_folder
        

    def save_voice_msg(self, chat_id, voice_msg):
        # Creamos directorio de salvado
        working_folder = self.get_save_dir(chat_id)

        file_obj = voice_msg.get_file()
        file_arr = file_obj.download_as_bytearray()

        
        file_idx = 0
        fname_found = False
        files_v = os.listdir(working_folder)
        while not fname_found:
            ogg_filename = '{}_{:05d}.ogg'.format(chat_id, file_idx)

            if not ogg_filename in files_v:
                fname_found = True

            file_idx += 1
                
        save_path = os.path.join(working_folder, ogg_filename)
        with open(save_path, 'wb') as f:
            f.write( file_arr )
            
        return save_path


    def save_log(self, chat_id, msg, resp):

        to_save = json.dumps([int(time.time()), chat_id, msg, resp])

        
        working_folder = self.get_save_dir(chat_id)
        log_file_path = os.path.join(working_folder, 'chat_log.txt')
        with open(log_file_path, 'a') as f:
            f.write(to_save + '\n')
                                            
        return None



    def on_txt_msg(self, tg_bot, update):
        msg = update.message.text
        chat_id = update.message.chat_id

        bot_brain = self.get_bot_by_chat_id(chat_id, force_start=False)

        resp = bot_brain.ask(msg)

        if self.verbose:
            print('msg[{}]: {} '.format(chat_id, msg))
            print('mk_rep:     {}'.format(resp))
            print()

        # Mando respuesta a través del telegram_bot
        tg_bot.send_message(chat_id=chat_id, text=resp)
        
        # Makeing or deleting log
        if self.make_log:
            self.save_log(chat_id, msg, resp)
            
        return None
    

    def on_voice_msg(self, tg_bot, update):
        voice_msg = update.message.voice
        chat_id   = update.message.chat_id

        bot_brain = self.get_bot_by_chat_id(chat_id, force_start=False)
        
        # Leemos y convertimos a texto el menzaje de voz    
        ogg_filename = self.save_voice_msg(chat_id, voice_msg)   
        msg = self.voice2text(ogg_filename)

        
        resp = bot_brain.ask(msg)
        
        text = 'wit_echo: {}\n\n{}'.format(msg, resp)

        if self.verbose:
            print('msg[{}]: {} '.format(chat_id, msg))
            print('mk_rep:     {}'.format(resp))
            print()
            
        # Mando respuesta a través del telegram_bot
        tg_bot.send_message(chat_id=chat_id, text=text)

        # Makeing or deleting log
        if self.make_log:
            self.save_log(chat_id, msg, resp)
        else:
            os.remove(ogg_filename)
        
        return None


    def connect(self):
        self.start_polling()
        if self.verbose:
            print('Telegram Bot is running ...')

        return None



if __name__ == '__main__':
    from aux_f import *
    from wit import WIT_sph2txt

    tokens_d = read_keys_d(file_name='./api_keys.json')

    if False:
        proxy_url = 'http://proxy.cab.cnea.gov.ar:3128/'
    else:
        proxy_url = None
    
    
    wit2 = WIT_sph2txt(wit_token=tokens_d['WIT_CLIENT_TOKEN'], verbose=False)

    tb = TelegramBot(token=tokens_d['BigSergioBot'], proxy_url=proxy_url, t2s_obj=wit2, make_log=True)
    tb.connect()

    

