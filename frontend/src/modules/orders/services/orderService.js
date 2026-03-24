import httpClient from "../../../api/httpClient";

export const ORDER_STATUS = [
  "Pending",
  "Confirmed",
  "Shipped",
  "Delivered",
  "Cancelled"
];

export const getOrders = async () => {
  const response = await httpClient.get("/orders");
  return response.data;
};

export const createOrder = async (payload) => {
  const response = await httpClient.post("/orders", payload);
  return response.data;
};