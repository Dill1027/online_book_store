import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/books", label: "Books" },
  { to: "/customers", label: "Customers" },
  { to: "/cart", label: "Cart" },
  { to: "/orders", label: "Orders" }
];

function AppShell({ children }) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <p className="eyebrow">Online Book Store System</p>
          <h1 className="brand-title">Frontend Control Center</h1>
        </div>
        <p className="api-badge">Gateway: /api</p>
      </header>

      <nav className="main-nav" aria-label="Main navigation">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <main className="page-content">{children}</main>
    </div>
  );
}

export default AppShell;