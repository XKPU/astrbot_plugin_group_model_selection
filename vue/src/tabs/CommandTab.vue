<template>
  <section class="tab-panel">
    <div class="panel-head">
      <h2>命令设置</h2>
    </div>
    <p class="hint">
      主命令设置会话首选模型，无参数时清除该会话的独立模型配置；关闭主命令后仅能在配置页设置会话模型（适用于 UID（发送者 ID）可能无法唯一标记或被伪造的平台）。其余命令可选启用，命令前缀与命令名均可自定义。
    </p>
    <label class="switch-row">
      <input type="checkbox" v-model="store.config.enable_main_command" @change="markDirty">
      <span>启用主命令（关闭后仅可在配置页设置会话模型）</span>
    </label>
    <div class="grid-2">
      <div class="field">
        <label for="command_prefix">主命令前缀</label>
        <input id="command_prefix" v-model="store.config.command_prefix" type="text" placeholder="/" @input="markDirty">
      </div>
      <div class="field">
        <label for="command_name">主命令名</label>
        <input id="command_name" v-model="store.config.command_name" type="text" placeholder="msto" @input="markDirty">
      </div>
      <div class="field">
        <label for="sid_command_prefix">查询命令前缀</label>
        <input id="sid_command_prefix" v-model="store.config.sid_command_prefix" type="text" placeholder="/" @input="markDirty">
      </div>
      <div class="field">
        <label for="sid_command_name">查询命令名</label>
        <input id="sid_command_name" v-model="store.config.sid_command_name" type="text" placeholder="mstosid" @input="markDirty">
      </div>
      <div class="field">
        <label for="list_command_prefix">列表命令前缀</label>
        <input id="list_command_prefix" v-model="store.config.list_command_prefix" type="text" placeholder="/" @input="markDirty">
      </div>
      <div class="field">
        <label for="list_command_name">列表命令名</label>
        <input id="list_command_name" v-model="store.config.list_command_name" type="text" placeholder="mstolist" @input="markDirty">
      </div>
      <div class="field">
        <label for="curr_command_prefix">当前模型命令前缀</label>
        <input id="curr_command_prefix" v-model="store.config.curr_command_prefix" type="text" placeholder="/" @input="markDirty">
      </div>
      <div class="field">
        <label for="curr_command_name">当前模型命令名</label>
        <input id="curr_command_name" v-model="store.config.curr_command_name" type="text" placeholder="mstom" @input="markDirty">
      </div>
      <div class="field">
        <label for="list_output_mode">列表输出方式</label>
        <select id="list_output_mode" v-model="store.config.list_output_mode" @change="markDirty">
          <option value="alias">仅别名</option>
          <option value="id">仅 ID</option>
          <option value="both">别名 + ID</option>
        </select>
      </div>
      <div class="field">
        <label for="curr_output_mode">当前模型输出方式</label>
        <select id="curr_output_mode" v-model="store.config.curr_output_mode" @change="markDirty">
          <option value="as_set">跟随设置时</option>
          <option value="alias">仅别名</option>
          <option value="id">仅 ID</option>
          <option value="both">别名 + ID</option>
        </select>
      </div>
    </div>
    <label class="switch-row">
      <input type="checkbox" v-model="store.config.enable_sid_command" @change="markDirty">
      <span>启用会话查询命令（/mstosid）（查询 UMO（会话 ID）与 UID（发送者 ID），UID 供填入管理员白名单）</span>
    </label>
    <label class="switch-row">
      <input type="checkbox" v-model="store.config.enable_list_command" @change="markDirty">
      <span>启用列表命令（查看可用模型列表）</span>
    </label>
    <label class="switch-row">
      <input type="checkbox" v-model="store.config.enable_curr_command" @change="markDirty">
      <span>启用当前模型命令（查看当前会话模型）</span>
    </label>
    <div class="preview">
      <div v-for="line in previewLines" :key="line" class="preview-line">{{ line }}</div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { store, markDirty } from "../store.js";

const previewLines = computed(() => {
  const cfg = store.config;
  const prefix = String(cfg.command_prefix || "/").trim() || "/";
  const lines = [];
  if (cfg.enable_main_command !== false) {
    lines.push(
      `${prefix}${String(cfg.command_name || "msto").trim() || "msto"} <别名或模型 ID>`,
    );
    lines.push(
      `${prefix}${String(cfg.command_name || "msto").trim() || "msto"}（清除会话模型设置）`,
    );
  }
  if (cfg.enable_sid_command) {
    const sidPrefix = String(cfg.sid_command_prefix || "/").trim() || "/";
    const sidName = String(cfg.sid_command_name || "mstosid").trim() || "mstosid";
    lines.push(`${sidPrefix}${sidName}`);
  }
  if (cfg.enable_list_command) {
    const listPrefix = String(cfg.list_command_prefix || "/").trim() || "/";
    const listName = String(cfg.list_command_name || "mstolist").trim() || "mstolist";
    lines.push(`${listPrefix}${listName}`);
  }
  if (cfg.enable_curr_command) {
    const currPrefix = String(cfg.curr_command_prefix || "/").trim() || "/";
    const currName = String(cfg.curr_command_name || "mstom").trim() || "mstom";
    lines.push(`${currPrefix}${currName}`);
  }
  return lines;
});
</script>
