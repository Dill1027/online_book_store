const mongoose = require("mongoose");

const cartItemSchema = new mongoose.Schema(
  {
    cartId: {
      type: String,
      required: true,
      unique: true,
      match: /^CRT\d{3}$/
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
      default: "Pending"
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model("CartItem", cartItemSchema, "cartItems");
