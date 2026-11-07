import { reactive } from "vue";
import { apiGet, apiPost, pick, bridgeReady } from "./sdk.js";

export const DEFAULT_CONFIG = {
  enable_main_command: true,
  command_prefix: "/",
  command_name: "msto",
  sid_command_prefix: "/",
  sid_command_name: "mstosid",
  enable_sid_command: false,
  list_command_prefix: "/",
  list_command_name: "mstolist",
  list_output_mode: "alias",
  enable_list_command: false,
  curr_command_prefix: "/",
  curr_command_name: "mstom",
  curr_output_mode: "as_set",
  enable_curr_command: false,
  allowed_uids: [],
  models: [],
};

export const store = reactive({
  tab: "command",
  config: JSON.parse(JSON.stringify(DEFAULT_CONFIG)),
  providers: [],
  version: "",
  dirty: false,
  busy: false,
  alert: null,
  /* Session rows owned by SessionTab; saveConfig flushes changed rows. */
  sessionRows: [],
  /* Saved-state snapshot {umo, token} for change detection. */
  sessionSaved: [],
  /* Set by SessionTab so reload paths (重新加载/取消编辑) refresh rows too. */
  reloadSessions: null,
});

export function markDirty() {
  store.dirty = true;
}

export function clearDirty() {
  store.dirty = false;
}

export function showAlert(kind, text) {
  store.alert = { kind, text };
}

export function applyConfig(cfg) {
  const merged = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
  if (cfg && typeof cfg === "object") {
    for (const key of Object.keys(merged)) {
      const value = cfg[key];
      if (value !== undefined && value !== null) merged[key] = value;
    }
    /* Backend persisted defaults for keys the remote schema predates. */
    if (cfg.enable_main_command === undefined) {
      merged.enable_main_command = false;
    }
  }
  store.config = merged;
}

/* Session row snapshot taken by SessionTab whenever rows load or change;
 * saveConfig compares live rows against the saved snapshot to flush only
 * actually-changed rows. */
export function snapshotSessions(rows) {
  store.sessionRows = rows;
}

export function markSessionsSaved() {
  store.sessionSaved = store.sessionRows.map((row) => ({
    umo: row.umo,
    token: row.token,
  }));
}

export function changedSessions() {
  const saved = new Map(
    store.sessionSaved
      .filter((row) => row.umo.trim())
      .map((row) => [row.umo.trim(), row.token]),
  );
  return store.sessionRows.filter((row) => {
    const umo = row.umo.trim();
    if (!umo) return false;
    return saved.get(umo) !== row.token;
  });
}

function normalizeVersion(value) {
  const text = String(value || "").trim();
  return text ? "v" + text.replace(/^v+/i, "") : "";
}

export async function loadAll() {
  store.busy = true;
  try {
    await bridgeReady();
    /* The bridge already unwraps {"status":"ok","data":...} envelopes and
     * throws on {"status":"error",...}; support both shapes defensively. */
    const [configResp, providerResp, versionResp] = await Promise.all([
      apiGet("config").catch(() => null),
      apiGet("providers").catch(() => null),
      apiGet("version").catch(() => null),
    ]);
    const configWrap = pick(configResp);
    const config = configWrap && configWrap.config ? configWrap.config : configWrap;
    if (config && typeof config === "object") {
      applyConfig(config);
    }
    const providerWrap = pick(providerResp);
    if (providerWrap && providerWrap.providers) {
      store.providers = providerWrap.providers;
    }
    const versionWrap = pick(versionResp);
    if (versionWrap && versionWrap.version) {
      store.version = normalizeVersion(versionWrap.version);
    }
    clearDirty();
    store.alert = null;
    if (typeof store.reloadSessions === "function") {
      await store.reloadSessions();
    }
  } finally {
    store.busy = false;
  }
}

export async function saveConfig() {
  store.busy = true;
  try {
    const body = { config: JSON.parse(JSON.stringify(store.config)) };
    const resp = await apiPost("config", body);
    if (resp && resp.status === "error") {
      throw new Error(resp.message || "保存失败。");
    }
    const savedWrap = pick(resp);
    const changes =
      savedWrap && Array.isArray(savedWrap.session_changes)
        ? savedWrap.session_changes
        : [];
    /* Flush session rows changed since the last saved snapshot, mirroring
     * the per-row 应用 button (empty token = reset to default). */
    let flushed = 0;
    for (const row of changedSessions()) {
      const umo = row.umo.trim();
      try {
        const rowResp = await apiPost("session-model", {
          umo,
          token: row.token.trim(),
        });
        if (rowResp && rowResp.status === "error") {
          throw new Error(rowResp.message || "设置错误");
        }
        flushed += 1;
      } catch (rowErr) {
        showAlert(
          "err",
          `会话 ${umo} 保存失败：${rowErr.message || String(rowErr)}`,
        );
      }
    }
    const freshWrap = pick(await apiGet("config"));
    const fresh = freshWrap && freshWrap.config ? freshWrap.config : freshWrap;
    if (fresh && typeof fresh === "object") applyConfig(fresh);
    markSessionsSaved();
    clearDirty();
    const notes = [];
    if (changes.length) notes.push(`已同步 ${changes.length} 个会话。`);
    if (flushed) notes.push(`已应用 ${flushed} 条会话模型设置。`);
    showAlert("ok", notes.length ? `配置已保存。${notes.join("")}` : "配置已保存。");
  } catch (err) {
    showAlert("err", err.message || String(err));
  } finally {
    store.busy = false;
  }
}
