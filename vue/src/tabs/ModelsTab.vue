<template>
  <section class="tab-panel">
    <div class="panel-head">
      <h2>可用模型设置</h2>
      <button type="button" class="btn tonal sm" @click="addModel">+ 添加模型</button>
    </div>
    <p class="hint">
      选择主命令可用的模型（来自 AstrBot 提供商配置），可设置别名；未设置别名的模型直接用模型 ID（提供商 ID）切换。列表命令仅显示已启用的条目。
    </p>
    <div v-if="models.length === 0" class="empty">暂无模型，点击右上角「+ 添加模型」。</div>
    <div
      v-for="(model, index) in models"
      :key="model.__template_key || 'm-' + index"
      class="model-card"
      draggable="true"
      :class="{ 'dragging': dragIndex === index, 'drop-target': dropIndex === index && dragIndex !== index }"
      @dragstart="onDragStart(index, $event)"
      @dragover.prevent="onDragOver(index)"
      @dragend="onDragEnd"
      @drop.prevent="onDrop(index)"
    >
      <div class="model-head">
        <span class="drag-handle" title="拖动排序" aria-hidden="true">⋮⋮</span>
        <label class="switch-row grow">
          <input
            type="checkbox"
            :checked="model.enabled !== false"
            @change="setEnabled(index, $event)"
          >
          <span>启用</span>
        </label>
        <button type="button" class="btn danger-text sm" @click="removeModel(index)">删除</button>
      </div>
      <div class="model-grid">
        <div class="field">
          <label :for="'model-alias-' + index">别名</label>
          <input
            :id="'model-alias-' + index"
            v-model="model.alias"
            type="text"
            placeholder="别名，如 glm"
            @input="markDirty"
          >
        </div>
        <div class="field">
          <label :for="'model-pid-' + index">模型 ID（提供商 ID）</label>
          <input
            :id="'model-pid-' + index"
            v-model="model.provider_id"
            type="text"
            list="provider-list"
            placeholder="AstrBot 提供商 ID（即模型 ID）"
            @input="markDirty"
          >
        </div>
      </div>
      <label class="switch-row public-row">
        <input
          type="checkbox"
          :checked="model.public === true"
          @change="setPublic(index, $event)"
        >
        <span>允许非管理员选择</span>
      </label>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import { store, markDirty } from "../store.js";
const models = computed(() => store.config.models);
const dragIndex = ref(-1);
const dropIndex = ref(-1);

function onDragStart(index, event) {
  dragIndex.value = index;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", String(index));
}

function onDragOver(index) {
  dropIndex.value = index;
}

function onDrop(index) {
  const from = dragIndex.value;
  if (from < 0 || from === index) {
    onDragEnd();
    return;
  }
  const moved = models.value.splice(from, 1)[0];
  models.value.splice(index, 0, moved);
  markDirty();
  onDragEnd();
}

function onDragEnd() {
  dragIndex.value = -1;
  dropIndex.value = -1;
}

function nextKey() {
  const keys = models.value.map((item) => Number(item.__template_key) || 0);
  return (keys.length ? Math.max(...keys) : 0) + 1;
}

function addModel() {
  models.value.push({
    __template_key: nextKey(),
    alias: "",
    provider_id: "",
    enabled: true,
    public: false,
  });
  markDirty();
}

function removeModel(index) {
  models.value.splice(index, 1);
  markDirty();
}

function setEnabled(index, event) {
  models.value[index].enabled = event.target.checked;
  markDirty();
}

function setPublic(index, event) {
  models.value[index].public = event.target.checked;
  markDirty();
}
</script>
