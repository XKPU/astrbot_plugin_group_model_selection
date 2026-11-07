<template>
  <button type="button" class="btn ghost sm" @click="open">选择</button>

  <Teleport to="body">
    <div v-if="visible" class="modal-mask" @click.self="close">
      <div class="modal-card">
        <div class="modal-head">
          <h3 class="modal-title">选择会话</h3>
          <button type="button" class="chip-close lg" aria-label="关闭" @click="close">×</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <input
              v-model="keyword"
              type="text"
              placeholder="过滤 UMO / 名称"
              @input="onInput"
            >
          </div>
          <div v-if="error" class="alert err">{{ error }}</div>
          <div v-if="loading" class="hint">加载中…</div>
          <div v-else-if="filtered.length === 0" class="empty">没有匹配的会话。</div>
          <div
            v-for="item in visibleItems"
            :key="item.umo"
            class="picker-row umos"
          >
            <button
              type="button"
              class="picker-row-btn"
              @click="choose(item.umo)"
            >
              <span class="picker-main">{{ item.display_name || item.umo }}</span>
              <span v-if="item.display_name && item.display_name !== item.umo" class="picker-sub">{{ item.umo }}</span>
              <span v-if="item.platform" class="picker-tag">{{ item.platform }}</span>
            </button>
          </div>
          <div v-if="filtered.length > visibleLimit" class="hint">
            还有 {{ filtered.length - visibleItems.length }} 条未显示，请缩小过滤条件。
          </div>
        </div>
        <div class="modal-foot">
          <span class="modal-count">共 {{ filtered.length }} 条</span>
          <button type="button" class="btn primary sm" @click="close">完成</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref } from "vue";
import { apiGet } from "../sdk.js";

const visible = ref(false);
const keyword = ref("");
const items = ref([]);
const loading = ref(false);
const error = ref("");
const visibleLimit = 50;
let filterTimer = null;

const emit = defineEmits(["select"]);

const filtered = computed(() => {
  const token = keyword.value.trim().toLowerCase();
  if (token === "") return items.value;
  return items.value.filter(
    (item) =>
      item.umo.toLowerCase().includes(token) ||
      (item.display_name || "").toLowerCase().includes(token) ||
      (item.sender_name || "").toLowerCase().includes(token),
  );
});

const visibleItems = computed(() => filtered.value.slice(0, visibleLimit));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const wrap = await apiGet("umos");
    items.value = wrap?.umos || [];
  } catch (err) {
    error.value = `读取会话列表失败：${err?.message || err}`;
    items.value = [];
  } finally {
    loading.value = false;
  }
}

function onInput() {
  if (filterTimer) clearTimeout(filterTimer);
  filterTimer = setTimeout(() => {
    /* filtered is computed; the timeout only batches rapid input events. */
  }, 200);
}

function choose(umo) {
  emit("select", umo);
  close();
}

function open() {
  visible.value = true;
  keyword.value = "";
  error.value = "";
  load();
}

function close() {
  visible.value = false;
}
</script>
