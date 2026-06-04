import client from "./client";


export function fetchMyPayments(params) {
  return client.get("/payments/mine", { params });
}


export function payPayment(paymentId, data) {
  return client.patch(`/payments/${paymentId}/pay`, data);
}


export function failPayment(paymentId, data) {
  return client.patch(`/payments/${paymentId}/fail`, data);
}


export function refundPayment(paymentId, data) {
  return client.patch(`/payments/${paymentId}/refund`, data);
}


export function markOverduePayments() {
  return client.post("/payments/overdue-scan");
}
