import { useEffect, useState } from "react";
import { createBook, getBooks } from "../services/bookService";

const initialForm = {
  bookId: "",
  title: "",
  price: "",
  quantity: "",
  status: "Active"
};

function BooksPage() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(initialForm);

  const loadBooks = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getBooks();
      setBooks(Array.isArray(data) ? data : []);
    } catch (fetchError) {
      setError(fetchError.response?.data?.message || "Failed to load books");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      const payload = {
        ...form,
        price: Number(form.price),
        quantity: Number(form.quantity)
      };
      const created = await createBook(payload);
      setBooks((prev) => [created, ...prev]);
      setForm(initialForm);
    } catch (saveError) {
      setError(saveError.response?.data?.message || "Failed to create book");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-grid">
      <article className="panel panel-form">
        <header className="panel-header">
          <p className="panel-kicker">Book Service</p>
          <h2 className="panel-title">Create Book</h2>
        </header>
        <form className="form-grid" onSubmit={onSubmit}>
          <label className="field">
            <span>bookId</span>
            <input
              name="bookId"
              value={form.bookId}
              onChange={onChange}
              placeholder="B001"
              required
            />
          </label>
          <label className="field field-wide">
            <span>title</span>
            <input
              name="title"
              value={form.title}
              onChange={onChange}
              placeholder="Atomic Habits"
              required
            />
          </label>
          <label className="field">
            <span>price</span>
            <input
              name="price"
              type="number"
              min="0"
              step="0.01"
              value={form.price}
              onChange={onChange}
              required
            />
          </label>
          <label className="field">
            <span>quantity</span>
            <input
              name="quantity"
              type="number"
              min="0"
              value={form.quantity}
              onChange={onChange}
              required
            />
          </label>
          <label className="field field-wide">
            <span>status</span>
            <input
              name="status"
              value={form.status}
              onChange={onChange}
              placeholder="Active"
              required
            />
          </label>
          <button className="btn-primary field-wide" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Create Book"}
          </button>
        </form>
      </article>

      <article className="panel panel-data">
        <header className="panel-header panel-header-row">
          <div>
            <p className="panel-kicker">Inventory</p>
            <h2 className="panel-title">Books List</h2>
          </div>
          <button className="btn-secondary" type="button" onClick={loadBooks}>
            Refresh
          </button>
        </header>

        {error ? <p className="alert">{error}</p> : null}

        {loading ? (
          <p className="meta">Loading books...</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>bookId</th>
                  <th>title</th>
                  <th>price</th>
                  <th>quantity</th>
                  <th>status</th>
                </tr>
              </thead>
              <tbody>
                {books.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="empty-cell">
                      No books found
                    </td>
                  </tr>
                ) : (
                  books.map((book) => (
                    <tr key={book._id || book.bookId}>
                      <td>{book.bookId}</td>
                      <td>{book.title}</td>
                      <td>{book.price}</td>
                      <td>{book.quantity}</td>
                      <td>{book.status}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}

export default BooksPage;
