const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");

const router = express.Router();

router.get("/services", (req, res) => {
  res.json({
    books: process.env.BOOK_SERVICE_URL,
    customers: process.env.CUSTOMER_SERVICE_URL,
    cartItems: process.env.CART_SERVICE_URL,
    orders: process.env.ORDER_SERVICE_URL
  });
});

router.use(
  "/books",
  createProxyMiddleware({
    target: process.env.BOOK_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path) => `/books${path === "/" ? "" : path}`
  })
);

router.use(
  "/customers",
  createProxyMiddleware({
    target: process.env.CUSTOMER_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path) => `/customers${path === "/" ? "" : path}`
  })
);

router.use(
  "/cart-items",
  createProxyMiddleware({
    target: process.env.CART_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path) => `/cart-items${path === "/" ? "" : path}`
  })
);

router.use(
  "/orders",
  createProxyMiddleware({
    target: process.env.ORDER_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: (path) => `/orders${path === "/" ? "" : path}`
  })
);

module.exports = router;
