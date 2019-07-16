import requests
import json

##import librosa
import pyogg
import wave
import numpy as np

import io
import sys


##def read_audio2(file_name, verbose=True):
##    if verbose:
##        print('Leyendo archivo de audio:', file_name)
##        
##    with open(file_name, 'rb') as f:
##        audio_data = f.read()
##
##    return audio_data


##def read_audio(file_name, verbose=True):
##    if verbose:
##        print('Leyendo archivo de audio usando librosa:', file_name)
##
##    sample_rate = 16000
##    y, sr = librosa.load(file_name, sr=sample_rate)
##    y_int = (np.iinfo(np.int16).max / np.abs(y).max() * y).astype(np.int16)
##
####    file_name2 = file_name+'.wav'
##
##    f_buffer = io.BytesIO()
##    
##    waveFile = wave.open(f_buffer, 'wb')
##    waveFile.setnchannels(1)
##    waveFile.setsampwidth(2)  # el 2 viene de "pyaudio.PyAudio().get_sample_size(pyaudio.paInt16 )"
##    waveFile.setframerate(sr)
##    waveFile.writeframes(y_int)
##    
####    waveFile.close()
####    read_audio2(file_name2, verbose=verbose)
##    f_buffer.flush()
##    f_buffer.seek(0)
##    
##    
##    return f_buffer.read()


def read_opus(file_name, verbose=True):
    if verbose:
        print(' - read_opus, Leyendo archivo de read_opus usando pyogg.OpusFile:', file_name)

    of = pyogg.OpusFile(file_name)
    sr = of.frequency
    b_len = of.buffer_length//2
    y_int = np.array( of.buffer[:b_len], dtype=np.int16)

    sr = sr//3
    y_int = y_int[::3].copy()
    
##    file_name2 = file_name+'.wav'

    f_buffer = io.BytesIO()
    
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
    
    if verbose:
        print('Tamaño de archivo:', len(audio_data) // 1024, 'kBytes')

    return audio_data



    
class WIT_sph2txt:

    def __init__(self, wit_token='', verbose=False):
        self.wit_token = wit_token
        self.verbose   = verbose
        
        return None

    def opusfile_to_text(self, file_name='cristobal.ogg'):
        WIT_API_URL = 'https://api.wit.ai/speech'
        
        headers_d = {'Authorization': 'Bearer ' + self.wit_token,
                     'Content-type':  'audio/wav'}

        audio_data = read_opus(file_name, verbose=self.verbose)
        
        r = requests.post(WIT_API_URL, data=audio_data, headers=headers_d)
        resp_d = json.loads( r.content )
        
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


        
if __name__ == '__main__':

    from aux_f import *
    tokens_d = read_keys_d(file_name='./api_keys.json')
    file_name = r'./sergio.ogg'

    wit = WIT_sph2txt(wit_token=tokens_d['WIT_CLIENT_TOKEN'], verbose=False)
    text = wit.opusfile_to_text(file_name)

    print(text)

