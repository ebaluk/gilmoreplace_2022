"use client";


/**
 * Site layout: PromoBoxModal.
 */
import { useEffect, useState } from "react";
import { type PromoBoxData } from "@/types/page";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { StreamLinkButton } from "@/components/shared/StreamLinkButton";
import { usePromoBox } from "@/components/layout/PromoBoxContext";
import { PortalModalShell } from "@/components/shared/PortalModalShell";
import { formatImageUrl, cn } from "@/lib/utils";

interface PromoBoxModalProps {
  promo: PromoBoxData;
  pageId: number;
  locale: string;
}

function PromoCloseButton({
  className,
  onClose,
}: {
  className?: string;
  onClose: () => void;
}) {
  return (
    <button
      type="button"
      aria-label="Close"
      className={className}
      onClick={onClose}
    >
      <span className="sr-only">Close</span>
    </button>
  );
}

/** Promo overlay modal driven by PromoBoxContext. */
export function PromoBoxModal({ promo, pageId, locale }: PromoBoxModalProps) {
  const promoBox = usePromoBox();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const open = promoBox?.open ?? false;
  const setOpen = promoBox?.setOpen;

  if (!promoBox || !mounted) return null;

  const close = () => promoBox.setOpen(false);
  const modeClass =
    promo.mode === "image"
      ? "mode-image"
      : promo.mode === "text"
        ? "mode-text"
        : "mode-default";

  return (
    <PortalModalShell
      open={open}
      onOpenChange={(next) => setOpen?.(next)}
      transitionDurationMs={300}
      backdropClassName="promo-box-backdrop fixed inset-0 z-[10050] border-0 bg-black/50 p-0"
      className="z-[10050]"
    >
      {({ visible }) => (
        <div
          id={`promo-box-${pageId}`}
          className={cn(
            "promo-dialog promo-box",
            modeClass,
            promo.show_logo && "logo"
          )}
          role="dialog"
          aria-label={promo.title}
          data-state={visible ? "open" : "closed"}
        >
          <div
            className={cn(
              "promo-dialog__panel relative overflow-visible",
              promo.smaller_popup ? "smaller" : "large"
            )}
          >
            <PromoCloseButton className="close" onClose={close} />

            {promo.mode === "image" ? (
              <div className="image">
                {promo.image ? (
                  <img
                    src={formatImageUrl(promo.image.url)}
                    alt={promo.image.alt || promo.title}
                    width={promo.image.width}
                    height={promo.image.height}
                  />
                ) : null}
                <div className="related-links text-center">
                  {promo.links.map((link, i) => (
                    <StreamLinkButton key={i} link={link} locale={locale} />
                  ))}
                </div>
                <div className="fancy-corners">
                  <span />
                </div>
              </div>
            ) : promo.mode === "text" ? (
              <div className="text">
                <div className="content">
                  <h2 className="h2 title">{promo.title}</h2>
                  <RichTextRenderer html={promo.body} className="rich-text" />
                  <div className="related-links text-center">
                    {promo.links.map((link, i) => (
                      <StreamLinkButton key={i} link={link} locale={locale} />
                    ))}
                  </div>
                </div>
                <div className="fancy-corners">
                  <span />
                </div>
              </div>
            ) : (
              <>
                {promo.image && (
                  <div
                    className="image"
                    style={{
                      backgroundImage: `url(${formatImageUrl(promo.image.url)})`,
                    }}
                  />
                )}
                <div className="text">
                  <div className="content">
                    <h2 className="title">{promo.title}</h2>
                    <RichTextRenderer html={promo.body} className="rich-text" />
                    <div className="related-links text-center">
                      {promo.links.map((link, i) => (
                        <StreamLinkButton key={i} link={link} locale={locale} />
                      ))}
                    </div>
                  </div>
                  <div className="fancy-corners">
                    <span />
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </PortalModalShell>
  );
}
