"use client";


/**
 * Shared UI: FloorPlanOverlayShell.
 */
import { useCallback, useRef, useState, type MouseEvent, type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { PortalModalShell } from "@/components/shared/PortalModalShell";

const OVERLAY_TRANSITION_MS = 500;

interface FloorPlanOverlayShellProps {
  wrapperClassName: string;
  kpCount: number;
  onClose: () => void;
  children: ReactNode;
}

/** Full-screen floor-plan overlay chrome. */
export function FloorPlanOverlayShell({
  wrapperClassName,
  kpCount,
  onClose,
  children,
}: FloorPlanOverlayShellProps) {
  const [open, setOpen] = useState(true);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  const stopPropagation = (e: MouseEvent) => e.stopPropagation();

  const handleOpenChange = useCallback((next: boolean) => {
    setOpen(next);
    if (!next) {
      // Keep React tree mounted while CSS opacity fade-out runs.
      window.setTimeout(() => onCloseRef.current(), OVERLAY_TRANSITION_MS);
    }
  }, []);

  return (
    <PortalModalShell
      open={open}
      onOpenChange={handleOpenChange}
      transitionDurationMs={OVERLAY_TRANSITION_MS}
      closeOnBackdrop={false}
      backdropClassName="fixed inset-0 z-[9999] border-0 bg-transparent p-0"
      className={cn("floorplan-portal z-[10000]", wrapperClassName)}
    >
      {({ visible, close }) => (
        <div
          className={cn("overlay", visible && "active")}
          data-cnt={kpCount}
          onClick={close}
          data-floorplan-overlay=""
        >
          <button
            type="button"
            className="close"
            aria-label="Close"
            onClick={(e) => {
              e.stopPropagation();
              close();
            }}
          />
          <div className="content" onClick={stopPropagation}>
            {children}
          </div>
        </div>
      )}
    </PortalModalShell>
  );
}
