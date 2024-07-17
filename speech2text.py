#!/usr/bin/python

import os
from pydub import AudioSegment
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json

with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

IBM_API_KEY = conf_File['User']['Giacomo']['IBM_S2T']['token']
IBM_URL = conf_File['User']['Giacomo']['IBM_S2T']['url']

authenticator = IAMAuthenticator(IBM_API_KEY)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(IBM_URL)

# Funzione per la trascrizione del file audio
def transcribe_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        result = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/wav',
            model='it-IT_BroadbandModel'
        ).get_result()
    
    try:
        # Concatena tutti i segmenti di trascrizione
        transcript = ""
        for res in result['results']:
            transcript += res['alternatives'][0]['transcript'] + " "
        
        return transcript.strip()
    except IndexError:
        return "Non sono riuscito a capire il messaggio."
