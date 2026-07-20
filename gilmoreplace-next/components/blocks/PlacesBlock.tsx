"use client";


/**
 * Stream-field block UI for `PlacesBlock`.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { PLACES_MAP_STYLES } from "@/lib/googleMapStyles";

interface PlaceItem {
  title: string;
  latitude: string;
  longitude: string;
  address?: string;
  url?: string;
}

interface PlaceGroup {
  id: number;
  title: string;
  color: string;
  places: { type: string; value: PlaceItem }[];
}

interface PlacesValue {
  title?: string;
  resolved_instance?: {
    latitude: string;
    longitude: string;
    place_groups: PlaceGroup[];
  };
  google_maps_api_key?: string;
}

interface PlaceMarkerEntry {
  marker: google.maps.Marker;
  groupId: number;
  place: PlaceItem;
}

const DEFAULT_ZOOM = 16;
const MAIN_MARKER_ICON = "/images/marker-main.svg";

function loadGoogleMaps(apiKey: string): Promise<void> {
  if (typeof window === "undefined") return Promise.resolve();
  if (window.google?.maps) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      'script[src*="maps.googleapis.com/maps/api/js"]'
    );
    if (existing) {
      const done = () => resolve();
      existing.addEventListener("load", done);
      if (window.google?.maps) done();
      return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}`;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Google Maps failed to load"));
    document.head.appendChild(script);
  });
}

function categoryMarkerIcon(color: string): google.maps.Symbol {
  return {
    path: "M0 0 L22 0 L22 22 L0 22 Z",
    fillColor: "#611120",
    fillOpacity: 0,
    scale: 1.3,
    strokeColor: color,
    strokeWeight: 4,
  };
}

function infoWindowContent(place: PlaceItem): string {
  let content = `<h4>${place.title}</h4>`;
  if (place.address) content += `<br/>${place.address}`;
  if (place.url) {
    content += `<br/><br/><a target="_blank" rel="noopener noreferrer" href="${place.url}">Visit Website</a>`;
  }
  return content;
}

/** Wagtail "places" Google Map amenity pins. */
export function PlacesBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as PlacesValue;
  const instance = value.resolved_instance;
  const apiKey =
    value.google_maps_api_key || process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY || "";

  const groups = instance?.place_groups ?? [];
  const centerLat = parseFloat(instance?.latitude ?? "49.2653066");
  const centerLng = parseFloat(instance?.longitude ?? "-123.0135384");

  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<google.maps.Map | null>(null);
  const placeMarkersRef = useRef<PlaceMarkerEntry[]>([]);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);
  const centerRef = useRef({ lat: centerLat, lng: centerLng });

  const [expandedGroupId, setExpandedGroupId] = useState<number | null>(
    () => instance?.place_groups?.[0]?.id ?? null
  );

  const activeGroupId = expandedGroupId ?? groups[0]?.id ?? null;

  centerRef.current = { lat: centerLat, lng: centerLng };

  const adjustBoundsForGroup = useCallback((groupId: number | null) => {
    const map = mapInstanceRef.current;
    if (!map || groupId == null) return;

    const visible = placeMarkersRef.current.filter(
      (entry) => Number(entry.groupId) === Number(groupId)
    );

    if (!visible.length) {
      map.setCenter(centerRef.current);
      map.setZoom(DEFAULT_ZOOM);
      return;
    }

    const bounds = new google.maps.LatLngBounds();
    bounds.extend(centerRef.current);
    for (const { marker } of visible) {
      const pos = marker.getPosition();
      if (pos) bounds.extend(pos);
    }
    map.fitBounds(bounds);
    google.maps.event.addListenerOnce(map, "bounds_changed", () => {
      if ((map.getZoom() ?? DEFAULT_ZOOM) > DEFAULT_ZOOM) {
        map.setZoom(DEFAULT_ZOOM);
      }
    });
  }, []);

  const applyMarkerVisibility = useCallback(
    (groupId: number | null) => {
      if (groupId == null) return;
      infoWindowRef.current?.close();
      for (const entry of placeMarkersRef.current) {
        entry.marker.setVisible(Number(entry.groupId) === Number(groupId));
      }
      adjustBoundsForGroup(groupId);
    },
    [adjustBoundsForGroup]
  );

  useEffect(() => {
    if (!apiKey || !mapRef.current || !instance || groups.length === 0) return;

    let cancelled = false;

    loadGoogleMaps(apiKey).then(() => {
      if (cancelled || !mapRef.current) return;

      const center = { lat: centerLat, lng: centerLng };
      const map = new google.maps.Map(mapRef.current, {
        zoom: DEFAULT_ZOOM,
        scrollwheel: false,
        center,
        clickableIcons: false,
        mapTypeControl: false,
        streetViewControl: false,
        styles: PLACES_MAP_STYLES,
      });
      mapInstanceRef.current = map;

      new google.maps.Marker({
        position: center,
        map,
        icon: {
          url: MAIN_MARKER_ICON,
          scaledSize: new google.maps.Size(80, 93),
        },
      });

      infoWindowRef.current = new google.maps.InfoWindow({ content: "holding..." });

      const entries: PlaceMarkerEntry[] = [];
      for (const group of groups) {
        for (const place of group.places) {
          const p = place.value;
          const lat = parseFloat(p.latitude);
          const lng = parseFloat(p.longitude);
          if (Number.isNaN(lat) || Number.isNaN(lng)) continue;

          const marker = new google.maps.Marker({
            position: { lat, lng },
            map,
            icon: categoryMarkerIcon(group.color),
            title: p.title,
            visible: false,
          });

          marker.addListener("click", () => {
            infoWindowRef.current?.setContent(infoWindowContent(p));
            infoWindowRef.current?.open(map, marker);
          });

          entries.push({ marker, groupId: group.id, place: p });
        }
      }

      placeMarkersRef.current = entries;
      applyMarkerVisibility(expandedGroupId ?? groups[0]?.id ?? null);
    });

    return () => {
      cancelled = true;
    };
  }, [apiKey, instance, groups, centerLat, centerLng, applyMarkerVisibility]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const onResize = () => adjustBoundsForGroup(activeGroupId);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [activeGroupId, adjustBoundsForGroup]);

  const openPlace = (entry: PlaceMarkerEntry) => {
    const map = mapInstanceRef.current;
    if (!map) return;
    infoWindowRef.current?.setContent(infoWindowContent(entry.place));
    infoWindowRef.current?.open(map, entry.marker);
  };

  const handlePlaceClick = (groupId: number, place: PlaceItem) => {
    if (Number(activeGroupId) !== Number(groupId)) {
      setExpandedGroupId(groupId);
      applyMarkerVisibility(groupId);
    }
    const entry = placeMarkersRef.current.find(
      (e) => Number(e.groupId) === Number(groupId) && e.place.title === place.title
    );
    if (entry) openPlace(entry);
  };

  const handleGroupClick = (groupId: number) => {
    if (Number(groupId) !== Number(activeGroupId)) {
      setExpandedGroupId(groupId);
      applyMarkerVisibility(groupId);
    }
  };

  if (!instance || groups.length === 0) return null;

  return (
    <article className="places-block">
      {value.title && <h2 className="title text-center">{value.title}</h2>}

      <div
        className="places-widget google-map"
        data-latitude={instance.latitude}
        data-longitude={instance.longitude}
      >
        <div className="places-nav map-filter">
          <div className="panel-group" id="places" role="tablist" aria-multiselectable="true">
            {groups.map((group) => {
              const isExpanded = Number(activeGroupId) === Number(group.id);
              return (
                <div
                  key={group.id}
                  className="panel panel-primary places-category category"
                  data-color={group.color}
                >
                  <div
                    className="title panel-heading uppercase text-left"
                    role="tab"
                    id={`places-group-${group.id}`}
                    aria-expanded={isExpanded}
                    aria-controls={`places-group-collapse-${group.id}`}
                    onClick={() => handleGroupClick(group.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleGroupClick(group.id);
                      }
                    }}
                  >
                    <div className="icon" style={{ borderColor: group.color }}>
                      <div className="box-filled" style={{ backgroundColor: group.color }} />
                    </div>
                    <div className="h3 subhead white">{group.title}</div>
                  </div>
                  <div
                    id={`places-group-collapse-${group.id}`}
                    aria-expanded={isExpanded}
                    aria-hidden={!isExpanded}
                    data-color={group.color}
                    className={`places places-place${isExpanded ? " is-open" : ""}`}
                    role="tabpanel"
                    aria-labelledby={`places-group-${group.id}`}
                  >
                    <ul>
                      {group.places.map((place, idx) => {
                        const p = place.value;
                        return (
                          <li
                            key={`${group.id}-${idx}`}
                            className="list-group-item"
                            data-title={p.title}
                            data-latitude={p.latitude}
                            data-longitude={p.longitude}
                            {...(p.url ? { "data-url": p.url } : {})}
                            {...(p.address ? { "data-address": p.address } : {})}
                            onClick={() => handlePlaceClick(group.id, p)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault();
                                handlePlaceClick(group.id, p);
                              }
                            }}
                          >
                            {p.title}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="places-map vue-map-container" ref={mapRef} />
      </div>
    </article>
  );
}
