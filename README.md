# Maintenez-et-documentez-un-syst-me-de-stockage-des-donn-es-s-curis-et-performant
# Healthcare Data Migration Pipeline

## Description
Ce projet implémente un pipeline de données permettant le nettoyage, la transformation et la migration sécurisée d'un set de données médicales (CSV) vers une base de données NoSQL conteneurisée. 

## Stack Technique
* **Langage :** Python 3
* **Base de données :** MongoDB (via Docker)
* **Packages clés :** pandas, pymongo, pytest

## Prérequis
* Docker Desktop installé et en cours d'exécution
* Fichier `.env` correctement renseigné à la racine.


## 1. Déploiement et Exécution Automatisée

L'ensemble de l'infrastructure (base de données et script Python) est conteneurisé. Aucune installation locale de Python n'est requise.

```bash
# Lance MongoDB, construit l'environnement Python et exécute la migration en une commande
docker-compose up --build
```

## 2. Relance manuelle de la migration et des tests

Si l'infrastructure (le conteneur mongodb_healthcare) est déjà en cours de fonctionnement et que vous souhaitez rejouer les scripts localement :
Activez votre environnement virtuel Python local.

```bash
#Définissez la chaîne de connexion (qui simule les identifiants présents dans le .env pour un accès depuis votre hôte) :
export MONGO_APP_URI="mongodb://healthcare_user:AppSecretPassword_456@localhost:27017/healthcare_db"
export APP_DB_NAME="healthcare_db"

#Lancez le script de migration :
python Script/migration.py

Exécutez les contrôles qualité :

pytest Script/test_migration.py
```

## 3. Tests et Validation

```bash
#Sous Linux / macOS, commande :
TEST_MONGO_URI="mongodb://admin:supersecretpassword@localhost:27018/?authSource=admin" pytest test_migration.py

#Sous Windows (PowerShell), commandes :
$env:TEST_MONGO_URI="mongodb://admin:supersecretpassword@localhost:27018/?authSource=admin"
pytest test_migration.py
```

## 4. Maintenance de l'Infrastructure

```bash
# Mettre la base de données en pause (conserve les données)
docker-compose down

# Détruire le conteneur et purger totalement le volume (réinitialisation à zéro)
docker-compose down -v
```

## 5. Schéma de la Base de Données (MongoDB)
Bien que MongoDB soit orienté document (NoSQL) et "schema-less", les données ont été typées et structurées de manière rigoureuse lors de la migration. Voici le schéma (Data Contract) d'un document type de la collection patients :

Name : String (Standardisé : Title Case)

Age : Integer (Typé dynamiquement lors de la migration)

Gender : String (Catégories : Male, Female, Other)

Blood Type : String

Medical Condition : String (Indexé pour la recherche)

Date of Admission : Date (Format ISO 8601)

Discharge Date : Date (Format ISO 8601)

Billing Amount : Double (Conserve les montants négatifs pour intégrité comptable)

Index créés :
Pour répondre aux enjeux de scalabilité, des index ont été créés sur Name et Medical Condition afin d'accélérer les requêtes récurrentes du client.

## 6. Sécurité et Authentification
La base de données est sécurisée dès l'initialisation du conteneur via des variables d'environnement.

Mode d'authentification : SCRAM-SHA-256 (Standard MongoDB).

Rôle Administrateur (Root) : Utilisateur admin créé au lancement via MONGO_INITDB_ROOT_USERNAME. Il possède les droits globaux sur le cluster.

Évolution Cloud (AWS) : Pour un futur passage en production sur AWS (DocumentDB ou ECS), un rôle avec le privilège restrictif readWrite limité exclusivement à la base medical_db devra être créé pour le script applicatif, respectant ainsi le principe du moindre privilège.
