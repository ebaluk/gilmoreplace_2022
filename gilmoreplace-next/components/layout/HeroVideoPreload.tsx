/**
 * Site layout: HeroVideoPreload.
 */

interface HeroVideoPreloadProps {
  mp4Url?: string;
  posterUrl?: string;
}

/** Server component: hoisted <link> hints so video/poster fetch starts before client Hero mounts. */
/** SSR <link rel=preload> tags for hero mp4/poster. */
export function HeroVideoPreload({ mp4Url, posterUrl }: HeroVideoPreloadProps) {
  if (!mp4Url && !posterUrl) return null;

  return (
    <>
      {posterUrl ? (
        <link rel="preload" as="image" href={posterUrl} fetchPriority="high" />
      ) : null}
      {mp4Url ? (
        <link rel="preload" as="video" href={mp4Url} type="video/mp4" />
      ) : null}
    </>
  );
}
