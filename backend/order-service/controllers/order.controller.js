const Order = require("../models/order.model");

const listOrders = async (req, res) => {
  const orders = await Order.find().lean();
  res.json(orders);
};

const getOrderByOrderId = async (req, res) => {
  const order = await Order.findOne({ orderId: req.params.orderId }).lean();

  if (!order) {
    return res.status(404).json({ message: "Order not found" });
  }

  return res.json(order);
};

const createOrder = async (req, res) => {
  const created = await Order.create(req.body);
  res.status(201).json(created);
};

module.exports = {
  listOrders,
  getOrderByOrderId,
  createOrder
};
