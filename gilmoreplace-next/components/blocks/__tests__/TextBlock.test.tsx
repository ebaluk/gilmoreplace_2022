import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TextBlock } from "@/components/blocks/TextBlock";
import type { StreamFieldBlock } from "@/types/page";

vi.mock("@/components/shared/RichTextRenderer", () => ({
  RichTextRenderer: ({ html }: { html: string }) => <div>{html}</div>,
}));

describe("TextBlock", () => {
  it("renders multiline title_2 and links without React key warnings", () => {
    const error = vi.spyOn(console, "error").mockImplementation(() => {});

    const block: StreamFieldBlock = {
      type: "paragraph",
      id: "p1",
      value: {
        title: "MORE PLACES",
        title_2: "TO\nSHOP",
        layout: "whole",
        text: "<p>Retail copy</p>",
        new_links: {
          links: [
            {
              type: "link",
              value: {
                title: "Learn more",
                link_type: "button",
                link: "/commercial/",
              },
            },
            {
              type: "onni_link",
              value: { title: "ONNI", new_window: true },
            },
          ],
        },
      },
    };

    render(<TextBlock block={block} locale="en" />);

    expect(screen.getByText("MORE PLACES")).toBeInTheDocument();
    expect(screen.getByText(/TO\s+SHOP/)).toBeInTheDocument();
    expect(screen.getByText("Learn more")).toBeInTheDocument();

    const keyWarnings = error.mock.calls.filter(([msg]) =>
      String(msg).includes('unique "key" prop'),
    );
    expect(keyWarnings).toHaveLength(0);

    error.mockRestore();
  });
});
