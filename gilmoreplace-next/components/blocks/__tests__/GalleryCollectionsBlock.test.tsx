import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GalleryCollectionsBlock } from "@/components/blocks/GalleryCollectionsBlock";
import type { StreamFieldBlock } from "@/types/page";

vi.mock("@/components/shared/ModalCarousel", () => ({
  ModalCarousel: ({ onClose, open }: { onClose: () => void; open?: boolean }) =>
    open ? (
      <div data-testid="gallery-modal">
        <button type="button" onClick={onClose}>
          Close
        </button>
      </div>
    ) : null,
}));

describe("GalleryCollectionsBlock", () => {
  const block: StreamFieldBlock = {
    type: "gallery_collections",
    id: "gallery-1",
    value: {
      title: "Gallery",
      mode: "6",
      show_categories: false,
      resolved_images: [
        { id: 1, url: "/media/a.jpg", alt: "A" },
        { id: 2, url: "/media/b.jpg", alt: "B" },
      ],
    },
  };

  it("renders gallery thumbnails", () => {
    render(<GalleryCollectionsBlock block={block} />);
    expect(document.querySelectorAll(".gallery-tile.gallery-tile--square")).toHaveLength(2);
  });

  it("opens modal carousel on thumbnail click", () => {
    render(<GalleryCollectionsBlock block={block} />);
    fireEvent.click(document.querySelectorAll(".gallery-tile.gallery-tile--square")[0]!);
    expect(screen.getByTestId("gallery-modal")).toBeInTheDocument();
  });
});
