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
        <button type="button" class="btn danger-text sm" @click="removeRow(index)">
          删除
        </button>
      </div>
      <div class="field">
        <label :for="'session-umo-' + row.key">UMO（会话 ID）</label>
        <div class="picker-inline">
          <input
            :id="'session-umo-' + row.key"
            v-model="row.umo"
            class="session-umo-input"
            type="text"
            placeholder="平台:UserId:SessionId"
            @input="markDirty"
          >
          <UmoPicker @select="chooseUmo(row, $event)" />
        </div>
      </div>
      <div class="field">
        <label :for="'session-model-' + row.key">首选模型（别名或模型 ID，留空 = 恢复默认）</label>
        <input
          :id="'session-model-' + row.key"
          v-model="row.token"
          type="text"
          list="provider-list"
          placeholder="如 glm-5.2"
          @input="markDirty"
        >
        <button
          v-if="row.token"
          type="button"
          class="btn ghost sm"
          :disabled="store.busy"
          @click="clearRow(index)"
        >
          恢复默认（清除该字段）
        </button>
      </div>
      <div v-if="row.result" class="session-row-result" :class="row.ok ? 'ok' : 'err'">{{ row.result }}</div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { apiGet, pick } from "../sdk.js";
import UmoPicker from "../components/UmoPicker.vue";
import {
  store,
  markDirty,
  snapshotSessions,
  markSessionsSaved,
} from "../store.js";

const rows = ref([]);
let rowKey = 0;

function chooseUmo(row, umo) {
  row.umo = umo;
  markDirty();
}

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

function syncStore() {
  store.sessionRows = rows.value;
  markSessionsSaved();
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
    syncStore();
  } catch (err) {
    rows.value = [];
  }
}

/* Registered as store.reloadSessions so 重新加载/取消编辑 refresh rows too. */
async function reloadSessions() {
  await loadSessions();
}

function addRow() {
  rows.value.push(makeRow("", ""));
  syncStore();
}

function removeRow(index) {
  rows.value.splice(index, 1);
  syncStore();
  markDirty();
}

/* Token-only clear: blank the field and let the unified save flow apply it
 * (empty token = reset that session to the default model). */
function clearRow(index) {
  const row = rows.value[index];
  row.token = "";
  row.result = "已改为恢复默认，点侧栏「保存配置」后生效。";
  row.ok = true;
  syncStore();
  markDirty();
}

onMounted(() => {
  store.reloadSessions = reloadSessions;
  loadSessions();
});
</script>
