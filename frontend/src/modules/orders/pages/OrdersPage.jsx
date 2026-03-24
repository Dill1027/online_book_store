import { useEffect, useState } from "react";
import { ORDER_STATUS, createOrder, getOrders } from "../services/orderService";

const initialForm = {
  orderId: "",
  customerId: "",
  bookId: "",
  title: "",
  price: "",
  quantity: "",
  status: "Pending"
};

function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(initialForm);

  const loadOrders = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getOrders();
      setOrders(Array.isArray(data) ? data : []);
    } catch (fetchError) {
      setError(fetchError.response?.data?.message || "Failed to load orders");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
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
      const created = await createOrder(payload);
      setOrders((prev) => [created, ...prev]);
      setForm(initialForm);
    } catch (saveError) {
      setError(saveError.response?.data?.message || "Failed to create order");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-grid">
      <article className="panel panel-form">
        <header className="panel-header">
          <p className="panel-kicker">Order Service</p>
          <h2 className="panel-title">Create Order</h2>
        </header>
        <form className="form-grid" onSubmit={onSubmit}>
          <label className="field">
            <span>orderId</span>
            <input
              name="orderId"
              value={form.orderId}
              onChange={onChange}
              placeholder="O001"
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
            <select name="status" value={form.status} onChange={onChange}>
              {ORDER_STATUS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <button className="btn-primary field-wide" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Create Order"}
          </button>
        </form>
      </article>

      <article className="panel panel-data">
        <header className="panel-header panel-header-row">
          <div>
            <p className="panel-kicker">Fulfillment</p>
            <h2 className="panel-title">Orders List</h2>
          </div>
          <button className="btn-secondary" type="button" onClick={loadOrders}>
            Refresh
          </button>
        </header>

        {error ? <p className="alert">{error}</p> : null}

        {loading ? (
          <p className="meta">Loading orders...</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>orderId</th>
                  <th>customerId</th>
                  <th>bookId</th>
                  <th>title</th>
                  <th>price</th>
                  <th>quantity</th>
                  <th>status</th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty-cell">
                      No orders found
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => (
                    <tr key={order._id || order.orderId}>
                      <td>{order.orderId}</td>
                      <td>{order.customerId}</td>
                      <td>{order.bookId}</td>
                      <td>{order.title}</td>
                      <td>{order.price}</td>
                      <td>{order.quantity}</td>
                      <td>{order.status}</td>
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

export default OrdersPage;
