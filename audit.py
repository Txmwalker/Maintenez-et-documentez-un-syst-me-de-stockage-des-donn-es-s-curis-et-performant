import argparse
import logging
import pandas as pd

# ==========================================
# CONFIGURATION ET CONSTANTES
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(message)s')

VALID_GENDERS = {'Male', 'Female', 'Other'}
VALID_BLOOD_TYPES = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
MIN_AGE = 0
MAX_AGE = 120

# ==========================================
# FONCTIONS D'AUDIT MÉTIER
# ==========================================
def audit_structure(df: pd.DataFrame) -> None:
    """Vérifie la qualité structurelle globale du dataset (doublons, valeurs nulles)."""
    logging.info("=== 1. DOUBLONS STRICTS ===")
    doublons = df.duplicated().sum()
    logging.info(f"Lignes 100% identiques sur toutes les colonnes : {doublons}")

    logging.info("\n=== 2. VALEURS MANQUANTES ===")
    valeurs_nulles = df.isnull().sum()
    if valeurs_nulles.any():
        logging.info(valeurs_nulles[valeurs_nulles > 0].to_string())
    else:
        logging.info("Aucune valeur manquante détectée.")

def audit_finance(df: pd.DataFrame) -> None:
    """Vérifie la cohérence des données de facturation."""
    if 'Billing Amount' not in df.columns:
        return
        
    logging.info("\n=== 3. INCOHÉRENCES FINANCIÈRES ===")
    valeurs_negatives = (df['Billing Amount'] < 0).sum()
    logging.info(f"Factures avec un montant négatif : {valeurs_negatives} ligne(s)")

def audit_biology_and_time(df: pd.DataFrame) -> None:
    """Vérifie la cohérence des données patient (âge, dates de séjour)."""
    logging.info("\n=== 4. INCOHÉRENCES BIOLOGIQUES ET TEMPORELLES ===")
    
    if 'Age' in df.columns:
        age_invalide = df[(df['Age'] < MIN_AGE) | (df['Age'] > MAX_AGE)]
        logging.info(f"Âge aberrant (inférieur à {MIN_AGE} ou supérieur à {MAX_AGE}) : {len(age_invalide)} ligne(s)")

    if 'Date of Admission' in df.columns and 'Discharge Date' in df.columns:
        admission = pd.to_datetime(df['Date of Admission'], errors='coerce')
        discharge = pd.to_datetime(df['Discharge Date'], errors='coerce')
        dates_incoherentes = (discharge < admission).sum()
        logging.info(f"Sorties antérieures à l'admission : {dates_incoherentes} ligne(s)")

def audit_categories(df: pd.DataFrame) -> None:
    """Vérifie la conformité des variables catégorielles standards."""
    logging.info("\n=== 5. VÉRIFICATION DES CATÉGORIES STANDARDS ===")
    
    if 'Gender' in df.columns:
        genre_inconnu = df[~df['Gender'].isin(VALID_GENDERS) & df['Gender'].notna()]
        logging.info(f"Genres non reconnus : {len(genre_inconnu)} ligne(s)")

    if 'Blood Type' in df.columns:
        groupe_inconnu = df[~df['Blood Type'].isin(VALID_BLOOD_TYPES) & df['Blood Type'].notna()]
        logging.info(f"Groupes sanguins non reconnus : {len(groupe_inconnu)} ligne(s)")

# ==========================================
# FONCTION PRINCIPALE
# ==========================================
def run_audit(file_path: str) -> None:
    """Orchestre le chargement et l'analyse détaillée du dataset."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logging.error(f"Fichier introuvable au chemin : {file_path}")
        return
    except pd.errors.EmptyDataError:
        logging.error(f"Le fichier est vide : {file_path}")
        return

    audit_structure(df)
    audit_finance(df)
    audit_biology_and_time(df)
    audit_categories(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit d'un dataset de santé (Healthcare Dataset).")
    parser.add_argument(
        "--file", 
        type=str, 
        default="data/healthcare_dataset.csv", 
        help="Chemin vers le fichier CSV à analyser"
    )
    args = parser.parse_args()
    
    run_audit(args.file)