import os
import pytest
from pymongo import MongoClient

@pytest.fixture
def db_collection():
    """
    Prépare la connexion à la base de données pour les tests.
    Utilise une variable d'environnement pour cacher les identifiants.
    """
    # On récupère l'URI de connexion depuis l'environnement
    mongo_uri = os.getenv("TEST_MONGO_URI")
    
    # Sécurité : on bloque le test si la variable n'est pas fournie
    if not mongo_uri:
        raise ValueError("La variable d'environnement TEST_MONGO_URI est introuvable. Veuillez la définir avant de lancer pytest.")
        
    client = MongoClient(mongo_uri)
    return client['medical_db']['patients']

def test_migration_success(db_collection):
    """Vérifie que les documents ont bien été insérés dans la collection."""
    count = db_collection.count_documents({})
    assert count > 0, "Échec du test : La collection est vide !"
    assert count == 54966, f"Échec du test : Le nombre de documents attendu est 54966, mais on a trouvé {count}."

def test_data_typing(db_collection):
    """Vérifie que le nettoyage des données a bien formaté l'âge en nombre entier."""
    sample = db_collection.find_one()
    
    # On s'assure d'abord qu'un document a bien été trouvé
    assert sample is not None, "Échec du test : Aucun document trouvé pour le test de typage."
    
    # On vérifie le type de la donnée
    assert isinstance(sample['Age'], int), "Échec du test : L'âge n'est pas formaté en entier (int)."

if __name__ == "__main__":
    pytest.main(["-v", __file__])