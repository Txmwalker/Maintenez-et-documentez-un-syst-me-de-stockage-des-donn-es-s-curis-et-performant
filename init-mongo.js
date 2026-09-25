db = db.getSiblingDB(process.env.APP_DB_NAME);

db.createUser({
  user: process.env.APP_DB_USER,
  pwd: process.env.APP_DB_PASSWORD,
  roles: [{ role: "readWrite", db: process.env.APP_DB_NAME }]
});