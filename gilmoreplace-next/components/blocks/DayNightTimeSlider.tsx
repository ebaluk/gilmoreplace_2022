"use client";


/**
 * Stream-field block UI for `DayNightTimeSlider`.
 */
import { useCallback, useRef, useState } from "react";
import { formatImageUrl } from "@/lib/utils";

interface DayNightTimeSliderProps {
  daySrc: string;
  dayAlt: string;
  nightSrc: string;
  nightAlt: string;
}

/** Day/night comparison slider for an image pair. */
export function DayNightTimeSlider({
  daySrc,
  dayAlt,
  nightSrc,
  nightAlt,
}: DayNightTimeSliderProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [slideWidth, setSlideWidth] = useState(50);
  const lastXRef = useRef(0);
  const draggingRef = useRef(false);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    draggingRef.current = true;
    lastXRef.current = e.clientX;
    e.currentTarget.setPointerCapture(e.pointerId);
  }, []);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!draggingRef.current || !containerRef.current) return;
    const containerWidth = containerRef.current.offsetWidth;
    if (!containerWidth) return;

    const dx = ((lastXRef.current - e.clientX) * 100) / containerWidth;
    lastXRef.current = e.clientX;

    setSlideWidth((current) => {
      const next = current - dx;
      return Math.min(100, Math.max(0, next));
    });
  }, []);

  const handlePointerUp = useCallback(() => {
    draggingRef.current = false;
  }, []);

  return (
    <div className="day-night-time-slider" ref={containerRef}>
      <div className="slide" style={{ width: `${slideWidth}%` }}>
        <div className="slide-image">
          <img src={formatImageUrl(daySrc)} alt={dayAlt} />
        </div>
        <div
          className="slide-button"
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerCancel={handlePointerUp}
        >
          <div>
            <i className="fa fa-angle-left" aria-hidden="true" />
            <i className="fa fa-angle-right" aria-hidden="true" />
          </div>
        </div>
      </div>
      <img src={formatImageUrl(nightSrc)} alt={nightAlt} />
    </div>
  );
}
