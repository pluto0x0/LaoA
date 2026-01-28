async function loadData() {
  if (window.DATA) return window.DATA;
  const res = await fetch("../all_subtitles.min.json", { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load all_subtitles.min.json");
  return await res.json();
}

function app() {
  return {
    loaded: false,
    q: "",
    matchAll: true, // AND / OR
    tokens: [],
    raw: null,
    items: [],
    filtered: [],
    msg: "请输入搜索关键词",

    async init() {
      try {
        this.raw = await loadData();
        this.items = this.flatten(this.raw);
      } catch (e) {
        console.error(e);
        alert(
          "数据加载失败：请检查 DATA 是否内嵌或 all_subtitles.min.json 是否可访问（建议用本地服务器打开）。",
        );
      } finally {
        this.loaded = true;
      }

      // 如果 URL 带 ?q=xxx 自动搜索
      const params = new URLSearchParams(location.search);
      const preset = params.get("q");
      if (preset) {
        this.q = preset;
        this.applyFilter();
      }
    },

    flatten(data) {
      // { BV: [ {time:[s,e], text}, ... ] } -> [{...}]
      const out = [];
      let uid = 0;
      for (const [bv, arr] of Object.entries(data || {})) {
        (arr || []).forEach((x, i) => {
          const start = Number(x.time?.[0] ?? 0);
          const end = Number(x.time?.[1] ?? start);
          const t = Math.max(0, start);
          out.push({
            uid: uid++,
            bv,
            idxInVideo: i,
            start,
            end,
            text: String(x.text ?? ""),
            url: `https://www.bilibili.com/video/${bv}/?t=${t - 1}`,
          });
        });
      }
      return out;
    },

    applyFilter() {
      const q = (this.q || "").trim();
      this.tokens = [];
      this.filtered = [];
      this.msg = "";
      if (q == "") return;
      if (q.length < 2) {
        this.msg = "请输入至少两个字符";
        return;
      }
      this.tokens = q ? q.split(/\s+/).filter(Boolean) : [];
      if (!this.tokens.length) {
        this.filtered = this.items;
        return;
      }
      const toks = this.tokens.map((s) => s.toLowerCase());
      this.filtered = this.items.filter((it) => {
        const hay = it.text.toLowerCase();
        if (this.matchAll) return toks.every((t) => hay.includes(t));
        return toks.some((t) => hay.includes(t));
      });
      if (this.filtered.length === 0) {
        this.msg = "没有匹配结果。";
      }
    },

    fmtTime(sec) {
      // 123.4 -> 00:02:03
      sec = Math.max(0, Math.floor(Number(sec) || 0));
      const h = Math.floor(sec / 3600);
      const m = Math.floor((sec % 3600) / 60);
      const s = sec % 60;
      const pad = (n) => String(n).padStart(2, "0");
      return h > 0 ? `${pad(h)}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
    },

    escapeHtml(s) {
      return s.replace(
        /[&<>"']/g,
        (c) =>
          ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
          })[c],
      );
    },

    highlight(text) {
      // 简单高亮：把 token 变成 <mark>
      const safe = this.escapeHtml(String(text || ""));
      if (!this.tokens.length) return safe;

      // 避免 token 中出现正则特殊字符导致报错
      const esc = (x) => x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const pattern = this.tokens.map(esc).filter(Boolean).join("|");
      if (!pattern) return safe;

      const re = new RegExp(`(${pattern})`, "gi");
      return safe.replace(
        re,
        '<mark class="bg-yellow-200/70 rounded px-1">$1</mark>',
      );
    },

    async copyLink(it) {
      const link = it.url + `#item-${it.uid}`;
      try {
        await navigator.clipboard.writeText(link);
      } catch {
        // 兼容方案
        const ta = document.createElement("textarea");
        ta.value = link;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
    },
  };
}
