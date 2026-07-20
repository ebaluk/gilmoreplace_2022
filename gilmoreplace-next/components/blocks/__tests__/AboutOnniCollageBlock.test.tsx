import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AboutOnniCollageBlock } from "@/components/blocks/AboutOnniCollageBlock";
import type { StreamFieldBlock } from "@/types/page";

describe("AboutOnniCollageBlock", () => {
  const block: StreamFieldBlock = {
    type: "about_collage",
    id: "collage-1",
    value: {
      title: "FOR MORE INFORMATION ABOUT ONNI, VISIT OUR WEBSITE",
      resolved_image_groups: [
        {
          resolved_images: [
            {
              title: "CentreView, North Vancouver",
              resolved_image: { url: "/media_files/images/a.jpg", alt: "a" },
            },
            {
              title: "Evelyn, West Vancouver",
              resolved_image: { url: "/media_files/images/b.jpg", alt: "b" },
            },
          ],
        },
        {
          resolved_images: [
            {
              title: "Central, Vancouver",
              resolved_image: { url: "/media_files/images/c.jpg", alt: "c" },
            },
            {
              title: "Level Furnished Living, Los Angeles",
              resolved_image: { url: "/media_files/images/d.jpg", alt: "d" },
            },
          ],
        },
      ],
    },
  };

  it("renders collage groups with alternating tall and short images", () => {
    render(<AboutOnniCollageBlock block={block} />);

    expect(screen.getByRole("article")).toHaveClass("about-onni-block");
    expect(screen.getAllByText(/Vancouver|Los Angeles/)).toHaveLength(4);

    const images = document.querySelectorAll(".about-onni-block .image");
    expect(images[0]).toHaveClass("tall");
    expect(images[1]).toHaveClass("short");
    expect(images[2]).toHaveClass("short");
    expect(images[3]).toHaveClass("tall");
  });

  it("renders the Onni.com CTA", () => {
    render(<AboutOnniCollageBlock block={block} />);

    const link = screen.getByRole("link", { name: "Onni.com" });
    expect(link).toHaveAttribute("href", "https://www.onni.com/");
    expect(link).toHaveAttribute("target", "_blank");
  });

  it("returns null when there are no image groups", () => {
    const emptyBlock: StreamFieldBlock = {
      type: "about_collage",
      id: "empty",
      value: { resolved_image_groups: [] },
    };

    const { container } = render(<AboutOnniCollageBlock block={emptyBlock} />);
    expect(container).toBeEmptyDOMElement();
  });
});
