from flask import Flask, request, abort, jsonify
import analyses

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Built at PennApps XII 2015! Upload an m4a or amr to /analyze.'

@app.route('/analyze', methods=['POST'])
def analyzeVoice():
    voiceRaw = request.files.get('voiceRaw', None)
    print(voiceRaw.__dict__)
    # accept only filetypes that bleh
    if voiceRaw is None or not voiceRaw.filename.endswith(('.m4a', '.amr')):
        return 'Invalid filetype or no file uploaded', 400
    
    # we've determined that the file is of the correct format. Now, analyze!
    results = {}
    results['tone'] = analyses.tone_analyze()


    # return results
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



