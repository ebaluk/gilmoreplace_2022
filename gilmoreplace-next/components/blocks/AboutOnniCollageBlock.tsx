/**
 * Stream-field block UI for `AboutOnniCollageBlock`.
 */

import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface CollageImage {
  title?: string;
  resolved_image?: {
    url: string;
    alt?: string;
  };
}

interface CollageGroup {
  resolved_images?: CollageImage[];
  images?: CollageImage[];
}

interface AboutCollageValue {
  title?: string;
  image_groups?: CollageGroup[];
  resolved_image_groups?: CollageGroup[];
}

function imageType(groupIndex: number, imageIndex: number): "tall" | "short" {
  const oddGroup = groupIndex % 2 === 0;
  if (oddGroup) {
    return imageIndex === 0 ? "tall" : "short";
  }
  return imageIndex === 0 ? "short" : "tall";
}

/** Wagtail About Onni collage. */
export function AboutOnniCollageBlock({ block }: { block: StreamFieldBlock }) {
  const value = block.value as unknown as AboutCollageValue;
  const { title } = value;
  const groups = value.resolved_image_groups ?? value.image_groups ?? [];

  if (!groups.length) return null;

  return (
    <article className={cn("about-onni-block", siteContainerClass)}>
      <div className="image-blocks">
        {groups.map((group, groupIndex) => {
          const images = group.resolved_images ?? group.images ?? [];
          return (
            <div key={groupIndex} className="image-group">
              {images.map((item, imageIndex) => {
                const img = item.resolved_image;
                if (!img?.url) return null;
                return (
                  <div
                    key={imageIndex}
                    className={`image ${imageType(groupIndex, imageIndex)}`}
                    style={{
                      backgroundImage: `url(${formatImageUrl(img.url)})`,
                    }}
                  >
                    {item.title && <p className="img-desc">{item.title}</p>}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
      <div className="site-link">
        {title && <h3 className="subhead">{title}</h3>}
        <Button asChild variant="reverse">
          <a href="https://www.onni.com/" target="_blank" rel="noopener noreferrer">
            Onni.com
          </a>
        </Button>
      </div>
    </article>
  );
}
