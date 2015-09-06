from flask import Flask, request, abort, jsonify

import analyses, config, time, requests, json, wave, os ,requests

from alchemyapi_python.alchemyapi import AlchemyAPI

app = Flask(__name__)
alchemyapi = AlchemyAPI()
s = {}

@app.route('/')
def hello_world():
    return 'Built at PennApps XII 2015! Upload a .wav file to /analyze.'

def databaseEntry(jsonText):
    data = {
        'subject': 'Database',
        'predicate' : 'get_entry',
        'object': jsonText
    }

    url = "http://localhost:64210/api/v1/write"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps([data]), headers=headers)
    print r

#@app.route('/latest', methods=['G'])
@app.route('/latest')
def getLatest():
    url = "http://localhost:64210/api/v1/query/gremlin"
    r = requests.post(url, data="g.V(\"Database\").Out().GetLimit(1)")
    print r.text
    print r.json
    return r.text


@app.route('/analyze', methods=['POST'])
def analyzeVoice():
    results = {}

    voiceRaw = request.files.get('voiceRaw', None)
    voicePanel = request.form.get('panels')
    print(voicePanel)
    try:
        panel_data = json.loads(voicePanel)
        results['panel_data'] = panel_data
    except(TypeError):
       print(TypeError.__dict__)
       return 'Server error while decoding json response from Android app (for panel data)', 500



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
    print('#  CONCATENATION #')
    print('##################\n')

    transcript = []
    is_talking = []
    voice_results = voice_textified['results']
    for alternatives_obj in voice_results:
        for timestamps_obj in alternatives_obj['alternatives']:
            if (alternatives_obj['alternatives']) is not None:
                for timestamp in timestamps_obj['timestamps']:
                    is_talking.append((timestamp[0], timestamp[1], timestamp[2]))  # [ (word, startTime, endTime) ]
            if(timestamps_obj.get('word_confidence') is not None):
                for word_confidence in timestamps_obj.get('word_confidence'):
                        transcript.append((word_confidence[0], word_confidence[1]))  # [ (word, confidence) ]]

    results['transcript'] = transcript 
    results['word_times'] = is_talking 

    words_count = len(transcript)
    ums_count = len([x[0] for x in transcript if x[0] == '%HESITATION' or x[0] == 'nnnnn'])
    last_word_end_time_in_sec = is_talking[len(is_talking)-1][2]
    first_word_start_time_in_sec = is_talking[0][1]
    speech_length_in_min = (last_word_end_time_in_sec - first_word_start_time_in_sec)/60.0

    print('##################')
    print('#  DO SOME MATH  #')
    print('##################\n')
    wpm = words_count/(speech_length_in_min)
    upm = ums_count/(speech_length_in_min)
    results['wpm'] = wpm
    results['upm'] = upm
    results['words_total'] = words_count
    results['ums_total'] = ums_count
    print('Length of transcript in minutes: %f' % speech_length_in_min)
    results['duration'] = speech_length_in_min
    print('WPM: %f        UPM: %f' % (wpm, upm))
    print('Words: %d      Ums: %d' % (words_count, ums_count))

    # sentiment analysis
    print('##################')
    print('sentiment analysis')
    print('##################\n')
    results['sentiment'] = analyses.tone_analyze(voice_textified)
    
    print('\n\n##################')
    print('# results        #')
    print('##################\n')
    print(results)
    databaseEntry(json.dumps(results))
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


def _request_transcription(text_to_transcribe):
    response = alchemyapi.sentiment("text", text_in)
