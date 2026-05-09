import client from "./client";


export function createBooking(data) {
  return client.post("/bookings", data);
}


export function fetchMyBookings(params) {
  return client.get("/bookings/mine", { params });
}


export function updateBookingStatus(bookingId, data) {
  return client.patch(`/bookings/${bookingId}/status`, data);
}
