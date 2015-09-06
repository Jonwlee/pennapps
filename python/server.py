from flask import Flask, request, abort, jsonify

import analyses, config, time, requests, json, wave, os

from alchemyapi_python.alchemyapi import AlchemyAPI

app = Flask(__name__)
alchemyapi = AlchemyAPI()
s = {}


@app.route('/')
def hello_world():
    return 'Built at PennApps XII 2015! Upload a .wav file to /analyze.'


@app.route('/analyze', methods=['POST'])
def analyzeVoice():
    results = {}

    voiceRaw = request.files.get('voiceRaw', None)
    
    # accept only file types that we care about (???)
    if voiceRaw is None or not voiceRaw.filename.endswith(('.wav')):
        return 'Invalid filetype or no file uploaded: Supported suffixes: .m4a .amr .wav', 400

    # convert speech to text
    # Audio files larger than 4MB are required to be sent in streaming mode (chunked transfer-encoding). 
    # Streaming audio size limit is 100 MB.

    # voiceRaw = open('./yeah.wav', 'rb')  # for debugging

    print('##################')
    print('# start session  #')
    print('##################\n')
    try:
        r1 = requests.post(config.speech2text.get('url'), 
            auth=(config.speech2text.get('username'), config.speech2text.get('password'))
        )
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
    print('##################')
    print('# ask to recog   #')
    print('##################\n')
    try:
        r2 = requests.post(recognize_url,
        headers={'Content-Type': 'audio/wav'}, 
        cookies=r1.cookies.get_dict(),
        auth=(config.speech2text.get('username'), config.speech2text.get('password')),
        data=voiceRaw,
        params={'timestamps':True, 'word_confidence':True, 'continuous': True})
        voice_textified = json.loads(r2.text)
        print(voice_textified)
    except(IOError):
        return 'Server error: %r' % IOError, 500
    except(TypeError):
        return 'Server error while decoding json response from Watson while uploading audio: %r' % TypeError, 500

    print('##################')
    print('#  DO SOME MATH  #')
    print('##################\n')
    wpm = 0
    upm = 0

    print(wpm)



    # sentiment analysis
    print('##################')
    print('sentiment analysis')
    print('##################\n')
    results['sentiment_analysis'] = analyses.tone_analyze(voice_textified)
    
    print('\n\n##################')
    print('# results        #')
    print('##################\n')
    print(results)
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


def _request_transcription(text_to_transcribe):
    response = alchemyapi.sentiment("text", text_in)

