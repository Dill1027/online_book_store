const express = require("express");
const {
  listBooks,
  getBookByBookId,
  createBook
} = require("../controllers/book.controller");

const router = express.Router();

router.get("/", listBooks);
router.get("/:bookId", getBookByBookId);
router.post("/", createBook);

module.exports = router;
