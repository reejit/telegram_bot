import requests
import json

import librosa
import pyogg
import wave
import numpy as np

import io
import sys






    
class WIT_sph2txt:

    def __init__(self, wit_token='', verbose=False):
        self.wit_token = wit_token
        self.verbose   = verbose

        self.default_ogg_module = 'pyogg'
        
        return None


    def opusfile_to_text(self, file_name='cristobal.ogg'):
        WIT_API_URL = 'https://api.wit.ai/speech'
        
        headers_d = {'Authorization': 'Bearer ' + self.wit_token,
                     'Content-type':  'audio/wav'}

        audio_data = self.opus2wav(file_name)
        
        r = requests.post(WIT_API_URL, data=audio_data, headers=headers_d)
        content = r.content

        if self.verbose:
            print(' - wit response content:', content)
            
        if type(content) is bytes:
            content = content.decode(errors='ignore')
        
        resp_d = json.loads( content )
        
        if self.verbose:
            print(r.status_code, r.reason)

        if r.status_code == 200:
            text = resp_d['_text']
        else:
            print(' - ERROR, opusfile_to_text: ', resp_d, file=sys.stderr )
            text = ''

        if self.verbose:
            print(' - opusfile_to_text: Texto leido: "{}"'.format(text))
            
        return text
    

    def ath_test(self, q='hello'):
        WIT_API_URL = 'https://api.wit.ai/message?v=20170307&q={}'.format(q)
        headers_d = {'Authorization': 'Bearer ' + self.wit_token}
        r = requests.get(WIT_API_URL, headers=headers_d)
        resp_d = json.loads( r.content )
        
        if self.verbose:
            print(r.status_code, r.reason)

        if r.status_code == 200:
            resp = resp_d
        else:
            print(' - ERROR, ogg_to_text: ', resp_d, file=sys.stderr )
            resp = None

        return resp


    def read_opus(self, file_name):
        max_try = 2

        y_int, sr = None, None
        while max_try > 0:
            try:
                if self.default_ogg_module == 'librosa':
                    if self.verbose:
                        print(' - read_opus, Leyendo archivo:', file_name, 'con librosa')
                        
                    sample_rate = 16000
                    y, sr = librosa.load(file_name, sr=sample_rate)
                    
                    # Cortamos los archivos mayores a 19 s
                    max_len = 19 * sr
                    if y.shape[0] > max_len:
                        y = y[:max_len]
                        
                    y_int = (np.iinfo(np.int16).max / np.abs(y).max() * y).astype(np.int16)
                    
                elif self.default_ogg_module == 'pyogg':
                    if self.verbose:
                        print(' - read_opus, Leyendo archivo:', file_name, 'pyogg')
                        
                    of = pyogg.OpusFile(file_name)
                    sr = of.frequency
                    b_len = of.buffer_length//2
                    y_int = np.array( of.buffer[:b_len], dtype=np.int16)

                    # Cortamos los archivos mayores a 19 s
                    max_len = 19 * sr
                    if y.shape[0] > max_len:
                        y_int = y_int[:max_len]
                        
                    sr = sr//3
                    y_int = y_int[::3].copy()

                max_try = 0

            except:
                print(' - ERROR, opus2wav: module failure {}, changing default module'.format(self.default_ogg_module), file=sys.stderr)
                
                if self.default_ogg_module == 'pyogg':
                    self.default_ogg_module = 'librosa'
                else:
                    self.default_ogg_module = 'pyogg'

                max_try += 0

        if y_int is None:
            raise Exception(' - ERROR, read_opus: unable to read opus ogg.')            
            
        return y_int, sr
        
        
    def opus2wav(self, file_name):
        """ La funci´on lee los archivos ogg de Telegram, los convierte a wav, y los devuelve como cadena de bytes"""

        
        y_int, sr = self.read_opus(file_name)

        # buffer para almacenar el binario del archivo wav
        f_buffer = io.BytesIO()

        # Convertimos temporalmente a un archivo wav para mandar a la api
        waveFile = wave.open(f_buffer, 'wb')
        waveFile.setnchannels(1)
        waveFile.setsampwidth(2)  # el 2 viene de "pyaudio.PyAudio().get_sample_size(pyaudio.paInt16 )"
        waveFile.setframerate(sr)
        waveFile.writeframes(y_int)
        
    ##    waveFile.close()
    ##    read_audio2(file_name2, verbose=verbose)
        f_buffer.flush()
        f_buffer.seek(0)


        audio_data = f_buffer.read()
        
        if self.verbose:
            print('Tamaño de archivo:', len(audio_data) // 1024, 'kBytes')

        return audio_data




if __name__ == '__main__':

    from aux_f import *
    tokens_d = read_keys_d(file_name='./api_keys.json')

    
    file_name = r'./logs/843157648/843157648_00003.ogg'

    wit  = WIT_sph2txt(wit_token=tokens_d['WIT_SERVER_TOKEN'], verbose=True)
    text = wit.opusfile_to_text(file_name)

    print(text)






    

