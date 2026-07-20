"use client";


/**
 * Shared UI: PortalModalShell.
 */
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type MouseEvent,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";
import { lockBodyScroll, pushEscapeHandler, unlockBodyScroll } from "@/lib/modal-runtime";

interface PortalModalShellProps {
  open: boolean;
  onOpenChange: (nextOpen: boolean) => void;

  /** Used for fade-out timing before unmount. */
  transitionDurationMs?: number;

  /** When true, backdrop click closes. Default: true */
  closeOnBackdrop?: boolean;

  /** When true, ESC closes (top of stack). Default: true */
  closeOnEscape?: boolean;

  /** When true, disables body scroll. Default: true */
  lockScroll?: boolean;

  /** Backdrop classes (optional). */
  backdropClassName?: string;

  /** Wrapper classes (optional). */
  className?: string;

  /** Render panel/content. Receives helpers + `visible` for CSS. */
  children: (args: {
    visible: boolean;
    close: () => void;
    stopPropagation: (e: MouseEvent) => void;
  }) => ReactNode;
}

/** Portal + scroll-lock shell for generic modals. */
export function PortalModalShell({
  open,
  onOpenChange,
  transitionDurationMs = 300,
  closeOnBackdrop = true,
  closeOnEscape = true,
  lockScroll = true,
  backdropClassName,
  className,
  children,
}: PortalModalShellProps) {
  const [mounted, setMounted] = useState(false);
  const [rendered, setRendered] = useState(open);
  const [visible, setVisible] = useState(false);
  const closingRef = useRef(false);
  const timerRef = useRef<number | null>(null);

  useEffect(() => setMounted(true), []);

  const clearTimer = () => {
    if (timerRef.current !== null) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  const finishClose = useCallback(() => {
    clearTimer();
    closingRef.current = false;
    setRendered(false);
    setVisible(false);
  }, []);

  const close = useCallback(() => {
    if (closingRef.current) return;
    closingRef.current = true;
    // Start CSS exit this frame (do not wait for the `open` effect).
    setVisible(false);
    onOpenChange(false);
  }, [onOpenChange]);

  const stopPropagation = useCallback((e: MouseEvent) => e.stopPropagation(), []);

  // Drive mount/unmount + fade lifecycle from `open`.
  useEffect(() => {
    if (!mounted) return;

    clearTimer();

    if (open) {
      closingRef.current = false;
      setRendered(true);
      const frame = requestAnimationFrame(() => setVisible(true));
      return () => cancelAnimationFrame(frame);
    }

    if (!rendered) return;

    setVisible(false);
    if (transitionDurationMs <= 0) {
      finishClose();
      return;
    }
    timerRef.current = window.setTimeout(finishClose, transitionDurationMs);
    return () => clearTimer();
  }, [open, mounted, rendered, transitionDurationMs, finishClose]);

  // Runtime effects (scroll lock + ESC stack).
  useEffect(() => {
    if (!mounted || !rendered) return;

    if (lockScroll) lockBodyScroll();

    const unsubscribeEsc = closeOnEscape
      ? pushEscapeHandler(() => close())
      : () => {};

    return () => {
      unsubscribeEsc();
      if (lockScroll) unlockBodyScroll();
    };
  }, [mounted, rendered, lockScroll, closeOnEscape, close]);

  const backdropClick = useCallback(() => {
    if (!closeOnBackdrop) return;
    close();
  }, [closeOnBackdrop, close]);

  if (!mounted || !rendered) return null;

  return createPortal(
    <div
      className={cn("portal-modal", className)}
      data-state={visible ? "open" : "closed"}
    >
      <button
        type="button"
        className={cn("portal-modal__backdrop", backdropClassName)}
        aria-label="Close dialog"
        onClick={backdropClick}
      />
      {children({ visible, close, stopPropagation })}
    </div>,
    document.body
  );
}
