const Book = require("../models/book.model");

const listBooks = async (req, res) => {
  const books = await Book.find().lean();
  res.json(books);
};

const getBookByBookId = async (req, res) => {
  const book = await Book.findOne({ bookId: req.params.bookId }).lean();

  if (!book) {
    return res.status(404).json({ message: "Book not found" });
  }

  return res.json(book);
};

const createBook = async (req, res) => {
  const created = await Book.create(req.body);
  res.status(201).json(created);
};

module.exports = {
  listBooks,
  getBookByBookId,
  createBook
};
