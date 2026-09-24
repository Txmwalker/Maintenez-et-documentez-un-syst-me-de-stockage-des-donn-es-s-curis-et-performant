import logging
import os
from typing import List, Dict, Any

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Configuration des journaux d'exécution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_data(file_path: str) -> List[Dict[str, Any]]:
    """Charge, nettoie et formate les données médicales selon les standards Data Quality."""
    logging.info(f"Lecture du fichier : {file_path}")
    df = pd.read_csv(file_path)
    
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
    """Insère les données nettoyées dans MongoDB."""
    try:
        # LECTURE DE LA VARIABLE D'ENVIRONNEMENT ICI
        # Si la variable n'est pas trouvée, le script plantera proprement au lieu de se connecter au mauvais endroit
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("La variable d'environnement MONGO_URI est introuvable.")
            
        client = MongoClient(mongo_uri)
        
        db = client['medical_db']
        collection = db['patients']
        
        # Réinitialisation pour éviter les doublons en phase de test
        collection.drop()  
        
        # Insertion en masse
        collection.insert_many(data)
        logging.info(f"Migration réussie : {len(data)} documents insérés.")
        
        # Création des index (Point de vigilance)
        collection.create_index("Name")
        collection.create_index("Medical Condition")
        logging.info("Index de performance créés avec succès.")
        
    except PyMongoError as e:
        logging.error(f"Erreur lors de l'interaction avec MongoDB : {e}")
    except ValueError as e:
        logging.error(f"Erreur de configuration : {e}")

if __name__ == "__main__":
    dataset_file = "/app/data/healthcare_dataset.csv"
    
    # Exécution du pipeline complet
    clean_data = process_data(dataset_file)
    migrate_to_mongo(clean_data)