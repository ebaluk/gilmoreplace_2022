/**
 * Site layout: PageNavbar.
 */

import Link from "next/link";
import { type NavItem } from "@/lib/api/client";
import { type WagtailPage } from "@/types/page";
import { wagtailUrlToNextPath } from "@/lib/urls";

interface PageNavbarProps {
  page: WagtailPage;
  nav: NavItem[];
  locale: string;
}

function findNavItemById(items: NavItem[] | undefined | null, id: number): NavItem | null {
  if (!items || !Array.isArray(items)) return null;
  for (const item of items) {
    if (item.id === id) return item;
    const found = findNavItemById(item.children, id);
    if (found) return found;
  }
  return null;
}

function getNavbarItems(page: WagtailPage, nav: NavItem[]): NavItem[] {
  if (page.show_navbar) {
    const self = findNavItemById(nav, page.id);
    if (self?.children && self.children.length) return self.children;
    if (page.children?.length) {
      return page.children.map((child) => ({
        id: child.id,
        title: child.title,
        slug: child.slug,
        url: child.url,
        show_navbar: false,
        children: [],
      }));
    }
    return [];
  }

  if (page.parent) {
    const parent = findNavItemById(nav, page.parent.id);
    if (parent?.show_navbar && Array.isArray(parent.children) && parent.children.length) {
      return parent.children;
    }
  }

  return [];
}

/** In-page section navbar when show_navbar is set. */
export function PageNavbar({ page, nav, locale }: PageNavbarProps) {
  const items = getNavbarItems(page, nav);
  if (!items.length) return null;

  const currentPath = wagtailUrlToNextPath(page.url, locale);

  return (
    <>
      <a id="content" className="anchor" />
      <div id="filterWrapper" className="filter-wrapper">
        <ul id="filterGroup" className="filter-group">
          {items.map((item) => {
            const href = `${wagtailUrlToNextPath(item.url, locale)}#content`;
            const itemPath = wagtailUrlToNextPath(item.url, locale);
            const active =
              page.content_page_id === item.id || currentPath === itemPath;
            return (
              <li key={item.id} className={`filter${active ? " active" : ""}`}>
                <Link href={href}>{item.title}</Link>
              </li>
            );
          })}
        </ul>
      </div>
    </>
  );
}
