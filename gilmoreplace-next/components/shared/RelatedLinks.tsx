/**
 * Shared UI: RelatedLinks.
 */

import { StreamLinkButton } from "@/components/shared/StreamLinkButton";

interface LinkItem {
  type: string;
  value: {
    title?: string;
    link_type?: string;
    link?: string | number;
    new_window?: boolean;
    resolved_link?: { url: string } | null;
  };
}

interface RelatedLinksProps {
  links: {
    align?: string;
    description?: string;
    links?: LinkItem[];
  };
  locale: string;
  btnClass?: string;
}

/** List of StreamLinkButtons under related-links markup. */
export function RelatedLinks({ links, locale, btnClass }: RelatedLinksProps) {
  if (!links.links?.length) return null;

  return (
    <div className={`related-links uppercase${links.align ? ` ${links.align}` : ""}`}>
      {links.description && <p>{links.description}</p>}
      <div className="links">
        {links.links.map((link, i) => (
          <StreamLinkButton key={i} link={link} locale={locale} className={btnClass} />
        ))}
      </div>
    </div>
  );
}
