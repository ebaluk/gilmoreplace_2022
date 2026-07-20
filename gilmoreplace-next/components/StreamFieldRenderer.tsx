/**
 * Maps Wagtail stream_field blocks to React block components.
 */

import { type StreamFieldBlock } from "@/types/page";
import { TextBlock } from "@/components/blocks/TextBlock";
import { ImageBlock } from "@/components/blocks/ImageBlock";
import { VideoBlock } from "@/components/blocks/VideoBlock";
import { GalleryBlock } from "@/components/blocks/GalleryBlock";
import { AboutOnniCollageBlock } from "@/components/blocks/AboutOnniCollageBlock";
import { GalleryCollectionsBlock } from "@/components/blocks/GalleryCollectionsBlock";
import { CarouselBlock } from "@/components/blocks/CarouselBlock";
import { FeaturesBlock } from "@/components/blocks/FeaturesBlock";
import { InfoBlock } from "@/components/blocks/InfoBlock";
import { InteractiveMapBlock } from "@/components/blocks/InteractiveMapBlock";
import { InteractiveMapTabsBlock } from "@/components/blocks/InteractiveMapTabsBlock";
import { PlacesBlock } from "@/components/blocks/PlacesBlock";
import { TowerPlansBlock } from "@/components/blocks/TowerPlansBlock";
import { TowerViewsBlock } from "@/components/blocks/TowerViewsBlock";
import { ContactBlock } from "@/components/blocks/ContactBlock";
import { HashBlock } from "@/components/blocks/HashBlock";
import { RawHtmlBlock } from "@/components/blocks/RawHtmlBlock";
import { OnniLogoBlock } from "@/components/blocks/OnniLogoBlock";
import { InstagramBlock } from "@/components/blocks/InstagramBlock";
import { TextsAndImagesGallery } from "@/components/blocks/TextsAndImagesGallery";
import { SiteMapBlock } from "@/components/blocks/SiteMapBlock";
import { LazyFormBlock } from "@/components/blocks/LazyFormBlock";
import { PenthousesWidgetBlock } from "@/components/blocks/PenthousesWidgetBlock";

const blockComponents: Record<string, React.ComponentType<{ block: StreamFieldBlock; locale?: string }>> = {
  image: ImageBlock,
  video: VideoBlock,
  gallery: GalleryBlock,
  gallery_collections: GalleryCollectionsBlock,
  carousel: CarouselBlock,
  info: InfoBlock,
  interactive_map: InteractiveMapBlock,
  interactive_map_tabs: InteractiveMapTabsBlock,
  // Legacy/typoed block name seen in some environments during SSG.
  interactive_map_tabks: InteractiveMapTabsBlock,
  places: PlacesBlock,
  tower_views: TowerViewsBlock,
  contact: ContactBlock,
  hash: HashBlock,
  raw_html: RawHtmlBlock,
  onni_logo: OnniLogoBlock,
  instagram: InstagramBlock,
  site_map: SiteMapBlock,
  about_collage: AboutOnniCollageBlock,
  texts_and_images_gallery: TextsAndImagesGallery,
};

interface StreamFieldRendererProps {
  blocks: StreamFieldBlock[];
  locale: string;
}

/** Render an ordered list of StreamField blocks for a locale. */
export function StreamFieldRenderer({ blocks, locale }: StreamFieldRendererProps) {
  if (!blocks || blocks.length === 0) return null;

  return (
    <>
      {blocks.map((block) => {
        if (block.type === "form") {
          return <LazyFormBlock key={block.id} block={block} locale={locale} />;
        }

        if (block.type === "shared_blocks") {
          const nested =
            (block.value as { resolved_stream_field?: StreamFieldBlock[] })
              ?.resolved_stream_field ?? [];
          if (!nested.length) return null;
          return (
            <StreamFieldRenderer key={block.id} blocks={nested} locale={locale} />
          );
        }

        if (block.type === "paragraph") {
          return <TextBlock key={block.id} block={block} locale={locale} />;
        }

        if (block.type === "penthouses_widget") {
          return <PenthousesWidgetBlock key={block.id} block={block} locale={locale} />;
        }

        if (block.type === "features") {
          return <FeaturesBlock key={block.id} block={block} locale={locale} />;
        }

        if (block.type === "tower_plans") {
          return <TowerPlansBlock key={block.id} block={block} locale={locale} />;
        }

        const Component = blockComponents[block.type];
        if (!Component) {
          console.warn(`Unknown block type: ${block.type}`);
          return null;
        }
        return <Component key={block.id} block={block} locale={locale} />;
      })}
    </>
  );
}
