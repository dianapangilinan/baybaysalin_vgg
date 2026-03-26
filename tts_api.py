import requests

url = 'http://api.voicerss.org/'

class TTSHandler:
    def __init__(self, apikey):
        self.apikey = apikey

    def convert_to_speech(self, text):
        payload = {'key': str(self.apikey),
                   'hl': 'en-us',
                   'src': str(text)}

        response = requests.get(url, params=payload)

        return response.url