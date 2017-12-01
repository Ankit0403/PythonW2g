from flask import Flask
from flask import json
from flask import request
import os
import gensim
import logging
import time
from gensim.models import Word2Vec
from elasticsearch import Elasticsearch
from dateutil.parser import parse
import sys
MODEL_PATH='.\Domain'
logfile=MODEL_PATH+"\\restApi_w2v.log"
logging.basicConfig(filename=logfile,level=logging.DEBUG)
path = MODEL_PATH
app = Flask(__name__)
es = Elasticsearch('http://med3d.eastus.cloudapp.azure.com:9220')
@app.route("/similar", methods=["GET"])
def getSimilar():
    text = request.args.get("word")
    text=text.lower()
    domains = request.args.get("domains")
    domains=domains.lower()
    ModelFileName = '#any_' + domains
    print(text)
    print(domains)
    print(ModelFileName)
    if os.path.exists(MODEL_PATH + '\\' + ModelFileName + '_w2v.model'):
        modelWiki_w2v = gensim.models.Word2Vec.load(os.path.join(MODEL_PATH, ModelFileName + '_w2v.model'), mmap='r')
        print('Model files are present')
        try:
            synonyms = modelWiki_w2v.most_similar(text, topn=10)
            logging.info('Most similar word for '+domains+ '-' +text+ 'are : %s', synonyms)
            return json.dumps(synonyms)
        except:
            logging.info('No similar word found in domain %s for the word : %s' ,domains,text)
            return 'No similar word found in domain '+domains+' for the word : '+text
    else:
        logging.info('No model found for the domain %s' , domains)
        return '404- No model found for the domain ' + domains

@app.route("/logsimilarity", methods=["GET"])
def logsimilarity():
    try:
        args = request.args
        print (args)  # For debugging
        term = request.args.get("term")
        domain = request.args.get("domain")
        userid = request.args.get("userid")
        context = request.args.get("context")
        querysimilarity=request.args.get("querysimilarity")
        localtime = parse(time.asctime(time.localtime(time.time())))
        data = {
            'querydate' : localtime,
            'queryterm': term,
            'querydomain': domain,
            'userid': userid,
            'context':context,
            'querysimilarity' :querysimilarity
        }
        res = es.index(index="logsimilarity", doc_type='w2v', body=data)
        return json.dumps({ "querydomain": domain, "queryterm": term,"userid": userid, "context": context,"querysimilarity": querysimilarity}, sort_keys=False)
    except:
        return "failed"

@app.errorhandler(404)
def page_not_found(e):
    return json.jsonify(error=404, text=str(e)), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
