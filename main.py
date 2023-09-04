from fastapi import FastAPI, Path, File, UploadFile
from pydantic import BaseModel
from fuzzywuzzy import fuzz
import requests
import json
import re   
import uvicorn

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello, This is Mediscan!"}

#package endpoint
class DrugInfo(BaseModel):
    namaObat: str
    gambarObat : str
    resepDokter: str
    golonganObat: str
    deskripsi: str
    komposisi: str
    kemasan: str
    manfaat: str
    dosis: str
    penyajian: str
    efekSamping: str
    nomorIzin: str

with open("obat.json", "r") as file:
    data = json.load(file)

@app.get("/data")
def get_data():
    return {"success": True, "message": "Data obat berhasil diambil", "data": data}

@app.get("/detail-obat/{medicine_name}")
def detail_obat(medicine_name: str = Path(..., title="Medicine Name")):
    medicine_name = re.sub("-", " ", medicine_name)
    
    matching_drugs = [obat for obat in data if medicine_name.lower() in obat["namaObat"].lower()]
    if matching_drugs:
        return {"success": True, "message": "Data obat ditemukan", "data": matching_drugs}
    else:
        return {"success": False, "message": "Data obat tidak ditemukan"}
    
@app.get("/search")
def q_obat(q: str):
    # Split the query into words and take the first word
    query_first_word = q.split()[0].lower()

    matching_drugs = [
        obat for obat in data if fuzz.partial_ratio(
            query_first_word, obat["namaObat"].split()[0].lower()) >= 70
    ]
    return {"success": True, "message": "Hasil Search", "data": matching_drugs}

@app.post("/receipt")
async def predict_medicines(file: UploadFile):
    # Upload the image to the deployed ML model
    files = {'file': (file.filename, file.file)}
    response = requests.post('', files=files)

    if response.status_code == 200:
        predictions = response.json()
        return {"predictions": predictions} 
    else:
        return {"error": "Gagal membuat prediksi"}

class ArticleInfo(BaseModel):
    judul: str
    gambar: str
    artikel: str
    referensi: str

# Load articles data from a JSON file
with open("articles.json", "r") as file:
    articles_data = json.load(file)
    
@app.get("/all-articles")
async def get_all_articles():
    return {"dataArtikel": articles_data}

@app.get("/articles/{article_id}")
async def get_article(article_id: int):
    if 0 <= article_id < len(articles_data):
        return articles_data[article_id]
    else:
        return {"message": "Artikel tidak ditemukan"}

def fetch_medicine_details(medicine_name):
    for medicine in data:
        if medicine_name.lower() in medicine["namaObat"].lower():
            medicine["resepDokter"] = medicine["resepDokter"] or ""
            return medicine
    return None

@app.get("/ocr/{medicine_name}", response_model=DrugInfo)
def get_medicine_details(medicine_name: str):
    matching_medicines = fetch_medicine_details(medicine_name)

    if matching_medicines:

        return matching_medicines
    else:

        return {"error": f"Obat '{medicine_name}' tidak ditemukan"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
