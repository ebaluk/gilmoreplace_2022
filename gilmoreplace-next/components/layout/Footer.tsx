/**
 * Site layout: Footer.
 */

import Link from "next/link";
import { type NavItem } from "@/lib/api/client";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface FooterProps {
  locale: string;
  nav: NavItem[];
  footerData?: {
    phone?: string;
    email?: string;
    footer_legal?: string;
    footer_social_links?: { title: string; fontawesome_icon: string; link: string; new_window: boolean }[];
    footer_links?: any[];
  };
}

/** Site footer: legal, social, contact. */
export function Footer({ locale, nav, footerData }: FooterProps) {
  if (!footerData) return null;

  return (
    <footer>
      <div className={cn("footer-content", siteContainerClass)}>
        <div className="footer-links">
          <ul>
            {nav.map((item) => (
              <li key={item.id}>
                <Link href={item.url}>{item.title}</Link>
                {item.children.length > 0 && (
                  <ul>
                    {item.children.map((child) => (
                      <li key={child.id}>
                        <Link href={child.url}>{child.title}</Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="footer-contact">
          {footerData.phone && (
            <a href={`tel:${footerData.phone}`} className="footer-phone">
              {footerData.phone}
            </a>
          )}
          {footerData.email && (
            <a href={`mailto:${footerData.email}`} className="footer-email">
              {footerData.email}
            </a>
          )}
        </div>

        {footerData.footer_social_links?.length ? (
          <div className="footer-social">
            {footerData.footer_social_links.map((social, i) => (
              <a
                key={i}
                href={social.link}
                target={social.new_window ? "_blank" : undefined}
                rel={social.new_window ? "noopener noreferrer" : undefined}
                title={social.title}
              >
                <i className={`fa ${social.fontawesome_icon}`} />
              </a>
            ))}
          </div>
        ) : null}
      </div>

      {footerData.footer_legal && (
        <div className="footer-legal">
          <div
            className={siteContainerClass}
            dangerouslySetInnerHTML={{ __html: footerData.footer_legal }}
          />
        </div>
      )}
    </footer>
  );
}
