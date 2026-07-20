/**
 * Site layout: TowerSelect.
 */

import Link from "next/link";
import type { TowerChildPage } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import { wagtailUrlToNextPath } from "@/lib/urls";

interface TowerSelectProps {
  towers: TowerChildPage[];
  locale: string;
}

/** Layout: TowerSelectDesktop. */
export function TowerSelectDesktop({ towers, locale }: TowerSelectProps) {
  if (!towers.length) return null;

  return (
    <div className="tower-select tower-select--desktop">
      <ul className="tower-select__list tower-select__list--desktop">
        {towers.map((tower, i) => (
          <li key={tower.id} className={`label label-${i + 1}`}>
            <Link href={wagtailUrlToNextPath(tower.url, locale)}>
              {tower.icon_desktop ? (
                <img
                  src={formatImageUrl(tower.icon_desktop.url)}
                  alt={tower.title}
                />
              ) : null}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Layout: TowerSelectMobile. */
export function TowerSelectMobile({ towers, locale }: TowerSelectProps) {
  if (!towers.length) return null;

  return (
    <div className="tower-select tower-select--mobile">
      <ul className="tower-select__list tower-select__list--mobile">
        {towers.map((tower, i) => (
          <li key={tower.id} className={`label label-${i + 1}`}>
            <Link href={wagtailUrlToNextPath(tower.url, locale)}>
              {tower.icon_mobile ? (
                <img
                  src={formatImageUrl(tower.icon_mobile.url)}
                  alt={tower.title}
                />
              ) : null}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
