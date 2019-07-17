from mitsuku import PandoraBot

import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


bots_box = {}


def get_bot(chat_id, force_start=False):
    if force_start or (chat_id not in bots_box.keys()):
        mk_bot = PandoraBot()
        bots_box[chat_id]  = mk_bot
    else:
        mk_bot = bots_box[chat_id]
        
    return mk_bot
    

def start(bot, update):

    chat_id = update.message.chat_id

    print(' Empezando chat con:', chat_id)

    get_bot(chat_id, force_start=True)
    bot.send_message(chat_id=update.message.chat_id, text="Empezando nuevo chat con Mitsuku, say something in ENGLISH!!!! :")
    return None


def echo(bot, update):
    global update2

    update2 = update
    
    msg = update.message.text
    chat_id = update.message.chat_id

    mk_bot = get_bot(chat_id, force_start=False)

    resp = mk_bot.ask(msg)
    
    print('msg[{}]: {} '.format(chat_id, msg))
    print('mk_rep:     {}'.format(resp))
    print()
    
    bot.send_message(chat_id=chat_id, text=resp)

    return None


def voice_echo(bot, update):
    global update3

    update3 = update
    
    voice_msg = update.message.voice
    chat_id = update.message.chat_id


    mk_bot = get_bot(chat_id, force_start=False)

    
    if True:
        file_obj = voice_msg.get_file()
        file_arr = file_obj.download_as_bytearray()

        ogg_filename = 'aux_{}.ogg'.format(chat_id)
        with open(ogg_filename, 'wb') as f:
            f.write( file_arr )
            
        msg = wit.opusfile_to_text(ogg_filename)


    resp = mk_bot.ask(msg)
    
    text = 'wit_echo: {}\n\n{}'.format(msg, resp)
    bot.send_message(chat_id=chat_id, text=text)

    return None


if __name__ == '__main__':
    from aux_f import *
    from wit import WIT_sph2txt

    
    tokens_d = read_keys_d(file_name='./api_keys.json')
    wit = WIT_sph2txt(wit_token=tokens_d['WIT_CLIENT_TOKEN'], verbose=False)
    
    updater = Updater(token=tokens_d['BigSergioBot'],
                      request_kwargs={'proxy_url': 'http://proxy.cab.cnea.gov.ar:3128/'})

    dispatcher = updater.dispatcher


    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    text_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(text_handler)
    
    voice_handler = MessageHandler(Filters.voice, voice_echo)
    dispatcher.add_handler(voice_handler)
    


    updater.start_polling()

    print('running bot ...')
