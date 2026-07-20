"use client";


/**
 * Stream-field block UI for `PenthousesWidgetBlock`.
 */
import Link from "next/link";
import { useMemo, useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { formatImageUrl } from "@/lib/utils";
import { FormAnchorLink } from "@/components/layout/FormAnchorLink";
import { wagtailUrlToNextPath } from "@/lib/urls";
import { apiLocaleFromRoute } from "@/lib/i18n/config";
import { FloorPlanOverlayShell } from "@/components/shared/FloorPlanOverlayShell";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { Button } from "@/components/ui/button";
import { siteContainerClass } from "@/components/layout/SiteContainer";
import { cn } from "@/lib/utils";

interface PenthouseType {
  id: number;
  title: string;
  title_zh_hans: string;
  title_zh_hant: string;
  sort_order: number;
}

interface PenthousePlan {
  id: number;
  title: string;
  sold: boolean;
  interiors: string;
  exteriors: string;
  total_sqft: string;
  penthouse_type: PenthouseType | null;
  pdf_url: string | null;
  floorplan_image_url: string | null;
  floorplates_image_url: string | null;
  floorplates_images: string[];
  layout: "horizontal" | "vertical";
}

interface PenthouseTower {
  id: number;
  title: string;
  penthouse_type_ids: number[];
  plans: PenthousePlan[];
}

interface PenthousesWidgetValue {
  title?: string;
  title_2?: string;
  text?: string;
  penthouse_types?: PenthouseType[];
  towers?: PenthouseTower[];
}

function localizedTypeTitle(pt: PenthouseType, locale: string): string {
  const apiLocale = apiLocaleFromRoute(locale);
  if (apiLocale === "zh-hans" && pt.title_zh_hans) return pt.title_zh_hans;
  if (apiLocale === "zh-hant" && pt.title_zh_hant) return pt.title_zh_hant;
  return pt.title;
}

/** Wagtail "penthouses_widget" tower/unit finder. */
export function PenthousesWidgetBlock({
  block,
  locale,
}: {
  block: StreamFieldBlock;
  locale: string;
}) {
  const value = block.value as unknown as PenthousesWidgetValue;
  const { title, title_2, text, penthouse_types = [], towers = [] } = value;

  const [typeFilter, setTypeFilter] = useState("cat-all");
  const [visibleTowers, setVisibleTowers] = useState<Set<number>>(
    () => new Set(towers.map((t) => t.id))
  );
  const [modalPlan, setModalPlan] = useState<PenthousePlan | null>(null);

  const contactHref = `${wagtailUrlToNextPath("/en/contact-us/", locale)}#form`;

  const towerTypeClasses = useMemo(() => {
    const map = new Map<number, string>();
    for (const tower of towers) {
      const cats = ["cat-all", ...tower.penthouse_type_ids.map((id) => `cat-${id}`)];
      map.set(tower.id, cats.join(" "));
    }
    return map;
  }, [towers]);

  if (!towers.length) return null;

  const isPlanVisible = (plan: PenthousePlan) => {
    if (typeFilter === "cat-all") return true;
    return plan.penthouse_type?.id === Number(typeFilter.replace("cat-", ""));
  };

  const isTowerVisible = (tower: PenthouseTower) => {
    if (!visibleTowers.has(tower.id)) return false;
    if (typeFilter === "cat-all") return true;
    return tower.penthouse_type_ids.includes(Number(typeFilter.replace("cat-", "")));
  };

  return (
    <article className={cn("penthouses-block", siteContainerClass)}>
      <div className="penthouses-widget">
        <div className="plans">
          <section>
            {title && (
              <h2 className="title h1 text-center">
                {title}
                {title_2 && (
                  <>
                    <br />
                    <span>
                      {title_2.split("\n").map((line, i) => (
                        <span key={i}>
                          {i > 0 && <br />}
                          {line}
                        </span>
                      ))}
                    </span>
                  </>
                )}
              </h2>
            )}
            {text && (
              <div className="text-center">
                <RichTextRenderer html={text} />
              </div>
            )}

            <div className="text-center penthouse-type-filter">
              <div className="tower-toggle-group">
                {towers.map((tower) => (
                  <Button
                    key={tower.id}
                    type="button"
                    variant="gold"
                    className={cn(
                      "tower-toggle",
                      visibleTowers.has(tower.id) && "active"
                    )}
                    onClick={() => {
                      setVisibleTowers((prev) => {
                        const next = new Set(prev);
                        if (next.has(tower.id)) next.delete(tower.id);
                        else next.add(tower.id);
                        return next;
                      });
                    }}
                  >
                    Tower {tower.title}
                  </Button>
                ))}
              </div>

              <div>
                <label className="subhead white">Filter: &nbsp;</label>
                <span className="select-container select-box">
                  <select
                    required
                    className="light"
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                  >
                    <option value="cat-all">All</option>
                    {penthouse_types.map((pt) => (
                      <option key={pt.id} value={`cat-${pt.id}`}>
                        {localizedTypeTitle(pt, locale)}
                      </option>
                    ))}
                  </select>
                </span>
              </div>
            </div>

            {towers.map((tower) => {
              const visible = isTowerVisible(tower);
              const typeClasses = towerTypeClasses.get(tower.id) || "cat-all";
              return (
                <div
                  key={tower.id}
                  data-tower-id={tower.id}
                  className={`tower-item${visible ? " active in" : ""} ${typeClasses}`}
                >
                  <h3 className="title text-center">Tower {tower.title}</h3>
                  <div className="penthouses-list">
                    {tower.plans.map((plan) => {
                      const planVisible = visible && isPlanVisible(plan);
                      const planCats = [
                        "cat-all",
                        plan.penthouse_type ? `cat-${plan.penthouse_type.id}` : "",
                      ]
                        .filter(Boolean)
                        .join(" ");
                      return (
                        <div
                          key={plan.id}
                          className={`penthouse${plan.sold ? " sold" : ""}${planVisible ? " active" : ""} ${planCats}`}
                        >
                          <div>
                            <div className="title-wrapper">
                              <h4>
                                <small>plan</small> {plan.title}
                              </h4>
                              {plan.penthouse_type && (
                                <p>{localizedTypeTitle(plan.penthouse_type, locale)}</p>
                              )}
                            </div>

                            <div className="image">
                              <div
                                style={
                                  plan.floorplan_image_url
                                    ? {
                                        backgroundImage: `url(${formatImageUrl(plan.floorplan_image_url)})`,
                                      }
                                    : undefined
                                }
                              >
                                {plan.floorplan_image_url && (
                                  <img
                                    className="sr-only"
                                    src={formatImageUrl(plan.floorplan_image_url)}
                                    alt={plan.title}
                                  />
                                )}
                              </div>
                            </div>

                            <div className="sqft-total">
                              <div>TOTAL {plan.total_sqft} sqft</div>
                            </div>

                            <div className="sqft cols">
                              <div>Indoor {plan.interiors} sqft</div>
                              <div>Outdoor {plan.exteriors} sqft</div>
                            </div>

                            <div className="buttons cols">
                              <div>
                                <Button
                                  type="button"
                                  variant="gold"
                                  className="penthouse-action-btn view-floor-plan w-full"
                                  onClick={() => setModalPlan(plan)}
                                >
                                  Floor Plan
                                </Button>
                              </div>
                              <div>
                                <Button asChild className="penthouse-action-btn w-full">
                                  <FormAnchorLink href={contactHref}>Contact Us</FormAnchorLink>
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}

            {modalPlan && (
              <FloorPlanOverlay plan={modalPlan} locale={locale} onClose={() => setModalPlan(null)} />
            )}
          </section>
        </div>
      </div>
    </article>
  );
}

function FloorPlanOverlay({
  plan,
  locale,
  onClose,
}: {
  plan: PenthousePlan;
  locale: string;
  onClose: () => void;
}) {
  const kpCount = plan.floorplates_images.length;

  return (
    <FloorPlanOverlayShell
      wrapperClassName="section-plans penthouses-widget"
      kpCount={kpCount}
      onClose={onClose}
    >
      <div className="features">
          <h2>{plan.title}</h2>
          <div className="info-wrapper">
            <div className="info">{plan.penthouse_type ? localizedTypeTitle(plan.penthouse_type, locale) : ""}</div>
            <div className="area">
              <div>
                <h4>Total</h4>
                <p>
                  <span>{plan.total_sqft}</span> SqFt
                </p>
              </div>
              <div>
                <h4>Indoor</h4>
                <p>
                  <span>{plan.interiors}</span> SqFt
                </p>
              </div>
              <div>
                <h4>Outdoor</h4>
                <p>
                  <span>{plan.exteriors}</span> SqFt
                </p>
              </div>
            </div>
          </div>
        </div>

        {plan.floorplan_image_url && (
          <div
            id="apartment-floorplan"
            className={`floorplan-img ${plan.layout}`}
            style={{
              backgroundImage: `url(${formatImageUrl(plan.floorplan_image_url)})`,
            }}
          />
        )}

        <div className="keyplates-wrapper">
          {plan.pdf_url && (
            <a
              href={formatImageUrl(plan.pdf_url)}
              target="_blank"
              rel="noopener noreferrer"
              className="pdf-button"
            >
              Download PDF
            </a>
          )}
          {kpCount > 0 && (
            <div id="apartment-keyplates-desktop" className="keyplates">
              <div className="kp-title">
                NORTH <i className="fa fa-arrow-circle-up" aria-hidden="true" />
              </div>
              <div className="kp-items">
                {plan.floorplates_images.map((url, i) => (
                  <img key={i} src={formatImageUrl(url)} alt="" />
                ))}
              </div>
            </div>
          )}
        </div>
    </FloorPlanOverlayShell>
  );
}
