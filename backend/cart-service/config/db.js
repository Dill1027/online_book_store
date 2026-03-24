const mongoose = require("mongoose");

const connectDB = async () => {
  const mongoUrl = process.env.MONGODB_URL;
  const dbName = process.env.DB_NAME || "online_book_store_db";

  if (!mongoUrl) {
    throw new Error("MONGODB_URL is required");
  }

  await mongoose.connect(mongoUrl, { dbName });
  console.log(`Cart Service connected to MongoDB database: ${dbName}`);
};

module.exports = connectDB;
