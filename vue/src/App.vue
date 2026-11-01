<template>
  <div class="layout">
    <aside class="side-nav">
      <div class="brand">
        <h1>会话模型设置</h1>
        <p class="subtitle">为每个会话设置首选模型</p>
      </div>
      <nav class="nav-group">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="nav-item"
          :class="{ active: store.tab === tab.id }"
          @click="store.tab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>
      <div class="nav-foot">
        <div class="actions">
          <button
            type="button"
            class="btn ghost"
            :disabled="store.busy"
            @click="loadAll"
          >
            重新加载
          </button>
          <button
            v-if="store.dirty"
            type="button"
            class="btn ghost"
            :disabled="store.busy"
            @click="loadAll"
          >
            取消编辑
          </button>
          <button
            v-if="store.dirty"
            type="button"
            class="btn primary"
            :disabled="store.busy"
            @click="saveConfig"
          >
            保存配置
          </button>
        </div>
        <div class="version">{{ store.version }}</div>
      </div>
    </aside>
    <main class="content">
      <div v-if="store.alert" class="alert" :class="store.alert.kind">
        <span>{{ store.alert.text }}</span>
        <button type="button" class="close" @click="store.alert = null">×</button>
      </div>
      <CommandTab v-show="store.tab === 'command'" />
      <AdminTab v-show="store.tab === 'admin'" />
      <ModelsTab v-show="store.tab === 'models'" />
      <SessionTab v-show="store.tab === 'session'" />
      <datalist id="provider-list">
        <option v-for="provider in store.providers" :key="provider.id" :value="provider.id">
          {{ provider.model ? provider.id + "（" + provider.model + "）" : provider.id }}
        </option>
      </datalist>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { store, loadAll, saveConfig } from "./store.js";
import CommandTab from "./tabs/CommandTab.vue";
import AdminTab from "./tabs/AdminTab.vue";
import ModelsTab from "./tabs/ModelsTab.vue";
import SessionTab from "./tabs/SessionTab.vue";

const tabs = [
  { id: "command", label: "命令设置" },
  { id: "admin", label: "管理员设置" },
  { id: "models", label: "可用模型设置" },
  { id: "session", label: "会话模型" },
];

onMounted(() => {
  loadAll();
});
</script>
