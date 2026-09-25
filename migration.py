import logging
import os
import sys
from typing import List, Dict, Any

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Configuration des journaux d'exécution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_data(file_path: str) -> List[Dict[str, Any]]:
    """Charge, nettoie et formate les données médicales selon les standards Data Quality."""
    logging.info(f"Lecture du fichier : {file_path}")
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logging.error(f"Erreur : Le fichier {file_path} est introuvable.")
        sys.exit(1)
    
    # 1. Nettoyage de base : Suppression des valeurs nulles et des doublons stricts
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    
    # 2. Typage strict des champs pour assurer l'intégrité dans MongoDB
    df['Age'] = df['Age'].astype(int)
    df['Billing Amount'] = df['Billing Amount'].astype(float)
    
    # Typage des dates (demande spécifique pour les requêtes temporelles)
    if 'Date of Admission' in df.columns and 'Discharge Date' in df.columns:
        df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
        df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    
    # 3. Standardisation textuelle : Casse et espaces invisibles
    df['Name'] = df['Name'].str.strip().str.title()
    if 'Medical Condition' in df.columns:
        df['Medical Condition'] = df['Medical Condition'].str.strip()
    
    return df.to_dict(orient='records')

def migrate_to_mongo(data: List[Dict[str, Any]]) -> None:
    """Insère les données nettoyées dans MongoDB via une collection temporaire (Staging)."""
    try:
        # Alignement avec les variables du fichier .env
        mongo_uri = os.getenv("MONGO_APP_URI")
        db_name = os.getenv("APP_DB_NAME", "medical_db")
        
        if not mongo_uri:
            raise ValueError("La variable d'environnement MONGO_APP_URI est introuvable.")
            
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        if data:
            # 1. Préparation de la collection temporaire (staging)
            temp_collection_name = 'patients_temp'
            temp_collection = db[temp_collection_name]
            temp_collection.drop() # Nettoyage de sécurité en cas d'ancien résidu
            
            # 2. Insertion en masse dans l'espace isolé
            temp_collection.insert_many(data, ordered=False)
            logging.info(f"Données sécurisées dans l'espace temporaire : {len(data)} documents.")
            
            # 3. Bascule atomique : remplace 'patients' par la table temporaire instantanément
            temp_collection.rename('patients', dropTarget=True)
            logging.info("Migration réussie et bascule terminée sans interruption.")
        
        # 4. Création/Mise à jour des index sur la collection finale
        collection = db['patients']
        collection.create_index("Name")
        collection.create_index("Medical Condition")
        logging.info("Index de performance créés avec succès.")
        
    except PyMongoError as e:
        logging.error(f"Échec critique lors de l'interaction avec MongoDB : {e}")
        sys.exit(1) # Arrêt explicite
    except ValueError as e:
        logging.error(f"Erreur de configuration : {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Rendu dynamique pour fonctionner en local (VS Code) ou dans Docker (/app)
    base_dir = os.path.dirname(__file__)
    dataset_file = os.path.join(base_dir, "data", "healthcare_dataset.csv")
    
    # Exécution du pipeline complet
    clean_data = process_data(dataset_file)
    migrate_to_mongo(clean_data)