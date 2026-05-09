import client from "./client";


export function fetchMyPayments(params) {
  return client.get("/payments/mine", { params });
}


export function payPayment(paymentId, data) {
  return client.patch(`/payments/${paymentId}/pay`, data);
}
