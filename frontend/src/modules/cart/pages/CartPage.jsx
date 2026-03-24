import { useEffect, useState } from "react";
import { createCartItem, getCartItems } from "../services/cartService";

const initialForm = {
  cartId: "",
  customerId: "",
  bookId: "",
  title: "",
  price: "",
  quantity: "",
  status: "Pending"
};

function CartPage() {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(initialForm);

  const loadCartItems = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getCartItems();
      setCartItems(Array.isArray(data) ? data : []);
    } catch (fetchError) {
      setError(fetchError.response?.data?.message || "Failed to load cart items");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCartItems();
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
      const created = await createCartItem(payload);
      setCartItems((prev) => [created, ...prev]);
      setForm(initialForm);
    } catch (saveError) {
      setError(saveError.response?.data?.message || "Failed to create cart item");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-grid">
      <article className="panel panel-form">
        <header className="panel-header">
          <p className="panel-kicker">Cart Service</p>
          <h2 className="panel-title">Add Cart Item</h2>
        </header>
        <form className="form-grid" onSubmit={onSubmit}>
          <label className="field">
            <span>cartId</span>
            <input
              name="cartId"
              value={form.cartId}
              onChange={onChange}
              placeholder="CRT001"
              required
            />
          </label>
          <label className="field">
            <span>customerId</span>
            <input
              name="customerId"
              value={form.customerId}
              onChange={onChange}
              placeholder="C001"
              required
            />
          </label>
          <label className="field field-wide">
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
              placeholder="Book title"
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
              min="1"
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
              placeholder="Pending"
              required
            />
          </label>
          <button className="btn-primary field-wide" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Add Item"}
          </button>
        </form>
      </article>

      <article className="panel panel-data">
        <header className="panel-header panel-header-row">
          <div>
            <p className="panel-kicker">Checkout Prep</p>
            <h2 className="panel-title">Cart Items</h2>
          </div>
          <button className="btn-secondary" type="button" onClick={loadCartItems}>
            Refresh
          </button>
        </header>

        {error ? <p className="alert">{error}</p> : null}

        {loading ? (
          <p className="meta">Loading cart items...</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>cartId</th>
                  <th>customerId</th>
                  <th>bookId</th>
                  <th>title</th>
                  <th>price</th>
                  <th>quantity</th>
                  <th>status</th>
                </tr>
              </thead>
              <tbody>
                {cartItems.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty-cell">
                      No cart items found
                    </td>
                  </tr>
                ) : (
                  cartItems.map((cartItem) => (
                    <tr key={cartItem._id || cartItem.cartId}>
                      <td>{cartItem.cartId}</td>
                      <td>{cartItem.customerId}</td>
                      <td>{cartItem.bookId}</td>
                      <td>{cartItem.title}</td>
                      <td>{cartItem.price}</td>
                      <td>{cartItem.quantity}</td>
                      <td>{cartItem.status}</td>
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

export default CartPage;
