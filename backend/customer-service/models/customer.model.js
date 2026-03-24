const mongoose = require("mongoose");

const customerSchema = new mongoose.Schema(
  {
    customerId: {
      type: String,
      required: true,
      unique: true,
      match: /^C\d{3}$/
    },
    title: {
      type: String,
      default: "Customer"
    },
    status: {
      type: String,
      default: "Active"
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Customer", customerSchema, "customers");
