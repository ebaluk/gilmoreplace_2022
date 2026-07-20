"use client";


/**
 * Stream-field block UI for `GalleryCollectionsBlock`.
 */
import { useMemo, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import {
  ModalCarousel,
  type ModalCarouselImage,
} from "@/components/shared/ModalCarousel";
import { SiteContainer } from "@/components/layout/SiteContainer";

interface GalleryImage {
  id: number;
  title?: string;
  url: string;
  alt?: string;
}

interface GalleryCollectionsValue {
  title?: string;
  mode?: string;
  show_categories?: boolean;
  show_image_title?: boolean;
  theme?: { id: number; css_class: string | null } | null;
  gallery_collections?: { title?: string; collection?: number; tag?: number | null }[];
  resolved_images?: GalleryImage[];
}

function gridModeClass(mode?: string): string {
  if (mode === "lt-12") return "mode-lt-6";
  return "mode-6";
}

/** Wagtail gallery-with-collections (category tabs). */
export function GalleryCollectionsBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as GalleryCollectionsValue;
  const {
    title,
    mode,
    show_categories,
    show_image_title,
    theme,
    gallery_collections = [],
    resolved_images = [],
  } = value;

  const [modalOpen, setModalOpen] = useState(false);
  const [modalIdx, setModalIdx] = useState(0);

  const images = useMemo<ModalCarouselImage[]>(
    () =>
      resolved_images.map((img) => ({
        url: img.url,
        alt: img.alt,
        title: show_image_title ? img.title : undefined,
      })),
    [resolved_images, show_image_title],
  );

  const remindClass = `remind-${resolved_images.length % 3}`;
  const gridClass = `${gridModeClass(mode)} ${remindClass}`.trim();

  if (!resolved_images.length) return null;

  return (
    <>
      <article
        className={`gallery-block gallerywithcategoriespage gallery-type-flex${theme?.id ? ` themed-${theme.id}` : ""}${theme?.css_class ? ` ${theme.css_class}` : ""}`}
      >
        {title && <h2 className="subhead white">{title}</h2>}

        <SiteContainer>
          <div className="page-header-wrapper">
            <div className="page-header inside text-center clearfix has-subnav">
              {show_categories && gallery_collections.length > 0 ? (
                <ul className="page-nav page-navbar gallerywc-navbar list">
                  <li className="active">
                    <a data-cat="all" href="#">
                      All
                    </a>
                  </li>
                  {gallery_collections.map((coll, i) => (
                    <li key={i}>
                      <a data-cat={String(i + 1)} href="#">
                        {coll.title}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          </div>

          <div className={`grid clearfix ${gridClass}`}>
            {resolved_images.map((img, i) => (
              <button
                key={img.id}
                type="button"
                className="gallery-tile gallery-tile--square"
                data-id={img.id}
                onClick={() => {
                  setModalIdx(i);
                  setModalOpen(true);
                }}
              >
                <span
                  className="gallery-tile__image"
                  style={{
                    backgroundImage: `url(${formatImageUrl(img.url)})`,
                  }}
                />
              </button>
            ))}
          </div>
        </SiteContainer>
      </article>

      <ModalCarousel
        images={images}
        index={modalIdx}
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onIndexChange={setModalIdx}
      />
    </>
  );
}
