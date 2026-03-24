const express = require("express");
const {
  listCustomers,
  getCustomerByCustomerId,
  createCustomer
} = require("../controllers/customer.controller");

const router = express.Router();

router.get("/", listCustomers);
router.get("/:customerId", getCustomerByCustomerId);
router.post("/", createCustomer);

module.exports = router;
