const mongoose = require("mongoose");

const ORDER_STATUS = [
  "Pending",
  "Confirmed",
  "Shipped",
  "Delivered",
  "Cancelled"
];

const orderSchema = new mongoose.Schema(
  {
    orderId: {
      type: String,
      required: true,
      unique: true,
      match: /^O\d{3}$/
    },
    customerId: {
      type: String,
      required: true,
      match: /^C\d{3}$/
    },
    bookId: {
      type: String,
      required: true,
      match: /^B\d{3}$/
    },
    title: {
      type: String,
      required: true,
      trim: true
    },
    price: {
      type: Number,
      required: true,
      min: 0
    },
    quantity: {
      type: Number,
      required: true,
      min: 1
    },
    status: {
      type: String,
      enum: ORDER_STATUS,
      default: "Pending"
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Order", orderSchema, "orders");
module.exports.ORDER_STATUS = ORDER_STATUS;
