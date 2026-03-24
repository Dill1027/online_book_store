const Customer = require("../models/customer.model");

const listCustomers = async (req, res) => {
  const customers = await Customer.find().lean();
  res.json(customers);
};

const getCustomerByCustomerId = async (req, res) => {
  const customer = await Customer.findOne({ customerId: req.params.customerId }).lean();

  if (!customer) {
    return res.status(404).json({ message: "Customer not found" });
  }

  return res.json(customer);
};

const createCustomer = async (req, res) => {
  const created = await Customer.create(req.body);
  res.status(201).json(created);
};

module.exports = {
  listCustomers,
  getCustomerByCustomerId,
  createCustomer
};
