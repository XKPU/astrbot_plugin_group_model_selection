<template>
  <section class="tab-panel">
    <div class="panel-head">
      <h2>会话模型</h2>
      <button type="button" class="btn tonal sm" @click="addRow">+ 新建条目</button>
    </div>
    <p class="hint">
      列表自动读取已设置首选模型的会话；新会话点击「+ 新建条目」，填入 UMO（会话 ID）并设置模型，行为与主命令一致。
    </p>
    <div v-if="rows.length === 0" class="empty">暂无已设置首选模型的会话；点击「+ 新建条目」填入 UMO（会话 ID）。</div>
    <div v-for="(row, index) in rows" :key="row.key" class="session-row">
      <div class="session-head">
        <span class="session-title">{{ row.umo || "新条目" }}</span>
        <button type="button" class="btn tonal sm" :disabled="row.busy" @click="applyRow(index)">
          应用
        </button>
        <button type="button" class="btn tonal sm" :disabled="row.busy" @click="clearRow(index)">
        清除模型设置
        </button>
        <button type="button" class="btn danger-text sm" :disabled="row.busy" @click="removeRow(index)">
          删除
        </button>
      </div>
      <div class="field">
        <label :for="'session-umo-' + row.key">UMO（会话 ID）</label>
        <input
          :id="'session-umo-' + row.key"
          v-model="row.umo"
          class="session-umo-input"
          type="text"
          placeholder="平台:UserId:SessionId"
          @input="markDirty"
        >
      </div>
      <div class="field">
        <label :for="'session-model-' + row.key">首选模型（别名或模型 ID，留空 = 恢复默认）</label>
        <input
          :id="'session-model-' + row.key"
          v-model="row.token"
          type="text"
          list="provider-list"
          placeholder="如 glm-5.2"
        >
      </div>
      <div v-if="row.result" class="session-row-result" :class="row.ok ? 'ok' : 'err'">{{ row.result }}</div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { apiGet, apiPost, pick } from "../sdk.js";
import { store } from "../store.js";

const rows = ref([]);
let rowKey = 0;

function makeRow(umo, asSet) {
  return {
    key: ++rowKey,
    umo: umo || "",
    token: asSet || "",
    busy: false,
    result: "",
    ok: false,
  };
}

async function loadSessions() {
  try {
    /* The bridge unwraps ok envelopes and throws on error ones. */
    const umos = (pick(await apiGet("sessions")).sessions) || [];
    const details = await Promise.all(
      umos.map((umo) =>
        apiGet("session-model", { umo })
          .then((detail) => (detail ? pick(detail).info : null))
          .catch(() => null),
      ),
    );
    rows.value = umos.map((umo, i) => {
      const info = details[i];
      return makeRow(umo, info ? info.as_set || info.alias || info.provider_id || "" : "");
    });
  } catch (err) {
    rows.value = [];
  }
}

function addRow() {
  rows.value.push(makeRow("", ""));
}

function removeRow(index) {
  rows.value.splice(index, 1);
}

async function applyRow(index) {
  const row = rows.value[index];
  if (!row.umo.trim()) {
    row.result = "请先填写 UMO（会话 ID）。";
    row.ok = false;
    return;
  }
  row.busy = true;
  row.result = "";
  try {
    const resp = await apiPost("session-model", { umo: row.umo.trim(), token: row.token.trim() });
    if (resp && resp.status === "error") {
      throw new Error(resp.message || "设置错误");
    }
    row.result = row.token.trim()
      ? "当前会话模型更改为：" + row.token.trim()
      : "已清除该会话的模型设置，恢复默认配置。";
    row.ok = true;
  } catch (err) {
    row.result = err.message || String(err);
    row.ok = false;
  } finally {
    row.busy = false;
  }
}

async function clearRow(index) {
  const row = rows.value[index];
  if (!row.umo.trim()) {
    row.result = "请先填写 UMO（会话 ID）。";
    row.ok = false;
    return;
  }
  row.busy = true;
  row.result = "";
  try {
    const resp = await apiPost("session-model", { umo: row.umo.trim(), token: "" });
    if (resp && resp.status === "error") {
      throw new Error(resp.message || "设置错误");
    }
    row.token = "";
    row.result = "已清除该会话的模型设置，恢复默认配置。";
    row.ok = true;
  } catch (err) {
    row.result = err.message || String(err);
    row.ok = false;
  } finally {
    row.busy = false;
  }
}

onMounted(() => {
  loadSessions();
});
</script>
