"use client";


/**
 * Stream-field block UI for `CarouselBlock`.
 */
import { useState, createElement, type MouseEvent } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay } from "swiper/modules";
import type { Swiper as SwiperType } from "swiper";
import "swiper/css";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";

interface CarouselValue {
  title?: string;
  title_tag?: string;
  text?: string;
  text_layout?: string;
  show_controls?: boolean;
  full_width?: boolean;
  show_tint?: boolean;
  image_size?: string;
  resolved_images?: { id: number; url: string; alt: string; width: number; height: number }[];
  theme?: { id: number; css_class: string | null } | null;
}

const AUTOPLAY_MS = 5000;

/** Wagtail "carousel" slider. */
export function CarouselBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as CarouselValue;
  const {
    title,
    title_tag = "h2",
    text,
    text_layout = "left",
    show_controls = false,
    full_width = false,
    show_tint,
    image_size = "inside",
    resolved_images = [],
    theme,
  } = value;

  const [swiper, setSwiper] = useState<SwiperType | null>(null);

  const imageCount = resolved_images.length;
  const carouselId = `carousel-${block.id}`;
  const hasControls = imageCount > 1 && show_controls;

  const goPrev = (e: MouseEvent) => {
    e.preventDefault();
    swiper?.slidePrev();
  };

  const goNext = (e: MouseEvent) => {
    e.preventDefault();
    swiper?.slideNext();
  };

  if (!imageCount) return null;

  const TitleTag = title_tag as keyof JSX.IntrinsicElements;
  const articleClass = [
    "carousel-block",
    theme?.id ? `themed-${theme.id}` : "",
    theme?.css_class || "",
    show_tint ? "tint" : "",
    `text-layout-${text_layout}`,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <article className={articleClass}>
      {(title || text) && (
        <div className={`text-wrapper text-layout-${text_layout}`}>
          <div className="title-text">
            {title &&
              createElement(
                TitleTag,
                { className: `title ${title_tag}` },
                title
              )}
            {text && <div className="text">{text}</div>}
          </div>
        </div>
      )}

      <div className={`img-top image-block${full_width ? " full-width" : ""}`}>
        <div className={`carousel-wrapper image-size-${image_size}`}>
          <div
            id={carouselId}
            className="carousel-swiper"
            data-interval={AUTOPLAY_MS}
          >
            <Swiper
              modules={[Autoplay]}
              className="carousel-swiper__track"
              speed={600}
              loop={imageCount > 1}
              allowTouchMove={imageCount > 1}
              grabCursor={imageCount > 1}
              autoplay={
                imageCount > 1
                  ? {
                      delay: AUTOPLAY_MS,
                      pauseOnMouseEnter: true,
                      disableOnInteraction: false,
                    }
                  : false
              }
              onSwiper={setSwiper}
            >
              {resolved_images.map((img) => {
                const imgUrl = formatImageUrl(img.url);
                return (
                  <SwiperSlide key={img.id} className="carousel-swiper__slide" tag="div">
                    <div
                      className="carousel-image"
                      style={{ backgroundImage: `url(${imgUrl})` }}
                      role="img"
                      aria-label={img.alt || undefined}
                    />
                  </SwiperSlide>
                );
              })}
            </Swiper>

            {hasControls && (
              <>
                <button
                  type="button"
                  className="carousel-swiper__button carousel-swiper__button--prev"
                  aria-label="Previous"
                  onClick={goPrev}
                >
                  <span className="sr-only">Previous</span>
                </button>
                <button
                  type="button"
                  className="carousel-swiper__button carousel-swiper__button--next"
                  aria-label="Next"
                  onClick={goNext}
                >
                  <span className="sr-only">Next</span>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
