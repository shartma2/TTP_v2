type DiagramSvgData = {
  sid?: string | null;
  sbd?: { subject: string; svg: string }[];
};

function extractSvgMarkup(raw: string) {
  const start = raw.indexOf("<svg");
  const end = raw.lastIndexOf("</svg>");
  if (start === -1 || end === -1) return raw;
  return raw.slice(start, end + "</svg>".length);
}

function escapeHtml(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function buildDiagramWindowHtml(svgData: DiagramSvgData): string {
  const sidSvgRaw =
    typeof svgData === "object" && svgData && "sid" in svgData
      ? svgData.sid
      : null;

  const sbdRaw =
    typeof svgData === "object" &&
      svgData &&
      "sbd" in svgData &&
      Array.isArray(svgData.sbd)
      ? svgData.sbd
      : [];

  const sidSvg = sidSvgRaw ? extractSvgMarkup(String(sidSvgRaw)) : null;
  const sbdEntries = sbdRaw.map((entry) => ({
    subject: String(entry.subject ?? ""),
    svg: extractSvgMarkup(String(entry.svg ?? "")),
  }));

  return `<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>PASS Diagrams</title>
    <style>
      * { box-sizing: border-box; }
      html, body {
        margin: 0;
        padding: 0;
        background: #111827;
        color: #f3f4f6;
        font-family: Arial, sans-serif;
      }
      body {
        padding: 24px;
      }
      h1 {
        margin: 0 0 24px 0;
        font-size: 28px;
      }
      h2 {
        margin: 0 0 16px 0;
        font-size: 20px;
      }
      .section {
        margin-bottom: 32px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        background: rgba(255,255,255,0.04);
      }
      .toolbar {
        display: flex;
        gap: 8px;
        margin-bottom: 12px;
        flex-wrap: wrap;
      }
      .toolbar button {
        border: 1px solid rgba(255,255,255,0.18);
        background: rgba(255,255,255,0.08);
        color: #f3f4f6;
        border-radius: 10px;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 14px;
      }
      .toolbar button:hover {
        background: rgba(255,255,255,0.14);
      }
      .viewport {
        position: relative;
        height: 75vh;
        min-height: 520px;
        overflow: hidden;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.08);
        cursor: grab;
        user-select: none;
        touch-action: none;
      }
      .viewport.dragging {
        cursor: grabbing;
      }
      .svg-host {
        width: 100%;
        height: 100%;
      }
      .svg-host > svg {
        display: block;
        width: 100%;
        height: 100%;
        background: #ffffff;
      }
      .hint {
        margin-top: 10px;
        font-size: 12px;
        color: #cbd5e1;
      }
    </style>
  </head>
  <body>
    <h1>PASS Diagrams</h1>

    ${sidSvg
      ? `
      <div class="section">
        <h2>SID</h2>
        <div class="toolbar">
          <button type="button" data-action="zoom-in">Zoom in</button>
          <button type="button" data-action="zoom-out">Zoom out</button>
          <button type="button" data-action="fit">Fit</button>
          <button type="button" data-action="reset">Reset</button>
        </div>
        <div class="viewport">
          <div class="svg-host">${sidSvg}</div>
        </div>
        <div class="hint">Mouse wheel to zoom. Drag to move. Fit restores the full diagram view.</div>
      </div>
    `
      : ""
    }

    ${sbdEntries
      .map(
        (entry) => `
      <div class="section">
        <h2>SBD: ${escapeHtml(entry.subject)}</h2>
        <div class="toolbar">
          <button type="button" data-action="zoom-in">Zoom in</button>
          <button type="button" data-action="zoom-out">Zoom out</button>
          <button type="button" data-action="fit">Fit</button>
          <button type="button" data-action="reset">Reset</button>
        </div>
        <div class="viewport">
          <div class="svg-host">${entry.svg}</div>
        </div>
        <div class="hint">Mouse wheel to zoom. Drag to move. Fit restores the full diagram view.</div>
      </div>
    `
      )
      .join("")}

    <script>
      (() => {
        function setupSection(section) {
          const viewport = section.querySelector(".viewport");
          const host = section.querySelector(".svg-host");
          const svg = host ? host.querySelector("svg") : null;
          if (!viewport || !svg) return;

          const zoomInBtn = section.querySelector('[data-action="zoom-in"]');
          const zoomOutBtn = section.querySelector('[data-action="zoom-out"]');
          const fitBtn = section.querySelector('[data-action="fit"]');
          const resetBtn = section.querySelector('[data-action="reset"]');

          const vbAttr = svg.getAttribute("viewBox");
          let initialView;

          if (vbAttr) {
            const parts = vbAttr.trim().split(/\\s+/).map(Number);
            initialView = {
              minX: parts[0],
              minY: parts[1],
              width: parts[2],
              height: parts[3],
            };
          } else {
            const width = svg.viewBox?.baseVal?.width || svg.width?.baseVal?.value || 1000;
            const height = svg.viewBox?.baseVal?.height || svg.height?.baseVal?.value || 800;

            initialView = {
              minX: 0,
              minY: 0,
              width,
              height,
            };
          }

          let view = { ...initialView };
          let dragging = false;
          let startClientX = 0;
          let startClientY = 0;
          let startMinX = 0;
          let startMinY = 0;

          svg.removeAttribute("width");
          svg.removeAttribute("height");
          svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

          function applyView() {
            svg.setAttribute(
              "viewBox",
              view.minX + " " + view.minY + " " + view.width + " " + view.height
            );
          }

          function resetView() {
            view = { ...initialView };
            applyView();
          }

          function fitView() {
            view = { ...initialView };
            applyView();
          }

          function zoomAt(factor, clientX, clientY) {
            const rect = viewport.getBoundingClientRect();
            if (!rect.width || !rect.height) return;

            const px = (clientX - rect.left) / rect.width;
            const py = (clientY - rect.top) / rect.height;

            const nextWidth = view.width * factor;
            const nextHeight = view.height * factor;

            const worldX = view.minX + px * view.width;
            const worldY = view.minY + py * view.height;

            view.minX = worldX - px * nextWidth;
            view.minY = worldY - py * nextHeight;
            view.width = nextWidth;
            view.height = nextHeight;

            applyView();
          }

          viewport.addEventListener("wheel", (e) => {
            e.preventDefault();
            const factor = e.deltaY < 0 ? 0.9 : 1.1;
            zoomAt(factor, e.clientX, e.clientY);
          }, { passive: false });

          viewport.addEventListener("pointerdown", (e) => {
            dragging = true;
            startClientX = e.clientX;
            startClientY = e.clientY;
            startMinX = view.minX;
            startMinY = view.minY;
            viewport.classList.add("dragging");
            viewport.setPointerCapture(e.pointerId);
          });

          viewport.addEventListener("pointermove", (e) => {
            if (!dragging) return;

            const rect = viewport.getBoundingClientRect();
            if (!rect.width || !rect.height) return;

            const dxPx = e.clientX - startClientX;
            const dyPx = e.clientY - startClientY;

            const dxWorld = (dxPx / rect.width) * view.width;
            const dyWorld = (dyPx / rect.height) * view.height;

            view.minX = startMinX - dxWorld;
            view.minY = startMinY - dyWorld;

            applyView();
          });

          function stopDragging(e) {
            if (!dragging) return;
            dragging = false;
            viewport.classList.remove("dragging");
            try {
              viewport.releasePointerCapture(e.pointerId);
            } catch (_) {}
          }

          viewport.addEventListener("pointerup", stopDragging);
          viewport.addEventListener("pointercancel", stopDragging);
          viewport.addEventListener("pointerleave", (e) => {
            if (dragging && e.buttons === 0) stopDragging(e);
          });

          zoomInBtn?.addEventListener("click", () => {
            const rect = viewport.getBoundingClientRect();
            zoomAt(0.9, rect.left + rect.width / 2, rect.top + rect.height / 2);
          });

          zoomOutBtn?.addEventListener("click", () => {
            const rect = viewport.getBoundingClientRect();
            zoomAt(1.1, rect.left + rect.width / 2, rect.top + rect.height / 2);
          });

          fitBtn?.addEventListener("click", fitView);
          resetBtn?.addEventListener("click", resetView);

          applyView();
        }

        document.querySelectorAll(".section").forEach(setupSection);
      })();
    </script>
  </body>
</html>`;
}

export function openDiagramWindow(svgData: DiagramSvgData) {
  const html = buildDiagramWindowHtml(svgData);
  const pageBlob = new Blob([html], { type: "text/html;charset=utf-8" });
  const pageUrl = URL.createObjectURL(pageBlob);
  const newWindow = window.open(pageUrl, "_blank", "noopener,noreferrer");
  if (newWindow) {
    newWindow.addEventListener(
      "load",
      () => {
        URL.revokeObjectURL(pageUrl);
      },
      { once: true }
    );
  } else {
    URL.revokeObjectURL(pageUrl);
  }
}