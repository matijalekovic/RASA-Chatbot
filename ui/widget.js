(function () {
  if (window.OnePaxChatbotLoaded) return;
  window.OnePaxChatbotLoaded = true;

  var script = document.currentScript;
  var baseUrl = new URL(script.getAttribute("src"), window.location.href).origin;
  var chatUrl = script.dataset.chatUrl || new URL(script.dataset.chatPath || "/", baseUrl).toString();
  var title = script.dataset.title || "1PAX Assistant";
  var openByDefault = script.dataset.open === "true";

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function withEmbedParam(url) {
    var next = new URL(url, window.location.href);
    next.searchParams.set("embed", "1");
    return next.toString();
  }

  var style = document.createElement("style");
  style.textContent = [
    "#onepax-chatbot-widget{position:fixed;right:22px;bottom:22px;z-index:2147483000;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#111}",
    "#onepax-chatbot-panel{position:absolute;right:0;bottom:76px;width:min(390px,calc(100vw - 32px));height:min(650px,calc(100dvh - 116px));overflow:hidden;border:1px solid rgba(20,20,20,.14);border-radius:18px;background:#f5f4f2;box-shadow:0 24px 80px rgba(0,0,0,.26);opacity:0;transform:translateY(14px) scale(.98);pointer-events:none;transition:opacity .18s ease,transform .18s ease}",
    "#onepax-chatbot-widget.is-open #onepax-chatbot-panel{opacity:1;transform:translateY(0) scale(1);pointer-events:auto}",
    "#onepax-chatbot-head{height:44px;display:flex;align-items:center;justify-content:space-between;padding:0 10px 0 14px;background:#fff;border-bottom:1px solid rgba(20,20,20,.1)}",
    "#onepax-chatbot-title{font-size:13px;font-weight:650;letter-spacing:.02em}",
    "#onepax-chatbot-close,#onepax-chatbot-launcher{border:0;background:#111;color:#fff;cursor:pointer;font:inherit}",
    "#onepax-chatbot-close{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;background:transparent;color:#111}",
    "#onepax-chatbot-close:hover{background:#f0efec}",
    "#onepax-chatbot-frame{width:100%;height:calc(100% - 44px);border:0;display:block;background:#f5f4f2}",
    "#onepax-chatbot-launcher{width:58px;height:58px;border-radius:50%;display:grid;place-items:center;box-shadow:0 16px 38px rgba(0,0,0,.24);transition:transform .16s ease,box-shadow .16s ease}",
    "#onepax-chatbot-launcher:hover{transform:translateY(-2px);box-shadow:0 18px 44px rgba(0,0,0,.28)}",
    "#onepax-chatbot-launcher svg{width:25px;height:25px}",
    "#onepax-chatbot-launcher .close-icon{display:none}",
    "#onepax-chatbot-widget.is-open #onepax-chatbot-launcher .chat-icon{display:none}",
    "#onepax-chatbot-widget.is-open #onepax-chatbot-launcher .close-icon{display:block}",
    "@media (max-width:600px){#onepax-chatbot-widget{right:14px;bottom:14px}#onepax-chatbot-panel{position:fixed;left:10px;right:10px;bottom:84px;width:auto;height:min(680px,calc(100dvh - 104px));border-radius:16px}#onepax-chatbot-launcher{width:56px;height:56px}}"
  ].join("");

  var root = document.createElement("div");
  var safeTitle = escapeHtml(title);
  root.id = "onepax-chatbot-widget";
  root.innerHTML =
    '<section id="onepax-chatbot-panel" role="dialog" aria-label="' + safeTitle + '">' +
      '<div id="onepax-chatbot-head">' +
        '<div id="onepax-chatbot-title">' + safeTitle + '</div>' +
        '<button id="onepax-chatbot-close" type="button" aria-label="Close 1PAX assistant">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>' +
        '</button>' +
      '</div>' +
      '<iframe id="onepax-chatbot-frame" title="' + safeTitle + '" src="' + withEmbedParam(chatUrl) + '" loading="lazy"></iframe>' +
    '</section>' +
    '<button id="onepax-chatbot-launcher" type="button" aria-label="Open 1PAX assistant">' +
      '<svg class="chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true"><path d="M21 11.5a8.5 8.5 0 0 1-8.9 8.49 9.6 9.6 0 0 1-4.4-1.24L3 20l1.25-4.18A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8 10h8M8 14h5"/></svg>' +
      '<svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>' +
    '</button>';

  function setOpen(open) {
    root.classList.toggle("is-open", open);
    root.querySelector("#onepax-chatbot-launcher").setAttribute(
      "aria-label",
      open ? "Close 1PAX assistant" : "Open 1PAX assistant"
    );
  }

  document.head.appendChild(style);
  document.body.appendChild(root);

  root.querySelector("#onepax-chatbot-launcher").addEventListener("click", function () {
    setOpen(!root.classList.contains("is-open"));
  });
  root.querySelector("#onepax-chatbot-close").addEventListener("click", function () {
    setOpen(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") setOpen(false);
  });

  setOpen(openByDefault);
})();
