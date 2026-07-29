---
name: openbb-widget-ui
description: Style widget content so it looks native inside OpenBB Workspace. Use when building or fixing an `iframe`, `html`/HtmlViewer, Streamlit, or any custom-rendered widget that draws its own tables, charts, or layout — covers the exact Workspace color palette for light and dark, theme detection, the series color cycle, and the framing mistakes that leave a white box around a widget in dark mode.
---

# OpenBB Workspace widget UI

Content rendered inside a widget by your own HTML/CSS (iframe, HtmlViewer, Streamlit)
does **not** inherit Workspace styling. You have to apply it. These are the exact
values sampled from the real Workspace UI.

A complete, runnable implementation of everything below lives in
[`widget-examples/iframe-native-ui/`](../../../widget-examples/iframe-native-ui/) —
copy `static/openbb-theme.css` and `static/openbb-iframe.js` rather than rewriting them.

## Rule 1 — theme the outermost element first

The single most common mistake. Apply the theme background to `html`, `body`, and
your top-level container — not just to an inner card or chart div. Styling only the
inner element leaves a white frame around the widget in dark mode.

```css
html, body {
  margin: 0;
  width: 100%;
  min-height: 100%;
  background: var(--obb-page-bg);
}
```

Keep the wrapper's own padding small (`8px 12px`). The content should sit close to
the widget's edges, not float inside a large margin.

## Rule 2 — use these colors, exactly

| | Light | Dark |
|---|---|---|
| Page / wrapper / chart background | `#FFFFFF` | `#151518` |
| Table row (odd) | `#FFFFFF` | `#1F1E23` |
| Table row (alternating) | `#F6F6F6` | `#2A2A31` |
| Table header background | `#EBEBED` | `#36363E` |
| Text / axis labels / legend text | `#191D1F` | `#FFFFFF` |
| Gridlines | `#E8E8E9` | `#515153` |

Supporting values: font `Inter`, body/table font-size `12px`, table cell horizontal
padding `7px`. Up/down values use `#57BA6F` / `#D53939`.

## Rule 3 — series palette: fixed 10 colors, identical in both themes

Series use the fixed 10-color palette in order; once exhausted, additional series can use randomly generated colors, unchanged across themes.
Only the chrome around the series changes between themes — the series colors never do.

1. `#5F8ED6` blue
2. `#F2A450` orange
3. `#5D9B5C` green
4. `#61BCDD` cyan
5. `#DECD43` yellow
6. `#8F6BC5` purple
7. `#B5B5B5` gray
8. `#B060A3` magenta
9. `#846430` brown
10. `#DD5F58` red

## Rule 4 — no borders in tables

The real Workspace table has no visible divider lines between rows or columns.
Separation comes from the alternating row fill alone. Use `border-collapse: collapse`
and set no border colors.

## Rule 5 — no in-content title

Workspace renders the widget's `name` in its own title bar above your content. An
`<h1>` repeating it shows the title twice. A short subtitle on its own (e.g.
"illustrative sample data") is fine.

## Rule 6 — legend

A small line swatch (≈12×2px) plus a label in the axis text color, wrapping across
multiple rows when there are many series. No box, no border, no background fill.

## Detecting the active theme

Never hardcode a theme. Workspace delivers it two ways, and a widget should handle
both:

1. **Query string** — every param, including `theme=light|dark`, is appended to the
   iframe URL, so a fresh load already knows its state.
2. **postMessage** — `{ type: "openbb-params-update", params: { theme: "light" } }`
   arrives when the user toggles the theme. Restyle without reloading.

```js
const params = Object.fromEntries(new URLSearchParams(location.search));
const apply = () => {
  document.documentElement.dataset.theme = params.theme === "light" ? "light" : "dark";
};
window.addEventListener("message", (e) => {
  if (e.data?.type === "openbb-params-update") {
    Object.assign(params, e.data.params || {});
    apply();
  }
});
apply();
```

Then define both palettes as CSS variables under `html[data-theme="light"]` and
`html[data-theme="dark"]`, and reference only the variables everywhere else.

## Checklist before shipping

- [ ] No white or unstyled space anywhere around the content in dark mode.
- [ ] Theme read from the workspace context, not hardcoded — verified by toggling.
- [ ] No border lines between table rows or columns.
- [ ] Series colored from the 10-color cycle, in order, unchanged across themes.
- [ ] No heading duplicating the widget's own name.
