from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Koala Backend")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle de données
class QuestionnaireData(BaseModel):
    organisation: str
    screenType: str
    saleSize: Optional[str] = None
    budget: Optional[str] = None
    equipement: Optional[str] = None
    screenSize: Optional[str] = None
    publicType: Optional[str] = None
    sector: Optional[str] = None
    nom: str
    email: EmailStr
    telephone: Optional[str] = None

# Variables d'environnement
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/koala-questionnaire")

@app.get("/")
def read_root():
    return {"message": "Koala Backend API - Version 1.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/questionnaire")
async def submit_questionnaire(data: QuestionnaireData):
    """
    Reçoit les données du questionnaire et les envoie à N8N
    """
    try:
        # Préparer les données pour N8N
        payload = {
            "organisation": data.organisation,
            "screenType": data.screenType,
            "saleSize": data.saleSize,
            "budget": data.budget,
            "equipement": data.equipement,
            "screenSize": data.screenSize,
            "publicType": data.publicType,
            "sector": data.sector,
            "nom": data.nom,
            "email": data.email,
            "telephone": data.telephone,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }

        print(f"Envoi vers N8N: {N8N_WEBHOOK_URL}")
        print(f"Données: {payload}")

        # Envoyer à N8N
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        print(f"Réponse N8N: {response.status_code}")

        if response.status_code not in [200, 201]:
            print(f"N8N Response: {response.text}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de l'envoi à N8N"
            )

        return {
            "status": "success",
            "message": "Questionnaire reçu et en cours de traitement",
            "data": payload
        }

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to N8N: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur de connexion au serveur de traitement"
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du traitement du questionnaire"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)