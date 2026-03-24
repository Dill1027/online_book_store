import { useEffect, useState } from "react";
import { createCustomer, getCustomers } from "../services/customerService";

const initialForm = {
  customerId: "",
  title: "Customer",
  status: "Active"
};

function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(initialForm);

  const loadCustomers = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getCustomers();
      setCustomers(Array.isArray(data) ? data : []);
    } catch (fetchError) {
      setError(fetchError.response?.data?.message || "Failed to load customers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
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
      const created = await createCustomer(form);
      setCustomers((prev) => [created, ...prev]);
      setForm(initialForm);
    } catch (saveError) {
      setError(saveError.response?.data?.message || "Failed to create customer");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-grid">
      <article className="panel panel-form">
        <header className="panel-header">
          <p className="panel-kicker">Customer Service</p>
          <h2 className="panel-title">Create Customer</h2>
        </header>
        <form className="form-grid" onSubmit={onSubmit}>
          <label className="field field-wide">
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
            <span>title</span>
            <input
              name="title"
              value={form.title}
              onChange={onChange}
              placeholder="Customer"
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
            {saving ? "Saving..." : "Create Customer"}
          </button>
        </form>
      </article>

      <article className="panel panel-data">
        <header className="panel-header panel-header-row">
          <div>
            <p className="panel-kicker">Accounts</p>
            <h2 className="panel-title">Customers List</h2>
          </div>
          <button className="btn-secondary" type="button" onClick={loadCustomers}>
            Refresh
          </button>
        </header>

        {error ? <p className="alert">{error}</p> : null}

        {loading ? (
          <p className="meta">Loading customers...</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>customerId</th>
                  <th>title</th>
                  <th>status</th>
                </tr>
              </thead>
              <tbody>
                {customers.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="empty-cell">
                      No customers found
                    </td>
                  </tr>
                ) : (
                  customers.map((customer) => (
                    <tr key={customer._id || customer.customerId}>
                      <td>{customer.customerId}</td>
                      <td>{customer.title}</td>
                      <td>{customer.status}</td>
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

export default CustomersPage;
