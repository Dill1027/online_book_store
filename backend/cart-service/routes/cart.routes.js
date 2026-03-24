const express = require("express");
const {
  listCartItems,
  getCartItemByCartId,
  createCartItem
} = require("../controllers/cart.controller");

const router = express.Router();

router.get("/", listCartItems);
router.get("/:cartId", getCartItemByCartId);
router.post("/", createCartItem);

module.exports = router;
