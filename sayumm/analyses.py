from alchemyapi_python.alchemyapi import AlchemyAPI
import json

alchemyapi = AlchemyAPI()

def tone_analyze(text_in):

    response = alchemyapi.sentiment("text", text_in)
    print(response)
    return response