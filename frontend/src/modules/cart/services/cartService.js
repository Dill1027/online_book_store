import httpClient from "../../../api/httpClient";

export const getCartItems = async () => {
  const response = await httpClient.get("/cart-items");
  return response.data;
};

export const createCartItem = async (payload) => {
  const response = await httpClient.post("/cart-items", payload);
  return response.data;
};