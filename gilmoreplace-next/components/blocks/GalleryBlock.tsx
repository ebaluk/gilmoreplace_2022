"use client";


/**
 * Stream-field block UI for `GalleryBlock`.
 */
import { useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import {
  ModalCarousel,
  type ModalCarouselImage,
} from "@/components/shared/ModalCarousel";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface GalleryValue {
  images?: { id: number; url: string; alt: string; caption?: string; width: number; height: number }[];
  theme?: { id: number; css_class: string | null } | null;
}

/** Wagtail "gallery" lightbox carousel. */
export function GalleryBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as GalleryValue;
  const { images = [], theme } = value;

  const [modalOpen, setModalOpen] = useState(false);
  const [modalIdx, setModalIdx] = useState(0);

  if (!images.length) return null;

  const images10 = images.slice(0, 10);
  const carouselImages: ModalCarouselImage[] = images.map((img) => ({
    url: img.url,
    alt: img.alt,
  }));

  return (
    <>
      <article
        className={cn(
          "gallery-block",
          siteContainerClass,
          theme?.id ? `themed-${theme.id}` : "",
          theme?.css_class || ""
        )}
      >
        <div className="collage collage-10">
          <div className="chunk">
            {images10.map((img, i) => (
              <div key={img.id} className="list-item">
                <button
                  type="button"
                  className="gallery-tile"
                  data-id={img.id}
                  draggable={false}
                  style={{ backgroundImage: `url(${formatImageUrl(img.url)})` }}
                  onClick={() => {
                    setModalIdx(i);
                    setModalOpen(true);
                  }}
                  onDragStart={(e) => {
                    e.preventDefault();
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </article>

      <ModalCarousel
        images={carouselImages}
        index={modalIdx}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onIndexChange={setModalIdx}
      />
    </>
  );
}
