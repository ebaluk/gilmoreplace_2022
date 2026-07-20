import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StreamFieldRenderer } from "@/components/StreamFieldRenderer";
import type { StreamFieldBlock } from "@/types/page";

vi.mock("@/components/shared/RichTextRenderer", () => ({
  RichTextRenderer: ({ html }: { html: string }) => <div>{html}</div>,
}));

vi.mock("@/components/shared/ModalCarousel", () => ({
  ModalCarousel: () => null,
}));

describe("StreamFieldRenderer integration", () => {
  it("renders known block types from a mixed stream field", () => {
    const blocks: StreamFieldBlock[] = [
      {
        type: "paragraph",
        id: "p1",
        value: {
          title: "MORE PLACES",
          title_2: "TO SHOP",
          layout: "whole",
          text_align: "center",
          text: "<p>Retail copy</p>",
        },
      },
      {
        type: "info",
        id: "i1",
        value: {
          title: "500,000+",
          items: [{ title: "THE SHOPS", text: "<p>Shops</p>" }],
        },
      },
      {
        type: "about_collage",
        id: "c1",
        value: {
          title: "Visit Onni",
          resolved_image_groups: [
            {
              resolved_images: [
                {
                  title: "Building A",
                  resolved_image: { url: "/media_files/images/a.jpg" },
                },
              ],
            },
          ],
        },
      },
      {
        type: "gallery_collections",
        id: "g1",
        value: {
          title: "Gallery",
          mode: "12",
          resolved_images: [{ id: 1, url: "/media_files/images/g.jpg", alt: "G" }],
        },
      },
    ];

    render(<StreamFieldRenderer blocks={blocks} locale="en" />);

    expect(screen.getByText("MORE PLACES")).toBeInTheDocument();
    expect(screen.getByText("500,000+")).toBeInTheDocument();
    expect(screen.getByText("Building A")).toBeInTheDocument();
    expect(screen.getByText("Gallery")).toBeInTheDocument();
  });

  it("ignores unknown block types without crashing", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    render(
      <StreamFieldRenderer
        blocks={[{ type: "unknown_block", id: "x", value: {} }]}
        locale="en"
      />,
    );

    expect(warn).toHaveBeenCalledWith("Unknown block type: unknown_block");
    warn.mockRestore();
  });
});
