const express = require("express");
const {
  listOrders,
  getOrderByOrderId,
  createOrder
} = require("../controllers/order.controller");

const router = express.Router();

router.get("/", listOrders);
router.get("/:orderId", getOrderByOrderId);
router.post("/", createOrder);

module.exports = router;
