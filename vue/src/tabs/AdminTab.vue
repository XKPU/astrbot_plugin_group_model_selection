<template>
  <section class="tab-panel">
    <div class="panel-head">
      <h2>管理员白名单</h2>
      <button type="button" class="btn tonal sm" @click="addRow">+ 添加条目</button>
    </div>
    <p class="hint">
      可使用主命令的用户 UID（发送者 ID）（/sid 输出的 UID 行），每条一个；留空表示无人可用。会话查询命令（/mstosid）不受此名单限制。
    </p>
    <UserPicker v-model="picked" />
    <div v-if="rows.length === 0" class="empty">暂无条目，点击右上角「+ 添加条目」或使用上方选择器。</div>
    <div v-for="(row, index) in rows" :key="index" class="uid-row">
      <input
        v-model="rows[index]"
        type="text"
        placeholder="发送者 UID，如 123456789"
        @input="markDirty"
      >
      <button type="button" class="btn danger-text sm" @click="removeRow(index)">删除</button>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { store, markDirty } from "../store.js";
import UserPicker from "../components/UserPicker.vue";

const rows = computed({
  get: () => store.config.allowed_uids,
  set: (value) => {
    store.config.allowed_uids = value;
  },
});

const picked = computed({
  get: () => rows.value.filter((item) => item.trim() !== ""),
  set: (value) => {
    const blanks = rows.value.filter((item) => item.trim() === "");
    rows.value = [...value, ...blanks];
    markDirty();
  },
});

function addRow() {
  rows.value = [...rows.value, ""];
  markDirty();
}

function removeRow(index) {
  rows.value = rows.value.filter((_, i) => i !== index);
  markDirty();
}
</script>
