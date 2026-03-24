import { Navigate, Route, Routes } from "react-router-dom";
import BooksPage from "../modules/books/pages/BooksPage";
import CustomersPage from "../modules/customers/pages/CustomersPage";
import CartPage from "../modules/cart/pages/CartPage";
import OrdersPage from "../modules/orders/pages/OrdersPage";
import AppShell from "../layouts/AppShell";

function AppRoutes() {
  return (
    <AppShell>
      <Routes>
        <Route path="/books" element={<BooksPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="*" element={<Navigate to="/books" replace />} />
      </Routes>
    </AppShell>
  );
}

export default AppRoutes;
