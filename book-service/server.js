const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db");
const bookRoutes = require("./routes/book.routes");

dotenv.config();

const app = express();
const port = process.env.PORT || 4001;

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ service: "book-service", status: "ok" });
});

app.use("/books", bookRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: "Internal server error" });
});

connectDB()
  .then(() => {
    app.listen(port, () => {
      console.log(`Book Service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Book Service failed to start:", error.message);
    process.exit(1);
  });
