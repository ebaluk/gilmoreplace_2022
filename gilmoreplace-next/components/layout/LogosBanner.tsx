"use client";

/**
 * Hero logos ticker — CSS infinite marquee with hover-pause, drag/swipe,
 * and Swiper-like momentum coast after a flick.
 *
 * Two identical flex sets sit side-by-side; ``translateX(-50%)`` loops
 * seamlessly. Manual offset lives on ``.logo-track-manual`` so it does not
 * fight the CSS animation ``transform`` on ``.logo-track``.
 */
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type MouseEvent,
  type PointerEvent,
  type WheelEvent,
} from "react";
import type { LogoData } from "@/types/page";
import { cn, formatImageUrl } from "@/lib/utils";

/** Max visible logo slots in legacy CSS (xxlarge). */
const MIN_SET_SLOTS = 10;
const DRAG_THRESHOLD_PX = 5;

/** Momentum (px per ms). */
const VELOCITY_SMOOTH = 0.35;
const MAX_SPEED = 2.5;
const MIN_COAST_START = 0.08;
const MIN_COAST_STOP = 0.02;
const FRICTION_PER_FRAME = 0.95;

function LogoSlide({
  logo,
  inertDuplicate,
}: {
  logo: LogoData;
  inertDuplicate?: boolean;
}) {
  const img = logo.resolved_logo;
  if (!img) return null;

  const image = (
    <img
      src={formatImageUrl(img.url)}
      alt={inertDuplicate ? "" : img.alt || ""}
      draggable={false}
    />
  );

  return (
    <span className="logo-block" data-id={img.id}>
      {logo.link ? (
        <a
          href={logo.link}
          target="_blank"
          rel="noopener noreferrer"
          tabIndex={inertDuplicate ? -1 : undefined}
          aria-hidden={inertDuplicate || undefined}
          draggable={false}
        >
          {image}
        </a>
      ) : (
        image
      )}
    </span>
  );
}

function LogoSet({
  logos,
  inertDuplicate,
  setKey,
}: {
  logos: LogoData[];
  inertDuplicate?: boolean;
  setKey: string;
}) {
  return (
    <div
      className="logo-track-set"
      aria-hidden={inertDuplicate || undefined}
    >
      {logos.map((logo, i) => (
        <LogoSlide
          key={`${setKey}-${logo.resolved_logo!.id}-${i}`}
          logo={logo}
          inertDuplicate={inertDuplicate}
        />
      ))}
    </div>
  );
}

function padLogoSet(unique: LogoData[]): LogoData[] {
  if (!unique.length) return [];
  // Match logos_banner.js: floor(pageSize / len) + 1, with +1 extra so the
  // track is wider than the viewport (avoids a right-edge gap from vw rounding).
  const repeats = Math.max(2, Math.floor(MIN_SET_SLOTS / unique.length) + 2);
  const out: LogoData[] = [];
  for (let i = 0; i < repeats; i++) {
    out.push(...unique);
  }
  return out;
}

/** Wrap offset into (-half, 0] so the duplicated set stays seamless while dragging. */
function wrapDrag(offset: number, halfWidth: number): number {
  if (halfWidth <= 0) return offset;
  let x = offset % halfWidth;
  if (x > 0) x -= halfWidth;
  if (x <= -halfWidth) x += halfWidth;
  return x;
}

function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n));
}

/** Continuously scrolling partner logos under the hero. */
export function LogosBanner({ logos }: { logos: LogoData[] }) {
  const unique = useMemo(() => {
    const seen = new Set<number>();
    const out: LogoData[] = [];
    for (const logo of logos) {
      const id = logo.resolved_logo?.id;
      if (id == null || seen.has(id)) continue;
      seen.add(id);
      out.push(logo);
    }
    return out;
  }, [logos]);

  const setLogos = useMemo(() => padLogoSet(unique), [unique]);

  const bannerRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const dragXRef = useRef(0);
  const lastXRef = useRef(0);
  const lastTRef = useRef(0);
  const velocityRef = useRef(0);
  const pointerIdRef = useRef<number | null>(null);
  const passedThresholdRef = useRef(false);
  const suppressClickRef = useRef(false);
  const originXRef = useRef(0);
  const coastRafRef = useRef<number | null>(null);

  const [dragX, setDragX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isCoasting, setIsCoasting] = useState(false);

  const halfWidth = useCallback(() => {
    const track = trackRef.current;
    if (!track) return 0;
    return track.scrollWidth / 2;
  }, []);

  const applyDrag = useCallback(
    (next: number) => {
      const wrapped = wrapDrag(next, halfWidth());
      dragXRef.current = wrapped;
      setDragX(wrapped);
    },
    [halfWidth],
  );

  const stopCoast = useCallback(() => {
    if (coastRafRef.current != null) {
      cancelAnimationFrame(coastRafRef.current);
      coastRafRef.current = null;
    }
    velocityRef.current = 0;
    setIsCoasting(false);
  }, []);

  const startCoast = useCallback(
    (initialVelocity: number) => {
      stopCoast();
      let v = clamp(initialVelocity, -MAX_SPEED, MAX_SPEED);
      if (Math.abs(v) < MIN_COAST_START) return;

      setIsCoasting(true);
      let last = performance.now();

      const tick = (now: number) => {
        const dt = Math.min(now - last, 64);
        last = now;
        applyDrag(dragXRef.current + v * dt);
        v *= Math.pow(FRICTION_PER_FRAME, dt / 16.67);
        if (Math.abs(v) < MIN_COAST_STOP) {
          stopCoast();
          return;
        }
        velocityRef.current = v;
        coastRafRef.current = requestAnimationFrame(tick);
      };

      coastRafRef.current = requestAnimationFrame(tick);
    },
    [applyDrag, stopCoast],
  );

  useEffect(() => () => stopCoast(), [stopCoast]);

  const endPointerInteraction = useCallback(
    (opts?: { startCoast?: boolean }) => {
      const shouldCoast = Boolean(opts?.startCoast);
      const v = velocityRef.current;
      pointerIdRef.current = null;
      setIsDragging(false);
      passedThresholdRef.current = false;
      // Keep --logos-drag so resuming the CSS marquee does not jump.
      applyDrag(dragXRef.current);
      if (shouldCoast) {
        startCoast(v);
      }
    },
    [applyDrag, startCoast],
  );

  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0 && event.pointerType === "mouse") return;
    stopCoast();
    pointerIdRef.current = event.pointerId;
    lastXRef.current = event.clientX;
    lastTRef.current = performance.now();
    originXRef.current = event.clientX;
    velocityRef.current = 0;
    passedThresholdRef.current = false;
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (pointerIdRef.current !== event.pointerId) return;

    const now = performance.now();
    const dx = event.clientX - lastXRef.current;
    const dt = now - lastTRef.current;
    lastXRef.current = event.clientX;
    lastTRef.current = now;

    if (!passedThresholdRef.current) {
      if (Math.abs(event.clientX - originXRef.current) < DRAG_THRESHOLD_PX) {
        return;
      }
      passedThresholdRef.current = true;
      setIsDragging(true);
    }

    event.preventDefault();
    applyDrag(dragXRef.current + dx);

    if (dt > 0 && dt < 100) {
      const instant = dx / dt;
      velocityRef.current =
        velocityRef.current * (1 - VELOCITY_SMOOTH) + instant * VELOCITY_SMOOTH;
    }
  };

  const onPointerUp = (event: PointerEvent<HTMLDivElement>) => {
    if (pointerIdRef.current !== event.pointerId) return;
    try {
      event.currentTarget.releasePointerCapture(event.pointerId);
    } catch {
      /* already released */
    }
    const didDrag = passedThresholdRef.current;
    if (didDrag) {
      suppressClickRef.current = true;
    }
    endPointerInteraction({ startCoast: didDrag });
  };

  const onClickCapture = (event: MouseEvent<HTMLDivElement>) => {
    if (!suppressClickRef.current) return;
    event.preventDefault();
    event.stopPropagation();
    suppressClickRef.current = false;
  };

  const onPointerLeave = () => {
    // Keep coasting after leave; only end an active press without forcing coast
    // (coast already started on pointerup).
    if (pointerIdRef.current == null) return;
    endPointerInteraction({ startCoast: passedThresholdRef.current });
  };

  const onWheel = (event: WheelEvent<HTMLDivElement>) => {
    const dx =
      Math.abs(event.deltaX) > Math.abs(event.deltaY)
        ? event.deltaX
        : event.shiftKey
          ? event.deltaY
          : 0;
    if (!dx) return;
    event.preventDefault();
    stopCoast();
    // Wheel delta: positive scrolls content rightward visually → decrease translate.
    applyDrag(dragXRef.current - dx);
  };

  if (!unique.length) return null;

  const durationSec = Math.max(setLogos.length, 1) * 2.5;
  const style = {
    "--logos-duration": `${durationSec}s`,
    "--logos-drag": `${dragX}px`,
  } as CSSProperties;

  return (
    <div
      ref={bannerRef}
      className={cn(
        "logos-banner",
        isDragging && "is-dragging",
        isCoasting && "is-coasting",
      )}
      role="region"
      aria-label="Partner logos"
      style={style}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onPointerLeave={onPointerLeave}
      onWheel={onWheel}
      onClickCapture={onClickCapture}
      onDragStart={(event) => event.preventDefault()}
    >
      <div className="logo-track-manual">
        <div className="logo-track" ref={trackRef}>
          <LogoSet logos={setLogos} setKey="a" />
          <LogoSet logos={setLogos} setKey="b" inertDuplicate />
        </div>
      </div>
    </div>
  );
}
