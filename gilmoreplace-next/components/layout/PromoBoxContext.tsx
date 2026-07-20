"use client";


/**
 * Site layout: PromoBoxContext.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  consumePendingPromoAutoShow,
  onPromoAutoShowRequest,
} from "@/lib/promo-auto-show";

interface PromoBoxContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
  requestOpen: () => void;
}

const PromoBoxContext = createContext<PromoBoxContextValue | null>(null);

export function usePromoBox() {
  return useContext(PromoBoxContext);
}

/** Layout: PromoBoxProvider. */
export function PromoBoxProvider({
  children,
  autoShow = false,
}: {
  children: ReactNode;
  autoShow?: boolean;
}) {
  const [open, setOpen] = useState(false);

  useLayoutEffect(() => {
    if (!autoShow) {
      setOpen(false);
      return;
    }

    let timer: number | undefined;

    const scheduleOpen = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => setOpen(true), 2000);
    };

    const unsubscribe = onPromoAutoShowRequest(scheduleOpen);
    if (consumePendingPromoAutoShow()) {
      scheduleOpen();
    }

    return () => {
      unsubscribe();
      window.clearTimeout(timer);
    };
  }, [autoShow]);

  useEffect(() => {
    if (!autoShow) setOpen(false);
  }, [autoShow]);

  const requestOpen = useCallback(() => setOpen(true), []);

  const value = useMemo(
    () => ({ open, setOpen, requestOpen }),
    [open, requestOpen],
  );

  return (
    <PromoBoxContext.Provider value={value}>{children}</PromoBoxContext.Provider>
  );
}

/** Layout: PromoBoxTrigger. */
export function PromoBoxTrigger({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const promo = usePromoBox();
  if (!promo) {
    return <span className={className}>{children}</span>;
  }

  return (
    <a
      href="#"
      className={className}
      onClick={(e) => {
        e.preventDefault();
        promo.requestOpen();
      }}
    >
      {children}
    </a>
  );
}
