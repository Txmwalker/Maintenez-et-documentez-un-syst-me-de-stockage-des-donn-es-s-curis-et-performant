db = db.getSiblingDB(process.env.APP_DB_NAME);

// 1. Création du compte applicatif (Lecture / Écriture)
db.createUser({
  user: process.env.APP_DB_USER,
  pwd: process.env.APP_DB_PASSWORD,
  roles: [{ role: "readWrite", db: process.env.APP_DB_NAME }]
});

// 2. Création du compte Lecture Seule
db.createUser({
  user: process.env.READ_DB_USER,
  pwd: process.env.READ_DB_PASSWORD,
  roles: [{ role: "read", db: process.env.APP_DB_NAME }]
});