#from requests_futures.sessions import FuturesSession
from flask import Flask, request, abort, jsonify
#from concurrent.futures import ThreadPoolExecutor
#from signal import signal, SIGPIPE, SIG_DFL

import analyses, config, time, requests, json

from alchemyapi_python.alchemyapi import AlchemyAPI

#signal(SIGPIPE,SIG_DFL) 
app = Flask(__name__)
alchemyapi = AlchemyAPI()
s = {}
#session = FuturesSession(executor=ThreadPoolExecutor(max_workers=4))


@app.route('/')
def hello_world():
    return 'Built at PennApps XII 2015! Upload an m4a or amr or wav to /analyze.'


@app.route('/analyze', methods=['POST'])
def analyzeVoice():
    results = {}

    voiceRaw = request.files.get('voiceRaw', None)
    
    # accept only filetypes that bleh
    #if voiceRaw is None or not voiceRaw.filename.endswith(('.m4a', '.amr', '.wav')):
    #return 'Invalid filetype or no file uploaded: Supported suffixes: .m4a .amr .wav', 400
    
    # convert speech from .amr to .wav format
    #print(voiceRaw.__dict__)

    # convert speech to text
    # Audio files larger than 4MB are required to be sent in streaming mode (chunked transfer-encoding). 
    # Streaming audio size limit is 100 MB.
    audio = open('./yeah.wav', 'rb')

    print('##################')
    print('# start session  #')
    print('##################')
    try:
        r1 = requests.post(config.speech2text.get('url'), 
            auth=(config.speech2text.get('username'), config.speech2text.get('password'))
        )
        print(r1.text)
    except(IOError):
        return 'Server error: %r' % IOError, 500
    # successfully retrieved response from IBM
    try:
        first_hit = json.loads(r1._content)
    except(TypeError):
        print(TypeError.__dict__)
        return 'Server error while decoding json response from Watson while uploading audio', 500

    recognize_url = first_hit.get('recognize')
    observe_url = first_hit.get('observe_result')
    recognize_cookie_session = {'SESSIONID': r1.cookies.get_dict()['SESSIONID']}
    print(recognize_url)
    print(recognize_cookie_session)
    print('##################')
    print('# ask to recog   #')
    print('##################')
    try:
        r2 = requests.post(recognize_url,
        headers={'Content-Type': 'audio/wav'}, 
        cookies=r1.cookies.get_dict(),
        auth=(config.speech2text.get('username'), config.speech2text.get('password')),
        data=audio,
        params={'timestamps':True, 'word_confidence':True})
    except(IOError):
        return 'Server error: %r' % IOError, 500

    print(r2.text)

    voiceText = 'hi there and would you like something to drink'

    # sentiment analysis
    
    print('##################')
    print('sentiment analysis')
    print('##################')
    results['sentiment_analysis'] = analyses.tone_analyze(voiceText)
    
    print('##################')
    print('# results        #')
    print('##################')
    print(results)
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


def _request_transcription(text_to_transcribe):
    response = alchemyapi.sentiment("text", text_in)

