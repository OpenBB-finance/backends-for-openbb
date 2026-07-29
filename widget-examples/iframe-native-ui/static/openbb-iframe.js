/*
 * Minimal helper for `type: "iframe"` widgets in OpenBB Workspace.
 *
 * Workspace talks to an iframe widget in two ways, and this file handles both:
 *
 *   1. Query string  — every param (including `theme`) is appended to the iframe
 *                      URL, so a fresh load already knows its state.
 *   2. postMessage   — `{ type: "openbb-params-update", params }` arrives when a
 *                      param or the theme changes.
 *
 * Outbound, the page can:
 *   - announce itself with `openbb-connect` (manifest + param defs). The manifest
 *     exposes the widget's data to the AI copilot; the param defs render controls
 *     in the widget navbar.
 *   - answer `openbb-request` with `openbb-data` (that's the copilot asking).
 *   - push a param back with `openbb:widget-params:update`, which Workspace
 *     persists and forwards to every widget grouped on that param.
 */
(function () {
  const parentWindow = window.top || window.parent;

  // Fixed 10-color series palette — identical in light and dark, cycles past 10.
  const PALETTE = [
    "#5F8ED6", "#F2A450", "#5D9B5C", "#61BCDD", "#DECD43",
    "#8F6BC5", "#B5B5B5", "#B060A3", "#846430", "#DD5F58",
  ];

  const params = Object.fromEntries(new URLSearchParams(window.location.search));
  const paramListeners = [];
  let requestHandler = null;
  let manifest = null;

  function applyTheme() {
    document.documentElement.dataset.theme = params.theme === "light" ? "light" : "dark";
  }

  function notify() {
    applyTheme();
    for (const cb of paramListeners) cb(params);
  }

  window.addEventListener("message", (event) => {
    const msg = event.data;
    if (!msg || !msg.type) return;

    if (msg.type === "openbb-params-update") {
      Object.assign(params, msg.params || {});
      notify();
      return;
    }

    if (msg.type === "openbb-request" && requestHandler) {
      const widgetId = msg.widgetId || (manifest && manifest[0] && manifest[0].widgetId);
      try {
        const payload = requestHandler(widgetId);
        parentWindow.postMessage({ type: "openbb-data", widgetId, ...payload }, "*");
      } catch (err) {
        parentWindow.postMessage(
          { type: "openbb-error", widgetId, error: String(err) },
          "*",
        );
      }
    }
  });

  const OpenBB = {
    PALETTE,
    params,

    /** Register a callback run once now and again on every param/theme change. */
    onParams(cb) {
      paramListeners.push(cb);
      cb(params);
    },

    /** Answer copilot data requests: `cb(widgetId)` -> `{ dataType, data, columns }`. */
    onRequest(cb) {
      requestHandler = cb;
    },

    /**
     * Handshake. `widgets` is the copilot-visible manifest, `paramDefs` renders
     * controls in the widget navbar. Re-sent a couple of times because the page
     * can finish loading before Workspace has its listener attached.
     */
    connect({ widgets = [], paramDefs = [] } = {}) {
      manifest = widgets;
      const send = () =>
        parentWindow.postMessage(
          { type: "openbb-connect", widgets, params: paramDefs },
          "*",
        );
      send();
      setTimeout(send, 300);
      setTimeout(send, 1200);
    },

    /** Push a param back to Workspace (drives any widget group synced on it). */
    setParam(paramName, value) {
      params[paramName] = String(value);
      parentWindow.postMessage(
        { type: "openbb:widget-params:update", paramName, value },
        "*",
      );
      notify();
    },
  };

  applyTheme();
  window.OpenBB = OpenBB;
})();
