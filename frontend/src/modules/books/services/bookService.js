import httpClient from "../../../api/httpClient";

export const getBooks = async () => {
  const response = await httpClient.get("/books");
  return response.data;
};

export const createBook = async (payload) => {
  const response = await httpClient.post("/books", payload);
  return response.data;
};