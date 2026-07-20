"use client";


/**
 * Stream-field block UI for `TowerViewsBlock`.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";

interface ViewItem {
  id: number;
  title: string;
  image_url: string | null;
  image_width: number | null;
  image_height: number | null;
}

interface TowerViewsValue {
  title?: string;
  title_2?: string;
  text?: string;
  penthouses_only?: boolean;
  items?: ViewItem[];
  theme?: { id: number; css_class: string | null } | null;
}

/** Wagtail "tower_views" vista/gallery block. */
export function TowerViewsBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as TowerViewsValue;
  const { title, title_2, text, items = [] } = value;

  const [selectedIndex, setSelectedIndex] = useState(0);
  const [positionX, setPositionX] = useState(0);
  const viewRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef({ active: false, startX: 0, startPos: 0 });

  const selected = items[selectedIndex];

  const resetPositionForItem = useCallback((item: ViewItem | undefined) => {
    const viewEl = viewRef.current;
    if (!viewEl || !item?.image_width || !item.image_height) return;
    const imageViewWidth =
      (viewEl.clientHeight / item.image_height) * item.image_width;
    setPositionX(imageViewWidth * 0.5 + window.innerWidth * 0.5);
  }, []);

  useEffect(() => {
    const update = () => resetPositionForItem(items[selectedIndex]);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, [items, selectedIndex, resetPositionForItem]);

  const selectView = (index: number) => {
    setSelectedIndex(index);
  };

  const onPointerDown = (e: React.PointerEvent) => {
    dragRef.current = { active: true, startX: e.clientX, startPos: positionX };
    viewRef.current?.setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (!dragRef.current.active) return;
    e.preventDefault();
    const dx = dragRef.current.startX - e.clientX;
    dragRef.current.startX = e.clientX;
    setPositionX((prev) => prev - dx * 2);
  };

  const onPointerUp = () => {
    dragRef.current.active = false;
  };

  const pan = (delta: number) => setPositionX((prev) => prev + delta);

  if (!items.length) return null;

  return (
    <div className="tower-views-widget">
      <div className="content">
        {title && (
          <h2 className="title h1">
            {title}
            {title_2 && (
              <>
                <br />
                <span>
                  {title_2.split("\n").map((line, i) => (
                    <span key={i}>
                      {i > 0 && <br />}
                      {line}
                    </span>
                  ))}
                </span>
              </>
            )}
          </h2>
        )}
        {text && (
          <div className="text-center">
            <RichTextRenderer html={text} />
          </div>
        )}

        <div className="level-select">
          <label className="subhead white mobile">See the view from</label>
          <div className="select-container medium">
            <label className="subhead white desktop">See the view from</label>
            <select
              name="select-dropdown"
              value={selectedIndex}
              onChange={(e) => selectView(Number(e.target.value))}
            >
              {items.map((item, i) => (
                <option key={item.id} value={i}>
                  LEVEL {item.title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className={`pano-block${selected?.image_url ? " active" : ""}`}>
        <div
          ref={viewRef}
          className="view"
          style={
            selected?.image_url
              ? {
                  backgroundImage: `url(${formatImageUrl(selected.image_url)})`,
                  backgroundPositionX: `${positionX}px`,
                }
              : undefined
          }
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerLeave={onPointerUp}
        />

        <button
          type="button"
          className="arrow right"
          onClick={() => pan(-100)}
          aria-label="Pan right"
        />
        <button
          type="button"
          className="arrow left"
          onClick={() => pan(100)}
          aria-label="Pan left"
        />
      </div>
    </div>
  );
}
