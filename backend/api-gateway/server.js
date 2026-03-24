const express = require("express");
const dotenv = require("dotenv");

dotenv.config();

const gatewayRoutes = require("./routes");

const app = express();
const port = process.env.PORT || 4000;
const allowedOrigins = new Set([
  "http://localhost:5173",
  "http://127.0.0.1:5173"
]);

app.use(express.json());

app.use((req, res, next) => {
  const origin = req.headers.origin;

  if (origin && allowedOrigins.has(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
  }

  res.setHeader("Vary", "Origin");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    return res.sendStatus(204);
  }

  return next();
});

app.get("/health", (req, res) => {
  res.json({ service: "api-gateway", status: "ok" });
});

app.use("/api", gatewayRoutes);

app.listen(port, () => {
  console.log(`API Gateway running on port ${port}`);
});
