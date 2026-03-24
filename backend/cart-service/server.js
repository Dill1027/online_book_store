const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db");
const cartRoutes = require("./routes/cart.routes");

dotenv.config();

const app = express();
const port = process.env.PORT || 4003;

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ service: "cart-service", status: "ok" });
});

app.use("/cart-items", cartRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: "Internal server error" });
});

connectDB()
  .then(() => {
    app.listen(port, () => {
      console.log(`Cart Service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Cart Service failed to start:", error.message);
    process.exit(1);
  });
