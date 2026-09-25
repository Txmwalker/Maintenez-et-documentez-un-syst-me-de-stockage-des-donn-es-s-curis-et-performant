import os
import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Alignement avec les variables du fichier .env
URI = os.getenv("MONGO_APP_URI")
DB_NAME = os.getenv("APP_DB_NAME", "medical_db")

@pytest.fixture(scope="module")
def db_collection():
    """
    Prépare la connexion à la base de données pour les tests.
    Utilise une variable d'environnement pour cacher les identifiants.
    """
    if not URI:
        raise ValueError("La variable d'environnement MONGO_APP_URI est introuvable.")
        
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    yield client[DB_NAME]['patients']
    client.close()

def test_migration_success(db_collection):
    """Vérifie que les documents ont bien été insérés dans la collection."""
    count = db_collection.count_documents({})
    assert count > 0, "Échec du test : La collection est vide !"
    assert count == 54966, f"Échec du test : Le nombre de documents attendu est 54966, mais on a trouvé {count}."

def test_data_typing(db_collection):
    """Vérifie que le nettoyage des données a bien formaté l'âge en nombre entier."""
    sample = db_collection.find_one()
    assert sample is not None, "Échec du test : Aucun document trouvé pour le test de typage."
    assert isinstance(sample['Age'], int), "Échec du test : L'âge n'est pas formaté en entier (int)."
    assert isinstance(sample['Billing Amount'], float), "Échec du test : Le montant n'est pas formaté en float."

def test_document_fields(db_collection):
    """Vérifie la présence des champs obligatoires suite au nettoyage."""
    sample = db_collection.find_one()
    assert sample is not None, "Échec du test : Aucun document trouvé."
    assert "Name" in sample, "Le champ 'Name' est manquant."
    assert "Medical Condition" in sample, "Le champ 'Medical Condition' est manquant."

def test_no_strict_duplicates_in_db(db_collection):
    """Demande à MongoDB de vérifier l'absence de doublons stricts sur une combinaison de champs clés."""
    pipeline = [
        {"$group": {
            "_id": {"Name": "\(Name", "Age": "\)Age", "Billing": "$Billing Amount"}, 
            "count": {"$sum": 1}
        }},
        {"\(match": {"count": {"\)gt": 1}}}
    ]
    duplicates = list(db_collection.aggregate(pipeline))
    assert len(duplicates) == 0, "Des documents dupliqués ont été trouvés en base de données."

def test_app_user_auth_restriction():
    """Vérifie que l'utilisateur de l'application n'a pas de privilèges root (Authentification)."""
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    
    # L'utilisateur applicatif ne doit pas pouvoir lire les collections de la base système 'admin'
    with pytest.raises(OperationFailure):
        client.admin.list_collection_names()
        
    client.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])