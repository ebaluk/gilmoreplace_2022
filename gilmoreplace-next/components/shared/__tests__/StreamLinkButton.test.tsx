import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StreamLinkButton } from "@/components/shared/StreamLinkButton";

describe("StreamLinkButton", () => {
  it("maps link_type button to default white button, not purple", () => {
    render(
      <StreamLinkButton
        locale="en"
        link={{
          type: "doc_link",
          value: {
            title: "TOWER COLLECTION FEATURE SHEET",
            link_type: "button",
            new_window: true,
            resolved_link: {
              url: "/documents/106/feature-sheet.pdf",
            },
          },
        }}
      />,
    );

    const el = screen.getByRole("link", { name: /tower collection feature sheet/i });
    expect(el.className).toContain("bg-white");
    expect(el.className).not.toContain("bg-[#3A3687]");
  });

  it("maps link_type gold to gold button", () => {
    render(
      <StreamLinkButton
        locale="en"
        link={{
          type: "doc_link",
          value: {
            title: "PENTHOUSE COLLECTION FEATURE SHEET",
            link_type: "gold",
            new_window: true,
            resolved_link: {
              url: "/documents/162/feature-list.pdf",
            },
          },
        }}
      />,
    );

    const el = screen.getByRole("link", {
      name: /penthouse collection feature sheet/i,
    });
    expect(el.className).toContain("bg-[#C1A340]");
  });

  it("maps link_type reverse to inverted button", () => {
    render(
      <StreamLinkButton
        locale="en"
        link={{
          type: "external_page_link",
          value: {
            title: "Learn more",
            link_type: "reverse",
            link: "https://example.com",
            new_window: true,
          },
        }}
      />,
    );

    const el = screen.getByRole("link", { name: /learn more/i });
    expect(el.className).toContain("bg-transparent");
    expect(el.className).toContain("text-white");
  });

  it("maps link_type link to a text link", () => {
    render(
      <StreamLinkButton
        locale="en"
        link={{
          type: "external_page_link",
          value: {
            title: "Details",
            link_type: "link",
            link: "https://example.com/details",
          },
        }}
      />,
    );

    const el = screen.getByRole("link", { name: /details/i });
    expect(el.className).toContain("link");
    expect(el.className).not.toContain("bg-white");
  });
});
