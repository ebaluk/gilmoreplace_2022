"use client";


/**
 * Stream-field block UI for `InteractiveMapTabsBlock`.
 */
import { useState, type MouseEvent } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { InteractiveMapBlock } from "@/components/blocks/InteractiveMapBlock";
import { normalizeTheme } from "@/lib/theme";

interface TabMapValue {
  title?: string;
  tab_name?: string;
  show_legend?: boolean;
  full_width?: boolean;
  interactive_map?: number;
  theme?: number | { id: number; css_class: string | null } | null;
  resolved_map?: {
    id?: number;
    title?: string;
    layout_image?: { url: string; alt: string; width: number; height: number };
    points?: unknown[];
    layout_image_points?: unknown[];
  };
}

interface TabsValue {
  maps?: TabMapValue[];
  resolved_maps?: TabMapValue[];
}

function toMapBlock(parentId: string, map: TabMapValue, index: number): StreamFieldBlock {
  return {
    id: `${parentId}-tab-${index}`,
    type: "interactive_map",
    value: {
      title: map.title,
      show_legend: map.show_legend,
      resolved_map: map.resolved_map,
      interactive_map: map.interactive_map,
      theme: normalizeTheme(map.theme),
    },
  };
}

/** Wagtail "interactive_map_tabs" tabbed site maps. */
export function InteractiveMapTabsBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as TabsValue;
  const maps = value.resolved_maps ?? value.maps ?? [];
  const [activeTab, setActiveTab] = useState(0);

  if (!maps.length) return null;

  const handleTabClick = (e: MouseEvent, index: number) => {
    e.preventDefault();
    setActiveTab(index);
  };

  return (
    <article className="amenity-tabs-block">
      <ul className="nav nav-tabs" role="tablist">
        {maps.map((map, index) => {
          const mapId = map.resolved_map?.id ?? map.interactive_map ?? index;
          const label = map.tab_name || map.title || `Tab ${index + 1}`;
          return (
            <li
              key={`tab-${mapId}`}
              role="presentation"
              className={index === activeTab ? "active" : ""}
            >
              <a
                href={`#map-${mapId}`}
                role="tab"
                aria-controls={`map-${mapId}`}
                aria-selected={index === activeTab}
                onClick={(e) => handleTabClick(e, index)}
              >
                {label}
              </a>
            </li>
          );
        })}
      </ul>

      <div className="tab-content">
        {maps.map((map, index) => {
          const mapId = map.resolved_map?.id ?? map.interactive_map ?? index;
          return (
            <div
              key={`pane-${mapId}`}
              role="tabpanel"
              className={`tab-pane${index === activeTab ? " active" : ""}`}
              id={`map-${mapId}`}
            >
              <InteractiveMapBlock block={toMapBlock(block.id, map, index)} />
            </div>
          );
        })}
      </div>
    </article>
  );
}
