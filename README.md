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
* Fichier `.env` correctement renseigné à la racine (voir ci-dessous).

## Configuration du fichier `.env`

Les identifiants ne sont jamais versionnés. Un modèle sans secrets, `.env.example`, liste toutes les variables nécessaires :

```bash
# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Ouvrez ensuite `.env` et remplacez chaque valeur `change_me_...` par un mot de passe fort :

| Variable | Rôle |
|---|---|
| `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` | Compte administrateur (root) MongoDB |
| `APP_DB_USER` / `APP_DB_PASSWORD` | Compte applicatif (`readWrite` sur la base) utilisé par les scripts |
| `APP_DB_NAME` | Nom de la base (`healthcare_db`) |
| `READ_DB_USER` / `READ_DB_PASSWORD` | Compte analyste en lecture seule |
| `MONGO_APP_URI` | URI utilisée dans le conteneur (hôte `mongodb`, port `27017`) |
| `MONGO_LOCAL_URI` | URI utilisée depuis la machine hôte (hôte `localhost`, port `27018`) |

Dans `MONGO_APP_URI` et `MONGO_LOCAL_URI`, l'utilisateur, le mot de passe et la base doivent correspondre à `APP_DB_USER`, `APP_DB_PASSWORD` et `APP_DB_NAME`.

> Les comptes sont créés uniquement au **premier** démarrage du volume MongoDB. Si vous modifiez `.env` après coup, réinitialisez le volume avec `docker-compose down -v`.

Le fichier `.env` est exclu du dépôt (`.gitignore`) et de l'image Docker (`.dockerignore`).


## 1. Déploiement et Exécution Automatisée

L'ensemble de l'infrastructure (base de données et script Python) est conteneurisé. Aucune installation locale de Python n'est requise.

```bash
# Lance MongoDB
docker-compose up -d mongodb

# Construit l'environnement Python et exécute la migration et les tests en une commande
docker-compose run --rm migration_and_tests
```

## 2. Relance manuelle de la migration et des tests

Si l'infrastructure (le conteneur mongodb_healthcare) est déjà en cours de fonctionnement et que vous souhaitez rejouer les scripts localement :
Activez votre environnement virtuel Python local.

Les variables sont chargées depuis `.env`, puis `MONGO_APP_URI` est redirigée vers `MONGO_LOCAL_URI` (accès depuis l'hôte). Aucun mot de passe n'est saisi en clair dans le terminal.

```bash
# Linux / macOS : chargement du .env
set -a; source .env; set +a
export MONGO_APP_URI="$MONGO_LOCAL_URI"

# Lancez le script de migration :
python migration.py
```

```powershell
# Windows (PowerShell) : chargement du .env
Get-Content .env | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object { $k, $v = $_ -split '=', 2; Set-Item "env:$k" $v }
$env:MONGO_APP_URI = $env:MONGO_LOCAL_URI

# Lancez le script de migration :
python migration.py
```

## 3. Tests et Validation

Les tests utilisent la même variable `MONGO_APP_URI` (compte applicatif) que la migration. Après avoir chargé le `.env` comme à l'étape 2 :

```bash
pytest test_migration.py -v
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

Rôle Applicatif (Read/Write) : Utilisateur `healthcare_user` (variable `APP_DB_USER`) **déjà créé** au lancement par `init-mongo.js`, avec le seul privilège `readWrite` sur la base `healthcare_db`. C'est ce compte, et non le compte root, qu'utilisent les scripts de migration, de test et de CRUD via `MONGO_APP_URI`, conformément au principe du moindre privilège.

Évolution Cloud (AWS) : Lors d'un passage en production sur AWS (DocumentDB ou ECS), ce même découpage des rôles serait conservé, les secrets étant alors stockés dans AWS Secrets Manager plutôt que dans un fichier `.env`.

Rôle Analyste (Read-Only) : Utilisateur `healthcare_reader` créé au lancement, possédant uniquement le privilège `read` sur la base `healthcare_db`. Ce compte est dédié aux outils de Business Intelligence (BI) et d'audit pour consulter les données sans risque de modification.

## 7. Opération CRUD

```bash
#Commande lancement du script d'exemple d'opérations CRUD
docker-compose run --rm migration_and_tests python crud_demo.py
```
