from google.cloud import firestore
import yaml
import os

file = os.path.dirname(os.path.abspath(__file__))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{file}/../static/json/assemblr-28d528f0fb82.json"
os.environ["FIREBASE_CONFIG"] = f"{file}/../static/json/firebase_config.json"

db = firestore.Client()

batch = db.batch()

collection_ref = db.collection('languages')

language_file = f"{file}/../static/yaml/languages.yml"
with open(language_file, 'r') as stream:
    languages = yaml.safe_load(stream)

for key, val in languages.items():
    if val['type'] == 'programming' and 'color' in val:
        doc_ref = collection_ref.document(key)
        batch.set(doc_ref, {'color': val['color']})

batch.commit()