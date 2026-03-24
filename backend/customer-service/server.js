const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db");
const customerRoutes = require("./routes/customer.routes");

dotenv.config();

const app = express();
const port = process.env.PORT || 4002;

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ service: "customer-service", status: "ok" });
});

app.use("/customers", customerRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: "Internal server error" });
});

connectDB()
  .then(() => {
    app.listen(port, () => {
      console.log(`Customer Service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Customer Service failed to start:", error.message);
    process.exit(1);
  });
