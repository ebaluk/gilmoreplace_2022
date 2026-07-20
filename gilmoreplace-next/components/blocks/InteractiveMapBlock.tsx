"use client";


/**
 * Stream-field block UI for `InteractiveMapBlock`.
 */
import { useRef, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import { themeClassName, type ResolvedTheme } from "@/lib/theme";

interface MapPoint {
  title: string;
  body: string;
  style?: string;
  left?: number;
  top?: number;
  idx?: number;
}

interface ResolvedMap {
  layout_image: { url: string; alt: string; width: number; height: number };
  points?: MapPoint[];
  layout_image_points?: MapPoint[];
}

interface InteractiveMapValue {
  title?: string;
  mobile_title?: string;
  show_legend?: boolean;
  resolved_map?: ResolvedMap;
  interactive_map?: ResolvedMap | number;
  theme?: ResolvedTheme | number | null;
}

function normalizeMapData(value: InteractiveMapValue): ResolvedMap | null {
  const source =
    value.resolved_map ||
    (typeof value.interactive_map === "object" ? value.interactive_map : null);

  if (!source?.layout_image) return null;

  const rawPoints = source.points || source.layout_image_points || [];
  const points = rawPoints.map((point, index) => ({
    ...point,
    idx: point.idx ?? index + 1,
    style:
      point.style ||
      (point.left != null && point.top != null
        ? `left: ${point.left}%; top: ${point.top}%;`
        : ""),
  }));

  return {
    layout_image: source.layout_image,
    points,
  };
}

/** Wagtail "interactive_map" site plan with legend points. */
export function InteractiveMapBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as InteractiveMapValue;
  const { title, mobile_title, show_legend, theme } = value;

  const mapData = normalizeMapData(value);
  const [activeIdx, setActiveIdx] = useState<number | null>(null);
  const [mobileActiveIdx, setMobileActiveIdx] = useState<number | null>(null);
  const [panOverlayVisible, setPanOverlayVisible] = useState(true);
  const overflowRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  if (!mapData) return null;

  const image = mapData.layout_image;
  const points = mapData.points || [];

  const dismissPanOverlay = () => setPanOverlayVisible(false);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!overflowRef.current) return;
    dismissPanOverlay();
    setIsDragging(true);
    setStartX(e.pageX - overflowRef.current.offsetLeft);
    setScrollLeft(overflowRef.current.scrollLeft);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !overflowRef.current) return;
    e.preventDefault();
    const x = e.pageX - overflowRef.current.offsetLeft;
    overflowRef.current.scrollLeft = scrollLeft - (x - startX) * 2;
  };

  const handleMobileHotspotClick = (index: number) => {
    dismissPanOverlay();
    setMobileActiveIdx(index);
  };

  return (
    <article className={`sitemap-section ${themeClassName(theme)}`.trim()}>
      {title && !show_legend && (
        <h2 className="subhead white main h3">
          {mobile_title ? (
            <>
              <span className="desktop">{title}</span>
              <span className="mobile">{mobile_title}</span>
            </>
          ) : (
            title
          )}
        </h2>
      )}

      <div className="sitemap-desktop">
        {points.map((item, i) => (
          <div
            key={item.idx ?? i}
            className={`hotspot${activeIdx === i ? " active" : ""}`}
            style={parseStyle(item.style ?? "")}
            data-idx={i + 1}
            onMouseEnter={() => setActiveIdx(i)}
            onMouseLeave={() => setActiveIdx(null)}
          >
            {i + 1}
            <span className="sr-only">{item.title}</span>
          </div>
        ))}

        <div className="callouts desktop">
          {points.map((item, i) => (
            <div
              key={item.idx ?? i}
              className={`callout${activeIdx === i ? " active" : ""}`}
              style={{ ...parseStyle(item.style ?? ""), marginTop: 50 }}
              data-idx={i + 1}
            >
              <h3 className="subhead underline white">{item.title}</h3>
              <div dangerouslySetInnerHTML={{ __html: item.body }} />
            </div>
          ))}
        </div>

        <img src={formatImageUrl(image.url)} alt={image.alt} />
        <div className={`overlay${activeIdx !== null ? " active" : ""}`} />
      </div>

      <div className="sitemap-mobile mobile">
        <div
          className="pan-mobile"
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onMouseMove={handleMouseMove}
        >
          <div className="overflow-wrapper" ref={overflowRef}>
            <div className="image-container" draggable={false}>
              <img src={formatImageUrl(image.url)} alt={image.alt} draggable={false} />
              {points.map((item, i) => (
                <div
                  key={item.idx ?? i}
                  className={`hotspot-mobile${mobileActiveIdx === i ? " active" : ""}`}
                  style={parseStyle(item.style ?? "")}
                  data-idx={i + 1}
                  onClick={() => handleMobileHotspotClick(i)}
                >
                  {i + 1}
                  <span className="sr-only">{item.title}</span>
                </div>
              ))}
            </div>
          </div>
          <div
            className={`mobile-callout${mobileActiveIdx !== null ? " active" : ""}`}
            onClick={() => setMobileActiveIdx(null)}
          >
            <div>
              {mobileActiveIdx !== null && points[mobileActiveIdx] && (
                <>
                  <h3 className="subhead underline white">
                    {points[mobileActiveIdx].title}
                  </h3>
                  <div
                    dangerouslySetInnerHTML={{ __html: points[mobileActiveIdx].body }}
                  />
                </>
              )}
            </div>
          </div>
          <div
            className={`overlay${panOverlayVisible ? " active" : ""}`}
            onClick={dismissPanOverlay}
            onTouchStart={dismissPanOverlay}
          >
            <div className="swipe-indicator">
              <img
                src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iNDdweCIgaGVpZ2h0PSIzOHB4IiB2aWV3Qm94PSIwIDAgNDcgMzgiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CiAgICA8IS0tIEdlbmVyYXRvcjogU2tldGNoIDQ4LjIgKDQ3MzI3KSAtIGh0dHA6Ly93d3cuYm9oZW1pYW5jb2RpbmcuY29tL3NrZXRjaCAtLT4KICAgIDx0aXRsZT5Hcm91cCA2PC90aXRsZT4KICAgIDxkZXNjPkNyZWF0ZWQgd2l0aCBTa2V0Y2guPC9kZXNjPgogICAgPGRlZnM+PC9kZWZzPgogICAgPGcgaWQ9Ik0tRElTQ09WRVItVklTSU9OIiBzdHJva2U9Im5vbmUiIHN0cm9rZS13aWR0aD0iMSIgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtNTYuMDAwMDAwLCAtMTM0Mi4wMDAwMDApIj4KICAgICAgICA8ZyBpZD0iR3JvdXAtOCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNTguMDAwMDAwLCAxMzQzLjAwMDAwMCkiIHN0cm9rZT0iI0ZGRkZGRiIgc3Ryb2tlLXdpZHRoPSIyIj4KICAgICAgICAgICAgPGcgaWQ9Ikdyb3VwLTYiPgogICAgICAgICAgICAgICAgPHBhdGggZD0iTTEzLDE4IEw0NSwxOCIgaWQ9IlBhdGgtOCIgc3Ryb2tlLWRhc2hhcnJheT0iMiwzIj48L3BhdGg+CiAgICAgICAgICAgICAgICA8cG9seWxpbmUgaWQ9IlRyaWFuZ2xlLTMtQ29weSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoOS4wMDAwMDAsIDE4LjAwMDAwMCkgc2NhbGUoLTEsIDEpIHRyYW5zbGF0ZSgtOS4wMDAwMDAsIC0xOC4wMDAwMDApICIgcG9pbnRzPSIwIDAgMTggMTggMCAzNiI+PC9wb2x5bGluZT4KICAgICAgICAgICAgPC9nPgogICAgICAgIDwvZz4KICAgIDwvZz4KPC9zdmc+"
                alt=""
              />
              <h3 className="subhead white">Pan to view site map</h3>
              <img
                src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iNDdweCIgaGVpZ2h0PSIzOHB4IiB2aWV3Qm94PSIwIDAgNDcgMzgiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CiAgICA8IS0tIEdlbmVyYXRvcjogU2tldGNoIDQ4LjIgKDQ3MzI3KSAtIGh0dHA6Ly93d3cuYm9oZW1pYW5jb2RpbmcuY29tL3NrZXRjaCAtLT4KICAgIDx0aXRsZT5Hcm91cCA2IENvcHk8L3RpdGxlPgogICAgPGRlc2M+Q3JlYXRlZCB3aXRoIFNrZXRjaC48L2Rlc2M+CiAgICA8ZGVmcz48L2RlZnM+CiAgICA8ZyBpZD0iTS1ESVNDT1ZFUi1WSVNJT04iIHN0cm9rZT0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIxIiBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC0yNzIuMDAwMDAwLCAtMTM0Mi4wMDAwMDApIj4KICAgICAgICA8ZyBpZD0iR3JvdXAtOCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNTguMDAwMDAwLCAxMzQzLjAwMDAwMCkiIHN0cm9rZT0iI0ZGRkZGRiIgc3Ryb2tlLXdpZHRoPSIyIj4KICAgICAgICAgICAgPGcgaWQ9Ikdyb3VwLTYtQ29weSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMjM2LjUwMDAwMCwgMTguMDAwMDAwKSBzY2FsZSgtMSwgMSkgdHJhbnNsYXRlKC0yMzYuNTAwMDAwLCAtMTguMDAwMDAwKSB0cmFuc2xhdGUoMjE0LjAwMDAwMCwgMC4wMDAwMDApIj4KICAgICAgICAgICAgICAgIDxwYXRoIGQ9Ik0xMywxOCBMNDUsMTgiIGlkPSJQYXRoLTgiIHN0cm9rZS1kYXNoYXJyYXk9IjIsMyI+PC9wYXRoPgogICAgICAgICAgICAgICAgPHBvbHlsaW5lIGlkPSJUcmlhbmdsZS0zLUNvcHkiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDkuMDAwMDAwLCAxOC4wMDAwMDApIHNjYWxlKC0xLCAxKSB0cmFuc2xhdGUoLTkuMDAwMDAwLCAtMTguMDAwMDAwKSAiIHBvaW50cz0iMCAwIDE4IDE4IDAgMzYiPjwvcG9seWxpbmU+CiAgICAgICAgICAgIDwvZz4KICAgICAgICA8L2c+CiAgICA8L2c+Cjwvc3ZnPg=="
                alt=""
              />
            </div>
          </div>
        </div>
      </div>

      {show_legend && title && (
        <div className={`interactive-map-legend${points.length > 12 ? " two-columns" : ""}`}>
          <h2 className="subhead white h3">{title}</h2>
          <ul>
            {points.map((item, i) => (
              <li key={item.idx ?? i} value={item.idx}>
                <span className="num">{i + 1}</span>
                <span className="cat">{item.title}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}

function parseStyle(style: string): React.CSSProperties {
  if (!style) return {};
  const obj: React.CSSProperties = {};
  style.split(";").forEach((s) => {
    const [key, val] = s.split(":").map((v) => v.trim());
    if (key && val) {
      const cssKey = key.replace(/-([a-z])/g, (_, c) => c.toUpperCase()) as keyof React.CSSProperties;
      (obj as Record<string, string>)[cssKey as string] = val;
    }
  });
  return obj;
}
