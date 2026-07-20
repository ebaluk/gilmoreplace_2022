/**
 * Pick hero background video / poster URLs from API hero payload.
 */

import { type HeroVideo, type ImageData } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";

function sortTranscodes(transcodes: HeroVideo["transcodes"]) {
  return [...transcodes].sort((a, b) => {
    const aMp4 = a.mime.includes("mp4");
    const bMp4 = b.mime.includes("mp4");
    if (aMp4 === bMp4) return 0;
    return aMp4 ? -1 : 1;
  });
}

/** Prefer first mp4 transcode URL (sorted), formatted for the client. */
export function pickHeroMp4Url(video: HeroVideo | null | undefined): string | undefined {
  const transcodes = video?.transcodes;
  if (!transcodes?.length) return undefined;
  const url = sortTranscodes(transcodes)[0]?.url;
  return url ? formatImageUrl(url) : undefined;
}

/** Poster from video.poster_url, else first hero image. */
export function pickHeroPosterUrl(
  video: HeroVideo | null | undefined,
  images: ImageData[] = [],
): string | undefined {
  if (video?.poster_url) return formatImageUrl(video.poster_url);
  if (images[0]?.url) return formatImageUrl(images[0].url);
  return undefined;
}
