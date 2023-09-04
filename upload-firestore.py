import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

with open("articles.json", "r") as file:
    articles_data = json.load(file)

db = firestore.client()

batch_size = 80 

batch = db.batch()
for index, article in enumerate(articles_data, start=1):
    article_ref = db.collection("articles").document()
    batch.set(article_ref, article)
    
    if index % batch_size == 0 or index == len(articles_data):
        batch.commit()
        batch = db.batch()  

print("Data berhasil upload ke Firestore")