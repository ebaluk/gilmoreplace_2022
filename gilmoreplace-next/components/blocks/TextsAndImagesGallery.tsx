"use client";


/**
 * Stream-field block UI for `TextsAndImagesGallery`.
 */
import { useMemo, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { createElement } from "react";
import { formatImageUrl } from "@/lib/utils";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import {
  ModalCarousel,
  type ModalCarouselImage,
} from "@/components/shared/ModalCarousel";

interface ResolvedImage {
  url: string;
  alt?: string;
  title?: string;
}

interface GalleryItem {
  type: string;
  id?: string;
  value: {
    image?: number;
    decor?: string;
    title?: string;
    text?: string;
    resolved_image?: ResolvedImage;
    items?: GalleryItem[];
  };
}

interface GalleryBox {
  type: string;
  id?: string;
  value: GalleryItem["value"];
}

interface GalleryRow {
  boxes?: GalleryBox[];
}

interface GalleryValue {
  title?: string;
  title_tag?: string;
  rows?: GalleryRow[];
  resolved_rows?: GalleryRow[];
}

const DECOR_SVG: Record<string, string> = {
  "top-left": "/images/svgs/tri-top-left.svg",
  "top-right": "/images/svgs/tri-top-right.svg",
  "bottom-left": "/images/svgs/tri-bottom-left.svg",
};

function collectGalleryImages(rows: GalleryRow[]): ModalCarouselImage[] {
  const images: ModalCarouselImage[] = [];

  function addImage(img?: ResolvedImage) {
    if (img?.url) {
      images.push({ url: img.url, alt: img.alt, title: img.title });
    }
  }

  function processItem(item: GalleryItem) {
    if (item.type === "image") {
      addImage(item.value.resolved_image);
    } else if (item.type === "text" && item.value.items?.length) {
      item.value.items.forEach(processItem);
    }
  }

  for (const row of rows) {
    for (const box of row.boxes ?? []) {
      if (box.type === "image_box") {
        addImage(box.value.resolved_image);
      } else if (box.type === "image_text_box") {
        box.value.items?.forEach(processItem);
      }
    }
  }

  return images;
}

function PlusIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
      <g stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
        <g stroke="#FFFFFF" strokeWidth="2">
          <path d="M8,0 L8,16" />
          <path d="M16,8 L0,8" />
        </g>
      </g>
    </svg>
  );
}

function DecorCorner({ decor }: { decor?: string }) {
  if (!decor || !DECOR_SVG[decor]) return null;
  return (
    <img
      className={`corner ${decor}`}
      src={DECOR_SVG[decor]}
      alt=""
      aria-hidden="true"
    />
  );
}

function GalleryImageLink({
  image,
  decor,
  className,
  onOpen,
}: {
  image: ResolvedImage;
  decor?: string;
  className: string;
  onOpen: () => void;
}) {
  const url = formatImageUrl(image.url);
  return (
    <button
      type="button"
      className={`block modal-carousel ${className}`}
      style={{ backgroundImage: `url(${url})` }}
      onClick={onOpen}
    >
      <DecorCorner decor={decor} />
      <span className="btn-plus bottomRight pointer-events-none" aria-hidden="true">
        <PlusIcon />
      </span>
    </button>
  );
}

function GalleryTextBlock({ title, text }: { title?: string; text?: string }) {
  return (
    <div className="block half text">
      {title && <h3 className="subhead underline white">{title}</h3>}
      {text && <RichTextRenderer html={text} />}
    </div>
  );
}

function GalleryItemRenderer({
  item,
  imageClassName,
  imageIndexByUrl,
  onOpenImage,
}: {
  item: GalleryItem;
  imageClassName: string;
  imageIndexByUrl: Map<string, number>;
  onOpenImage: (index: number) => void;
}) {
  if (item.type === "image" && item.value.resolved_image) {
    const idx = imageIndexByUrl.get(item.value.resolved_image.url);
    return (
      <GalleryImageLink
        image={item.value.resolved_image}
        decor={item.value.decor}
        className={imageClassName}
        onOpen={() => idx !== undefined && onOpenImage(idx)}
      />
    );
  }

  if (item.type === "text" && item.value.items?.length) {
    return (
      <>
        {item.value.items.map((sub, i) => (
          <GalleryItemRenderer
            key={sub.id ?? i}
            item={sub}
            imageClassName="half image"
            imageIndexByUrl={imageIndexByUrl}
            onOpenImage={onOpenImage}
          />
        ))}
      </>
    );
  }

  if (item.type === "text") {
    return <GalleryTextBlock title={item.value.title} text={item.value.text} />;
  }

  return null;
}

function GalleryBoxRenderer({
  box,
  imageIndexByUrl,
  onOpenImage,
}: {
  box: GalleryBox;
  imageIndexByUrl: Map<string, number>;
  onOpenImage: (index: number) => void;
}) {
  if (box.type === "image_box" && box.value.resolved_image) {
    const idx = imageIndexByUrl.get(box.value.resolved_image.url);
    return (
      <div className="image-block">
        <GalleryImageLink
          image={box.value.resolved_image}
          decor={box.value.decor}
          className="fullBlock"
          onOpen={() => idx !== undefined && onOpenImage(idx)}
        />
      </div>
    );
  }

  if (box.type === "image_text_box" && box.value.items?.length) {
    return (
      <div className="image-block info">
        {box.value.items.map((item, i) => (
          <GalleryItemRenderer
            key={item.id ?? i}
            item={item}
            imageClassName="full image"
            imageIndexByUrl={imageIndexByUrl}
            onOpenImage={onOpenImage}
          />
        ))}
      </div>
    );
  }

  return null;
}

/** Wagtail texts-and-images collage / amenity blocks. */
export function TextsAndImagesGallery({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as GalleryValue;
  const { title, title_tag = "h2" } = value;
  const rows = value.resolved_rows ?? value.rows ?? [];
  const TitleTag = title_tag as keyof JSX.IntrinsicElements;

  const [modalOpen, setModalOpen] = useState(false);
  const [modalIdx, setModalIdx] = useState(0);

  const images = useMemo(() => collectGalleryImages(rows), [rows]);
  const imageIndexByUrl = useMemo(() => {
    const map = new Map<string, number>();
    images.forEach((img, i) => map.set(img.url, i));
    return map;
  }, [images]);

  if (!rows.length) return null;

  return (
    <>
      <div className="amenities-blocks">
        {title && createElement(TitleTag, null, title)}
        {rows.map((row, ri) => (
          <div key={ri} className="block-section">
            {row.boxes?.map((box, bi) => (
              <GalleryBoxRenderer
                key={box.id ?? bi}
                box={box}
                imageIndexByUrl={imageIndexByUrl}
                onOpenImage={(index) => {
                  setModalIdx(index);
                  setModalOpen(true);
                }}
              />
            ))}
          </div>
        ))}
      </div>

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
