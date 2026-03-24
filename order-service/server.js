const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db");
const orderRoutes = require("./routes/order.routes");

dotenv.config();

const app = express();
const port = process.env.PORT || 4004;

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ service: "order-service", status: "ok" });
});

app.use("/orders", orderRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: "Internal server error" });
});

connectDB()
  .then(() => {
    app.listen(port, () => {
      console.log(`Order Service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Order Service failed to start:", error.message);
    process.exit(1);
  });
