"use client";


/**
 * Site layout: Hero.
 */
import { useEffect, useRef } from "react";
import Link from "next/link";
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, EffectFade } from "swiper/modules";
import { type HeroData } from "@/types/page";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { StreamLinkButton } from "@/components/shared/StreamLinkButton";
import { ScrollDownButton } from "@/components/layout/SiteChrome";
import { pickHeroMp4Url, pickHeroPosterUrl } from "@/lib/hero-video";
import { formatImageUrl } from "@/lib/utils";
import {
  PatternBottomRight,
  PatternTopLeftDesktop,
  PatternTopLeftMobile,
} from "@/components/layout/HeroPatterns";
import { TowerSelectDesktop } from "@/components/layout/TowerSelect";
import type { TowerChildPage } from "@/types/page";

interface HeroProps {
  hero: HeroData;
  locale: string;
  towerChildren?: TowerChildPage[];
}

/** Page hero band (title, media, links, logos). */
export function Hero({ hero, locale, towerChildren }: HeroProps) {
  const {
    title,
    text,
    text_align = "left",
    mobile_half_height = true,
    video,
    images = [],
    links = [],
    tower_detail,
    text_html,
  } = hero;

  const hasContent = title || text || text_html || links.length > 0 || tower_detail;

  const hasVideo = Boolean(video?.transcodes?.length);
  const mp4Url = hasVideo ? pickHeroMp4Url(video) : undefined;
  const posterUrl = hasVideo ? pickHeroPosterUrl(video, images) : undefined;
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const el = videoRef.current;
    if (!el || !mp4Url) return;

    const tryPlay = () => {
      void el.play().catch(() => {});
    };

    tryPlay();
    el.addEventListener("loadeddata", tryPlay);
    return () => el.removeEventListener("loadeddata", tryPlay);
  }, [mp4Url]);

  return (
    <div
      id="heroBanner"
      className={`hero-banner text-layout-${text_align}${mobile_half_height ? " mobileHalfHeight" : ""}${hasVideo ? " has-video" : ""}`}
    >
      {hasVideo ? (
        <div className="video-wrapper">
          <video
            ref={videoRef}
            src={mp4Url}
            muted
            playsInline
            autoPlay
            loop
            preload="auto"
            poster={posterUrl}
            className="bg-video"
          />
        </div>
      ) : null}

      {images.length > 0 && !hasVideo ? (
        <div className="banner-bg active">
          {images.length === 1 ? (
            <div
              className="hero-image"
              style={{ backgroundImage: `url(${formatImageUrl(images[0].url)})` }}
            />
          ) : (
            <Swiper
              modules={[Autoplay, EffectFade]}
              autoplay={{ delay: 5000, pauseOnMouseEnter: true }}
              effect="fade"
              fadeEffect={{ crossFade: true }}
              speed={1000}
              loop
              className="hero-swiper"
            >
              {images.map((img) => (
                <SwiperSlide key={img.id}>
                  <div
                    className="hero-image"
                    style={{ backgroundImage: `url(${formatImageUrl(img.url)})` }}
                  />
                </SwiperSlide>
              ))}
            </Swiper>
          )}
        </div>
      ) : null}

      {hasContent && (
        <div className={`content${tower_detail ? " tower" : ""}`}>
          {title ? <h1>{title}</h1> : null}
          {tower_detail ? (
            <div className="tower-detail">
              <h1 className="number">{tower_detail.number}</h1>
              <h2>
                Gilmore <br />
                <span>Place</span>
              </h2>
            </div>
          ) : null}
          {text_html ? (
            <div className="h3 subhead white">
              <RichTextRenderer html={text_html} />
            </div>
          ) : text ? (
            <div className="h3 subhead white">
              {text.split("\n").map((line, i) => (
                <span key={i}>
                  {i > 0 && <br />}
                  {line}
                </span>
              ))}
            </div>
          ) : null}
          {links.length > 0 ? (
            <div className="related-links">
              {links.map((link) => (
                <StreamLinkButton key={link.id} link={link} locale={locale} />
              ))}
            </div>
          ) : null}
        </div>
      )}

      {towerChildren?.length ? (
        <TowerSelectDesktop towers={towerChildren} locale={locale} />
      ) : null}

      <PatternTopLeftMobile />
      <PatternTopLeftDesktop />
      <PatternBottomRight />
      {title || text || text_html || tower_detail ? (
        <ScrollDownButton
          src="/images/scroll-down-icon.svg"
          alt=""
          className="scroll-down-icon"
        />
      ) : null}
    </div>
  );
}
