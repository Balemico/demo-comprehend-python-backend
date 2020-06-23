import json
import boto3
import PyPDF2
import werkzeug
from flask_restful import reqparse, Resource, Api
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

import time

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['CORS_HEADERS'] = 'Content-Type'

parser = reqparse.RequestParser()


class Welcome(Resource):
    def get(self):
        return {'status': 'ok'}


class Upload(Resource):
    def post(self):
        now = datetime.now()
        timestamp = str(datetime.timestamp(now))
        parser.add_argument(
            'file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        file = args['file']
        # filename = werkzeug.utils.secure_filename(timestamp+'_'+file.filename)
        # file.save("./uploads/" + filename)

        text = ''
        pdfReader = PyPDF2.PdfFileReader(file)
        for page in pdfReader.pages:
            text = text + " " + page.extractText()

        # print(text)

        comprehend = boto3.client(
            service_name='comprehend', region_name='eu-central-1')

        print('Calling DetectDominantLanguage')
        detectedLang = comprehend.detect_dominant_language(Text=text)
        print("End of DetectDominantLanguage\n")
        lang = detectedLang['Languages'][0]['LanguageCode']

        print('Lang: '+lang)

        print('Calling DetectSentiment with text')
        detectedSentiment = comprehend.detect_sentiment(
            Text=text, LanguageCode=lang)
        print()
        print('End of DetectSentiment\n')
        sentiment = detectedSentiment['Sentiment']

        print('Sentiment: ' + sentiment)

        print('Calling DetectEntities')
        detectedEntities = comprehend.detect_entities(
            Text=text, LanguageCode=lang)
        print('End of DetectEntities\n')
        entities = detectedEntities["Entities"]

        print('Entities: ')
        print(entities)

        result = {}
        result["language"] = lang
        result["sentiment"] = sentiment
        result["entities"] = entities
        return result


class Language(Resource):

    def post(self):
        parser.add_argument('text', type=str)
        args = parser.parse_args()

        comprehend = boto3.client(
            service_name='comprehend', region_name='eu-central-1')

        text = "It is raining today in Seattle"
        if args["text"] != "":
            text = args["text"]

        print('Calling DetectDominantLanguage')
        result = comprehend.detect_dominant_language(Text=text)
        print("End of DetectDominantLanguage\n")
        return result['Languages'][0]['LanguageCode']


class Sentiment(Resource):

    def post(self):
        parser.add_argument('text', type=str)
        args = parser.parse_args()

        comprehend = boto3.client(
            service_name='comprehend', region_name='eu-central-1')

        text = "It is raining today in Seattle"
        if args["text"] != "":
            text = args["text"]

        print('Calling DetectSentiment with text '+text)
        result = comprehend.detect_sentiment(Text=text, LanguageCode='en')
        print()
        print('End of DetectSentiment\n')
        return result['Sentiment']


class Entities(Resource):

    def post(self):
        parser.add_argument('text', type=str)
        args = parser.parse_args()

        comprehend = boto3.client(
            service_name='comprehend', region_name='eu-central-1')

        text = "It is raining today in Seattle"
        if args["text"] != "":
            text = args["text"]

        print('Calling DetectEntities')
        result = comprehend.detect_entities(Text=text, LanguageCode='en')
        print('End of DetectEntities\n')
        return result["Entities"]


api.add_resource(Welcome, '/api/')
api.add_resource(Upload, '/api/upload/')
api.add_resource(Language, '/api/language/')
api.add_resource(Sentiment, '/api/sentiment/')
api.add_resource(Entities, '/api/entities/')

if __name__ == '__main__':
    app.run(debug=True)
