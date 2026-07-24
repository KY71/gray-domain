// 灰域 / Gray Domain — 明暗切換 + 字級記憶（localStorage）
(function () {
  var root = document.documentElement;

  // ----- 主題 -----
  var savedTheme = localStorage.getItem("gd-theme");
  if (savedTheme) root.setAttribute("data-theme", savedTheme);

  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function syncThemeButtons() {
    var dark = currentTheme() === "dark";
    document.querySelectorAll('[data-action="theme"]').forEach(function (b) {
      b.textContent = dark ? "☀" : "☾";
    });
  }
  function toggleTheme() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("gd-theme", next);
    syncThemeButtons();
  }

  // ----- 字級 -----
  var MIN = 0.85, MAX = 1.6, STEP = 0.08;
  var scale = parseFloat(localStorage.getItem("gd-scale")) || 1;
  function applyScale() {
    root.style.setProperty("--reading-scale", scale.toFixed(2));
    localStorage.setItem("gd-scale", scale.toFixed(2));
  }
  applyScale();

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-action]");
    if (!btn) return;
    var action = btn.getAttribute("data-action");
    if (action === "theme") toggleTheme();
    else if (action === "font-inc") { scale = Math.min(MAX, scale + STEP); applyScale(); }
    else if (action === "font-dec") { scale = Math.max(MIN, scale - STEP); applyScale(); }
  });

  syncThemeButtons();
})();
