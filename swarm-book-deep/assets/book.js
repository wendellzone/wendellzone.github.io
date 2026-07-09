/* =========================================================================
   Swarm 图文电子书 · 交互脚本
   - 侧边栏当前章高亮
   - 顶部阅读进度条
   - 代码块一键复制
   - 移动端菜单开合
   - 键盘左右方向键翻章
   ========================================================================= */
(function () {
  "use strict";

  /* ---------- 1. 侧边栏当前章高亮 ---------- */
  function highlightCurrent() {
    var here = location.pathname.split("/").pop() || "index.html";
    var links = document.querySelectorAll(".sidebar nav a");
    links.forEach(function (a) {
      var href = a.getAttribute("href");
      if (href === here) {
        a.classList.add("active");
        // 滚动到可见
        a.scrollIntoView({ block: "nearest" });
      }
    });
  }

  /* ---------- 2. 阅读进度条 ---------- */
  function initProgress() {
    var bar = document.getElementById("progress-bar");
    if (!bar) return;
    function update() {
      var h = document.documentElement;
      var scrolled = h.scrollTop || document.body.scrollTop;
      var height = h.scrollHeight - h.clientHeight;
      var pct = height > 0 ? (scrolled / height) * 100 : 0;
      bar.style.width = pct + "%";
    }
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  /* ---------- 3. 代码块一键复制 ---------- */
  function initCopy() {
    document.querySelectorAll(".code-block").forEach(function (block) {
      var btn = block.querySelector(".copy-btn");
      var code = block.querySelector("pre code");
      if (!btn || !code) return;
      btn.addEventListener("click", function () {
        var text = code.innerText;
        navigator.clipboard.writeText(text).then(function () {
          var old = btn.textContent;
          btn.textContent = "已复制 ✓";
          btn.classList.add("copied");
          setTimeout(function () {
            btn.textContent = old;
            btn.classList.remove("copied");
          }, 1600);
        });
      });
    });
  }

  /* ---------- 4. 移动端菜单 ---------- */
  function initMenu() {
    var toggle = document.querySelector(".menu-toggle");
    var sidebar = document.querySelector(".sidebar");
    var scrim = document.querySelector(".scrim");
    if (!toggle || !sidebar) return;
    function close() { sidebar.classList.remove("open"); }
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
    if (scrim) scrim.addEventListener("click", close);
    sidebar.querySelectorAll("nav a").forEach(function (a) {
      a.addEventListener("click", close);
    });
  }

  /* ---------- 5. 键盘翻章 ---------- */
  function initKeyboard() {
    document.addEventListener("keydown", function (e) {
      if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
      var prev = document.querySelector(".chapter-nav a.prev:not(.disabled)");
      var next = document.querySelector(".chapter-nav a.next:not(.disabled)");
      if (e.key === "ArrowLeft" && prev) location.href = prev.getAttribute("href");
      if (e.key === "ArrowRight" && next) location.href = next.getAttribute("href");
    });
  }

  /* ---------- 6. highlight.js ---------- */
  function initHighlight() {
    if (window.hljs) {
      document.querySelectorAll("pre code").forEach(function (el) {
        window.hljs.highlightElement(el);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    highlightCurrent();
    initProgress();
    initCopy();
    initMenu();
    initKeyboard();
    initHighlight();
  });
})();
