import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InfoBlock } from "@/components/blocks/InfoBlock";
import type { StreamFieldBlock } from "@/types/page";

vi.mock("@/components/shared/RichTextRenderer", () => ({
  RichTextRenderer: ({ html }: { html: string }) => (
    <div data-testid="rich-text">{html}</div>
  ),
}));

describe("InfoBlock", () => {
  it("renders stat header and flat info items", () => {
    const block: StreamFieldBlock = {
      type: "info",
      id: "info-1",
      value: {
        title: "500,000+",
        title_2: "SQUARE FEET",
        items: [
          { title: "THE SHOPS", text: "<p>Shop copy</p>" },
          { title: "THE FLEXIBILITY", text: "<p>Flex copy</p>" },
        ],
      },
    };

    render(<InfoBlock block={block} />);

    expect(screen.getByRole("article")).toHaveClass("info-blocks");
    expect(screen.getByText("500,000+")).toBeInTheDocument();
    expect(screen.getByText("SQUARE FEET")).toBeInTheDocument();
    expect(screen.getByText("THE SHOPS")).toBeInTheDocument();
    expect(screen.getByText("<p>Shop copy</p>")).toBeInTheDocument();
  });

  it("normalizes nested Wagtail item structure", () => {
    const block: StreamFieldBlock = {
      type: "info",
      id: "info-2",
      value: {
        items: [
          {
            type: "item",
            id: "a",
            value: { title: "Nested title", text: "<p>Nested</p>" },
          },
        ],
      },
    };

    render(<InfoBlock block={block} />);

    expect(screen.getByText("Nested title")).toBeInTheDocument();
  });
});
