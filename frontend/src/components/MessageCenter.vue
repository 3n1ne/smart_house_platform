<template>
  <div class="page-card message-center">
    <div class="section-head section-head--compact">
      <div>
        <span class="eyebrow">{{ eyebrow }}</span>
        <h2 class="page-title page-title--section">{{ title }}</h2>
        <p class="page-text">{{ description }}</p>
      </div>

      <div class="hero-actions">
        <span class="tag" v-if="unreadTotal">{{ unreadTotal }} 条未读</span>
        <span class="tag tag--light" v-else>全部已读</span>
        <button class="ghost-button" type="button" :disabled="loading.conversations" @click="refreshAll">
          {{ loading.conversations ? "刷新中..." : "刷新" }}
        </button>
      </div>
    </div>

    <p v-if="errors.conversations" class="form-message form-message--error">
      {{ errors.conversations }}
    </p>

    <div class="message-layout" v-if="conversations.length">
      <div class="message-sidebar">
        <button
          v-for="conversation in conversations"
          :key="conversation.conversation_key"
          class="message-thread"
          :class="{ 'message-thread--active': activeConversation?.conversation_key === conversation.conversation_key }"
          type="button"
          @click="selectConversation(conversation)"
        >
          <div class="house-meta">
            <span class="tag tag--light">{{ conversation.house?.title || "普通会话" }}</span>
            <span v-if="conversation.unread_count" class="tag">{{ conversation.unread_count }} 条新消息</span>
          </div>
          <strong>{{ displayName(conversation.counterpart) }}</strong>
          <p class="message-preview">{{ conversation.last_message?.content || "暂无内容" }}</p>
          <span class="message-thread__time">{{ formatDateTime(conversation.last_message_at) }}</span>
        </button>
      </div>

      <div class="message-panel" v-if="activeConversation">
        <div class="message-panel__header">
          <div>
            <h3 class="house-title house-title--small">{{ displayName(activeConversation.counterpart) }}</h3>
            <p class="page-text">{{ activeConversation.house?.title || "普通会话" }}</p>
          </div>
          <span class="tag tag--light">{{ activeConversation.message_count }} 条消息</span>
        </div>

        <p v-if="errors.messages" class="form-message form-message--error">{{ errors.messages }}</p>

        <div v-if="loading.messages" class="empty-card empty-card--soft message-empty">
          <p class="page-text">正在加载会话内容...</p>
        </div>

        <div v-else-if="threadMessages.length" class="message-list">
          <article
            v-for="message in threadMessages"
            :key="message.id"
            class="chat-bubble"
            :class="{ 'chat-bubble--mine': message.is_mine }"
          >
            <div class="chat-bubble__meta">
              <span>{{ message.is_mine ? "我" : displayName(message.sender) }}</span>
              <span>{{ formatDateTime(message.created_at) }}</span>
            </div>
            <p>{{ message.content }}</p>
          </article>
        </div>

        <div v-else class="empty-card empty-card--soft message-empty">
          <p class="page-text">这个会话暂时还没有消息。</p>
        </div>

        <form class="form-stack" @submit.prevent="handleSendMessage">
          <label class="field">
            <span>回复内容</span>
            <textarea v-model.trim="draftMessage" rows="4" placeholder="请输入回复内容" />
          </label>

          <p v-if="errors.compose" class="form-message form-message--error">{{ errors.compose }}</p>

          <div class="filter-actions">
            <button class="primary-button" type="submit" :disabled="loading.submit">
              {{ loading.submit ? "发送中..." : "发送消息" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-else-if="!loading.conversations" class="empty-card empty-card--soft">
      <h3 class="page-title page-title--section">暂无会话</h3>
      <p class="page-text">{{ emptyText }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import {
  fetchMessageConversations,
  fetchMessages,
  markMessagesRead,
  sendMessage as sendMessageRequest,
} from "../api/message";

defineProps({
  eyebrow: {
    type: String,
    default: "消息中心",
  },
  title: {
    type: String,
    default: "会话中心",
  },
  description: {
    type: String,
    default: "查看未读消息，并直接在当前页面完成回复。",
  },
  emptyText: {
    type: String,
    default: "可以从房源详情页发起第一条咨询。",
  },
});

const conversations = ref([]);
const activeConversation = ref(null);
const threadMessages = ref([]);
const draftMessage = ref("");
const unreadTotal = ref(0);

const loading = reactive({
  conversations: false,
  messages: false,
  submit: false,
});

const errors = reactive({
  conversations: "",
  messages: "",
  compose: "",
});

function displayName(user) {
  return user?.real_name || user?.username || "未知用户";
}

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString() : "刚刚";
}

async function markConversationRead(conversation) {
  if (!conversation || !conversation.unread_count) {
    return;
  }

  const payload = {
    counterpart_id: conversation.counterpart.id,
  };
  if (conversation.house?.id) {
    payload.house_id = conversation.house.id;
  }

  try {
    const response = await markMessagesRead(payload);
    unreadTotal.value = response.data.data.unread_total || 0;

    conversations.value = conversations.value.map((item) =>
      item.conversation_key === conversation.conversation_key
        ? { ...item, unread_count: 0 }
        : item
    );
    activeConversation.value =
      conversations.value.find((item) => item.conversation_key === conversation.conversation_key) ||
      activeConversation.value;
  } catch {
    // Keep the existing UI state if read-marking fails.
  }
}

async function loadMessages(conversation, options = {}) {
  if (!conversation) {
    threadMessages.value = [];
    return;
  }

  loading.messages = true;
  errors.messages = "";

  try {
    const params = {
      counterpart_id: conversation.counterpart.id,
      page_size: 100,
    };
    if (conversation.house?.id) {
      params.house_id = conversation.house.id;
    }

    const response = await fetchMessages(params);
    threadMessages.value = response.data.data.items;

    if (options.markRead !== false) {
      await markConversationRead(conversation);
    }
  } catch (error) {
    errors.messages = error.message || "加载消息失败。";
    threadMessages.value = [];
  } finally {
    loading.messages = false;
  }
}

async function loadConversations(options = {}) {
  const preferredKey = options.preferredKey || activeConversation.value?.conversation_key || "";
  loading.conversations = true;
  errors.conversations = "";

  try {
    const response = await fetchMessageConversations();
    const payload = response.data.data;

    conversations.value = payload.items || [];
    unreadTotal.value = payload.unread_total || 0;

    if (!conversations.value.length) {
      activeConversation.value = null;
      threadMessages.value = [];
      return;
    }

    const nextConversation =
      conversations.value.find((item) => item.conversation_key === preferredKey) ||
      conversations.value[0];
    const changed =
      activeConversation.value?.conversation_key !== nextConversation.conversation_key;

    activeConversation.value = nextConversation;

    if (changed || options.reloadMessages || !threadMessages.value.length) {
      await loadMessages(nextConversation);
    }
  } catch (error) {
    errors.conversations = error.message || "加载会话列表失败。";
    conversations.value = [];
    activeConversation.value = null;
    threadMessages.value = [];
    unreadTotal.value = 0;
  } finally {
    loading.conversations = false;
  }
}

async function selectConversation(conversation) {
  activeConversation.value = conversation;
  await loadMessages(conversation);
}

async function refreshAll() {
  await loadConversations({
    preferredKey: activeConversation.value?.conversation_key,
    reloadMessages: true,
  });
}

async function handleSendMessage() {
  errors.compose = "";
  const content = draftMessage.value.trim();

  if (!activeConversation.value) {
    errors.compose = "请先选择一个会话。";
    return;
  }

  if (!content) {
    errors.compose = "请输入消息内容。";
    return;
  }

  loading.submit = true;
  try {
    const payload = {
      receiver_id: activeConversation.value.counterpart.id,
      content,
    };
    if (activeConversation.value.house?.id) {
      payload.house_id = activeConversation.value.house.id;
    }

    await sendMessageRequest(payload);
    draftMessage.value = "";
    await loadConversations({
      preferredKey: activeConversation.value.conversation_key,
      reloadMessages: true,
    });
  } catch (error) {
    errors.compose = error.message || "发送消息失败。";
  } finally {
    loading.submit = false;
  }
}

onMounted(async () => {
  await loadConversations();
});
</script>
