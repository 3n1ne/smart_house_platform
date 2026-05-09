import client from "./client";


export function fetchMessageConversations() {
  return client.get("/messages/conversations");
}

export function fetchMessages(params) {
  return client.get("/messages", { params });
}

export function sendMessage(data) {
  return client.post("/messages", data);
}

export function markMessagesRead(data) {
  return client.patch("/messages/read", data);
}
