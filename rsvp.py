from flask import Flask, render_template, redirect, url_for, request,make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import socket
import os
import json
import logging

app = Flask(__name__)

#LINK=os.environ.get('LINK', "www.cloudyuga.guru")
#TEXT1=os.environ.get('TEXT1', "CloudYuga")
#TEXT2=os.environ.get('TEXT2', "Garage RSVP")
LOGO=os.environ.get('LOGO', "https://raw.githubusercontent.com/cloudyuga/rsvpapp/master/static/cloudyuga.png")
COMPANY=os.environ.get('COMPANY', "DBHA Technology. Ltd.")

MONGODB_HOST=os.environ.get('MONGODB_HOST', 'localhost')
client = MongoClient(MONGODB_HOST, 27017)
db = client.rsvpdata

class RSVP(object):
    """Simple Model class for RSVP"""
    def __init__(self, name, email, _id=None):
        self.name = name
        self.email = email
        self._id = _id

    def dict(self):
        _id = str(self._id)
        return {
            "_id": _id,
            "name": self.name,
            "email": self.email,
            "links": {
                "self": "{}api/rsvps/{}".format(request.url_root, _id)
            }
        }

    def delete(self):
        db.rsvpdata.find_one_and_delete({"_id": self._id})

    @staticmethod
    def find_all():
        return [RSVP(**doc) for doc in db.rsvpdata.find()]

    @staticmethod
    def find_one(id):
        doc = db.rsvpdata.find_one({"_id": ObjectId(id)})
        return doc and RSVP(doc['name'], doc['email'], doc['_id'])

    @staticmethod
    def new(name, email):
        doc = {"name": name, "email": email}
        result = db.rsvpdata.insert_one(doc)
        return RSVP(name, email, result.inserted_id)

@app.route('/')
def rsvp():
    _items = db.rsvpdata.find()
    items = [item for item in _items]
    count = len(items)
    hostname = socket.gethostname()
    return render_template('profile.html', counter=count, hostname=hostname,\
                           items=items, LOGO=LOGO,\
                           COMPANY=COMPANY)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {'name': request.form['name'], 'email': request.form['email']}
    db.rsvpdata.insert_one(item_doc)

    # 로그 생성
    userName = request.form.get('name')
    logger = logging.getLogger()
    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)
    # log 출력 형식
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    # log를 파일에 출력
    file_handler = logging.FileHandler('/var/log/rsvp-web/rsvp.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f'{userName} 님 등록되었습니다')

    return redirect(url_for('rsvp'))

@app.route('/api/rsvps', methods=['GET', 'POST'])
def api_rsvps():
    if request.method == 'GET':
        docs = [rsvp.dict() for rsvp in RSVP.find_all()]
        return json.dumps(docs, indent=True)
    else:
        try:
            doc = json.loads(request.data)
        except ValueError:
            return '{"error": "expecting JSON payload"}', 400

        if 'name' not in doc:
            return '{"error": "name field is missing"}', 400
        if 'email' not in doc:
            return '{"error": "email field is missing"}', 400

        rsvp = RSVP.new(name=doc['name'], email=doc['email'])
        return json.dumps(rsvp.dict(), indent=True)

@app.route('/api/rsvps/<id>', methods=['GET', 'DELETE'])
def api_rsvp(id):
    rsvp = RSVP.find_one(id)
    if not rsvp:
        return json.dumps({"error": "not found"}), 404

    if request.method == 'GET':
        return json.dumps(rsvp.dict(), indent=True)
    elif request.method == 'DELETE':
        rsvp.delete()
        return json.dumps({"deleted": "true"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)