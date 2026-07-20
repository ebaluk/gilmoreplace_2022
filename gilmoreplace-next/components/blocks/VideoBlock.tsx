"use client";


/**
 * Stream-field block UI for `VideoBlock`.
 */
import { useRef, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface VideoValue {
  title?: string;
  show_controls?: boolean;
  resolved_poster?: { url: string; alt: string } | null;
  resolved_transcodes?: { url: string; mime: string }[];
  resolved_video?: {
    transcodes?: { url: string; mime: string }[];
    poster_url?: string;
  } | null;
  theme?: { id: number; css_class: string | null } | null;
}

/** Wagtail "video" block with optional play overlay. */
export function VideoBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as VideoValue;
  const {
    title,
    show_controls = false,
    resolved_poster,
    resolved_transcodes: resolvedTranscodes,
    resolved_video,
    theme,
  } = value;

  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const resolved_transcodes =
    resolvedTranscodes?.length
      ? resolvedTranscodes
      : resolved_video?.transcodes || [];

  const posterUrl = resolved_poster?.url
    ? formatImageUrl(resolved_poster.url)
    : resolved_video?.poster_url
      ? formatImageUrl(resolved_video.poster_url)
      : undefined;

  if (!resolved_transcodes.length) return null;

  const togglePlayback = () => {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) {
      void video.play();
      setIsPlaying(true);
    } else {
      video.pause();
      setIsPlaying(false);
    }
  };

  return (
    <article
      className={cn(
        "video-block-wrapper site-container",
        theme?.id ? `themed-${theme.id}` : "",
        theme?.css_class || ""
      )}
    >
      {title && <h2 className="title h1 text-center">{title}</h2>}

      <div
        className="video-block"
        onClick={show_controls ? undefined : togglePlayback}
        role={show_controls ? undefined : "button"}
        tabIndex={show_controls ? undefined : 0}
        onKeyDown={
          show_controls
            ? undefined
            : (e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  togglePlayback();
                }
              }
        }
      >
        <video
          ref={videoRef}
          controls={show_controls}
          playsInline
          {...(posterUrl ? { poster: posterUrl } : {})}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        >
          {resolved_transcodes.map((t, i) => (
            <source key={i} src={formatImageUrl(t.url)} type={t.mime} />
          ))}
        </video>
        {!show_controls && !isPlaying && (
          <span className="sr-only">Click to play video</span>
        )}
      </div>
    </article>
  );
}
