import os
from pymongo import MongoClient

# Récupération de l'URI depuis les variables d'environnement.
# S'il n'y a pas de variable d'environnement (ex: exécution en local), 
# on utilise l'URL de connexion du compte applicatif par défaut.
DEFAULT_URI = "mongodb://healthcare_user:AppSecretPassword_456@localhost:27018/healthcare_db"
URI = os.getenv("MONGO_APP_URI", DEFAULT_URI)
DB_NAME = os.getenv("APP_DB_NAME", "healthcare_db")

def main():
    print("\n=== Démonstration des opérations CRUD (Create, Read, Update, Delete) ===")
    
    # --- CONNEXION ---
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        collection = db['patients']
        print(f"Connecté avec succès à la base de données : {DB_NAME}\n")
    except Exception as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        return

    # ---------------------------------------------------------
    # 1. CREATE - Ajout d'un nouveau document
    # ---------------------------------------------------------
    print("--- 1. CREATE : Ajout d'un nouveau dossier patient ---")
    nouveau_patient = {
        "Name": "Jean Dupont",
        "Age": 45,
        "Gender": "Male",
        "Blood Type": "O+",
        "Medical Condition": "Hypertension",
        "Hospital": "Hôpital Central",
        "Insurance Provider": "Axa",
        "Billing Amount": 1500.50,
        "Admission Type": "Elective",
        "Test Results": "Inconclusive"
    }
    
    insert_result = collection.insert_one(nouveau_patient)
    patient_id = insert_result.inserted_id
    print(f"✅ Patient ajouté avec succès. L'ID généré est : {patient_id}\n")

    # ---------------------------------------------------------
    # 2. READ - Recherche d'un document spécifique
    # ---------------------------------------------------------
    print("--- 2. READ : Recherche du patient dans la base ---")
    patient_trouve = collection.find_one({"_id": patient_id})
    if patient_trouve:
        print(f"Dossier trouvé : {patient_trouve['Name']}, {patient_trouve['Age']} ans.")
        print(f"   Condition : {patient_trouve['Medical Condition']} | Facture : {patient_trouve['Billing Amount']}€\n")

    # ---------------------------------------------------------
    # 3. UPDATE - Modification d'un document
    # ---------------------------------------------------------
    print("--- 3. UPDATE : Mise à jour des résultats du patient ---")
    # Simulation : le patient a reçu ses résultats et la facture a augmenté
    update_query = {"_id": patient_id}
    new_values = {"$set": {"Test Results": "Normal", "Billing Amount": 1750.00}}
    
    collection.update_one(update_query, new_values)
    
    # Vérification en relisant la base
    patient_maj = collection.find_one({"_id": patient_id})
    print(f"Dossier mis à jour. Nouveaux résultats : {patient_maj['Test Results']} | Nouvelle facture : {patient_maj['Billing Amount']}€\n")

    # ---------------------------------------------------------
    # 4. DELETE - Suppression du document
    # ---------------------------------------------------------
    print("--- 4. DELETE : Suppression du dossier ---")
    # On supprime ce patient fictif pour garder notre base de données propre
    delete_result = collection.delete_one({"_id": patient_id})
    if delete_result.deleted_count == 1:
        print(f"Dossier de {patient_trouve['Name']} supprimé avec succès (Nettoyage post-démonstration).\n")
        
    print("=== Fin de la démonstration CRUD ===")
    client.close()

if __name__ == "__main__":
    main()