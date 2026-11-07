<template>
  <div class="chip-row">
    <span
      v-for="chip in selected"
      :key="chip.id"
      class="chip"
      :title="chip.id"
    >{{ chip.name || chip.id }}
      <button
        type="button"
        class="chip-close"
        :aria-label="`移除 ${chip.id}`"
        @click="toggle(chip.id)"
      >×</button>
    </span>
    <button type="button" class="btn tonal sm" @click="open">选择用户</button>
  </div>

  <Teleport to="body">
    <div v-if="visible" class="modal-mask" @click.self="close">
      <div class="modal-card">
        <div class="modal-head">
          <h3 class="modal-title">选择用户</h3>
          <button type="button" class="chip-close lg" aria-label="关闭" @click="close">×</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <input
              v-model="keyword"
              type="text"
              placeholder="搜索发送者 UID / 名称"
              @input="onInput"
              @keyup.enter="canAddKeyword && addKeyword()"
            >
          </div>
          <div v-if="error" class="alert err">{{ error }}</div>
          <div v-if="loading" class="hint">加载中…</div>
          <div v-else-if="results.length === 0 && !canAddKeyword" class="empty">
            没有匹配的用户。
          </div>
          <label
            v-for="item in results"
            :key="item.sender_id"
            class="picker-row"
          >
            <input
              type="checkbox"
              :checked="modelValue.indexOf(item.sender_id) >= 0"
              @change="toggle(item.sender_id)"
            >
            <span class="picker-main">{{ item.sender_name || item.sender_id }}</span>
            <span class="picker-sub">{{ item.sender_id }}</span>
            <span v-if="item.platform" class="picker-tag">{{ item.platform }}</span>
          </label>
          <button
            v-if="canAddKeyword"
            type="button"
            class="btn ghost sm"
            @click="addKeyword"
          >将「{{ keyword.trim() }}」作为手动 UID 添加</button>
        </div>
        <div class="modal-foot">
          <span class="modal-count">已选 {{ modelValue.length }} 个</span>
          <button type="button" class="btn primary sm" @click="close">完成</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { apiGet } from "../sdk.js";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
});

const visible = ref(false);
const keyword = ref("");
const results = ref([]);
const loading = ref(false);
const error = ref("");
const names = reactive({});
let searchTimer = null;

const selected = computed(() =>
  props.modelValue.map((id) => ({ id, name: names[id] || "" })),
);

const canAddKeyword = computed(() => {
  const token = keyword.value.trim();
  return (
    token !== "" &&
    props.modelValue.indexOf(token) < 0 &&
    !results.value.some((item) => item.sender_id === token)
  );
});

function toggle(id) {
  const next = [...props.modelValue];
  const index = next.indexOf(id);
  if (index >= 0) {
    next.splice(index, 1);
  } else {
    next.push(id);
  }
  emit("update:modelValue", next);
}

function addKeyword() {
  const token = keyword.value.trim();
  if (token === "" || props.modelValue.indexOf(token) >= 0) return;
  emit("update:modelValue", [...props.modelValue, token]);
}

async function resolveNames(ids) {
  const missing = ids.filter((id) => names[id] === undefined);
  if (missing.length === 0) return;
  try {
    const wrap = await apiGet("senders", { sender_ids: missing, limit: 100 });
    for (const item of wrap?.senders || []) {
      names[item.sender_id] = item.sender_name || "";
    }
  } catch (err) {
    /* Display falls back to the raw ID. */
  }
}

async function search() {
  loading.value = true;
  error.value = "";
  try {
    const wrap = await apiGet("senders", {
      search: keyword.value.trim(),
      limit: 50,
    });
    results.value = wrap?.senders || [];
  } catch (err) {
    error.value = `读取用户列表失败：${err?.message || err}`;
    results.value = [];
  } finally {
    loading.value = false;
  }
}

function onInput() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(search, 250);
}

function open() {
  visible.value = true;
  keyword.value = "";
  error.value = "";
  search();
}

function close() {
  visible.value = false;
}

watch(
  () => props.modelValue,
  (value) => resolveNames([...value]),
  { immediate: true, deep: true },
);

const emit = defineEmits(["update:modelValue"]);
</script>
