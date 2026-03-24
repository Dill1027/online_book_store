const express = require("express");
const dotenv = require("dotenv");
const gatewayRoutes = require("./routes");

dotenv.config();

const app = express();
const port = process.env.PORT || 4000;

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ service: "api-gateway", status: "ok" });
});

app.use("/api", gatewayRoutes);

app.listen(port, () => {
  console.log(`API Gateway running on port ${port}`);
});
