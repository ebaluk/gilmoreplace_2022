"use client";


/**
 * Shared UI: ModalCarousel.
 */
import { useState, type MouseEvent } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Keyboard } from "swiper/modules";
import type { Swiper as SwiperType } from "swiper";
import "swiper/css";
import { formatImageUrl } from "@/lib/utils";
import { PortalModalShell } from "@/components/shared/PortalModalShell";

export interface ModalCarouselImage {
  url: string;
  alt?: string;
  title?: string;
}

interface ModalCarouselProps {
  images: ModalCarouselImage[];
  index: number;
  open: boolean;
  onClose: () => void;
  onIndexChange: (index: number) => void;
}

/** Image carousel dialog (gallery). */
export function ModalCarousel({
  images,
  index,
  open,
  onClose,
  onIndexChange,
}: ModalCarouselProps) {
  const [swiper, setSwiper] = useState<SwiperType | null>(null);

  const hasControls = images.length > 1;

  const goPrev = (e: MouseEvent) => {
    e.preventDefault();
    swiper?.slidePrev();
  };

  const goNext = (e: MouseEvent) => {
    e.preventDefault();
    swiper?.slideNext();
  };

  if (!images.length) return null;

  return (
    <PortalModalShell
      open={open}
      onOpenChange={(next) => {
        if (!next) onClose();
      }}
      transitionDurationMs={800}
      closeOnBackdrop={false}
      backdropClassName="fixed inset-0 z-[1040] border-0 bg-transparent p-0"
      className="z-[1050]"
    >
      {({ visible, close, stopPropagation }) => (
        <div
          className="gallery-dialog site-dialog fixed inset-0 z-[1050] w-full max-w-none translate-x-0 translate-y-0 rounded-none border-0 bg-transparent p-0 shadow-none outline-none"
          aria-label="Image gallery"
          role="dialog"
          data-state={visible ? "open" : "closed"}
          onClick={close}
        >
          <div className="gallery-dialog__panel" onClick={stopPropagation}>
          <button
            type="button"
            className="close gallery-dialog__close"
            aria-label="Close"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              close();
            }}
          />
          <div className="gallery-swiper" id="modal-carousel-carousel">
            <Swiper
              modules={[Keyboard]}
              className="gallery-swiper__track"
              initialSlide={index}
              speed={400}
              allowTouchMove={hasControls}
              grabCursor={hasControls}
              keyboard={{ enabled: hasControls }}
              onSwiper={setSwiper}
              onSlideChange={(s) => onIndexChange(s.realIndex)}
            >
              {images.map((img, i) => (
                <SwiperSlide key={i} className="gallery-swiper__slide" tag="div">
                  <div
                    className="gallery-swiper__image"
                    style={{
                      backgroundImage: `url(${formatImageUrl(img.url)})`,
                    }}
                    role="img"
                    aria-label={img.alt || img.title || "Gallery image"}
                  />
                </SwiperSlide>
              ))}
            </Swiper>

            {hasControls && (
              <div className="gallery-swiper__controls">
                <button
                  type="button"
                  className="gallery-swiper__button gallery-swiper__button--prev"
                  aria-label="Previous image"
                  onClick={goPrev}
                >
                  <span className="gallery-swiper__button-icon" />
                </button>
                <button
                  type="button"
                  className="gallery-swiper__button gallery-swiper__button--next"
                  aria-label="Next image"
                  onClick={goNext}
                >
                  <span className="gallery-swiper__button-icon" />
                </button>
              </div>
            )}
          </div>
          </div>
        </div>
      )}
    </PortalModalShell>
  );
}
