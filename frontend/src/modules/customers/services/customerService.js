import httpClient from "../../../api/httpClient";

export const getCustomers = async () => {
  const response = await httpClient.get("/customers");
  return response.data;
};

export const createCustomer = async (payload) => {
  const response = await httpClient.post("/customers", payload);
  return response.data;
};