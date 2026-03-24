const CartItem = require("../models/cartItem.model");

const listCartItems = async (req, res) => {
  const cartItems = await CartItem.find().lean();
  res.json(cartItems);
};

const getCartItemByCartId = async (req, res) => {
  const cartItem = await CartItem.findOne({ cartId: req.params.cartId }).lean();

  if (!cartItem) {
    return res.status(404).json({ message: "Cart item not found" });
  }

  return res.json(cartItem);
};

const createCartItem = async (req, res) => {
  const created = await CartItem.create(req.body);
  res.status(201).json(created);
};

module.exports = {
  listCartItems,
  getCartItemByCartId,
  createCartItem
};
