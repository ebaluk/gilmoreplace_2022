"use client";


/**
 * Stream-field block UI for `TowerPlansBlock`.
 */
import { useState } from "react";
import type { StreamFieldBlock } from "@/types/page";
import { FloorPlanOverlayShell } from "@/components/shared/FloorPlanOverlayShell";
import { apiLocaleFromRoute } from "@/lib/i18n/config";
import { formatImageUrl } from "@/lib/utils";

interface BedroomType {
  id: number;
  title: string;
  title_zh_hans: string;
  title_zh_hant: string;
  sort_order: number;
  apartments: TowerPlan[];
}

interface TowerPlan {
  id: number;
  title: string;
  sold: boolean;
  interiors: string;
  exteriors: string;
  pdf_url: string | null;
  floorplan_image_url: string | null;
  floorplates_image_url: string | null;
  floorplates_images: string[];
  layout: "horizontal" | "vertical";
}

interface TowerPlansValue {
  title?: string;
  title_2?: string;
  theme?: { id: number; css_class: string | null } | null;
  apartment_types?: BedroomType[];
}

interface ModalState {
  plan: TowerPlan;
  apartmentTypeTitle: string;
}

function localizedTypeTitle(type: BedroomType, locale: string): string {
  const apiLocale = apiLocaleFromRoute(locale);
  if (apiLocale === "zh-hans" && type.title_zh_hans) return type.title_zh_hans;
  if (apiLocale === "zh-hant" && type.title_zh_hant) return type.title_zh_hant;
  return type.title;
}

/** Wagtail "tower_plans" floor-plan selector. */
export function TowerPlansBlock({
  block,
  locale,
}: {
  block: StreamFieldBlock;
  locale: string;
}) {
  const value = block.value as unknown as TowerPlansValue;
  const { apartment_types = [] } = value;

  const [selectedTypeId, setSelectedTypeId] = useState(
    () => String(apartment_types[0]?.id ?? "")
  );
  const [modal, setModal] = useState<ModalState | null>(null);

  if (!apartment_types.length) return null;

  return (
    <div className="section-plans">
      <div className="plans">
        <section>
          <span className="select-container select-box">
            <select
              required
              className="light"
              value={selectedTypeId}
              onChange={(e) => setSelectedTypeId(e.target.value)}
            >
              {apartment_types.map((type) => (
                <option key={type.id} value={String(type.id)}>
                  {localizedTypeTitle(type, locale)}
                </option>
              ))}
            </select>
          </span>

          {apartment_types.map((type) => (
            <div
              key={type.id}
              className={`appartment-type${String(type.id) === selectedTypeId ? " active" : ""}`}
              data-apartment-type={type.id}
            >
              <div className="list-container">
                {type.apartments.map((plan, i) => (
                  <div
                    key={plan.id}
                    className={`card${plan.sold ? " sold" : ""}`}
                    style={{ animationDelay: `${0.15 * (i + 1)}s` }}
                    onClick={() => {
                      if (!plan.sold) {
                        setModal({
                          plan,
                          apartmentTypeTitle: localizedTypeTitle(type, locale),
                        });
                      }
                    }}
                  >
                    <h2>{plan.title}</h2>
                    <div className="area">
                      <p>INT {plan.interiors} SF</p>
                      <p>EXT {plan.exteriors} SF</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>

        {modal && (
          <TowerPlanOverlay
            plan={modal.plan}
            apartmentTypeTitle={modal.apartmentTypeTitle}
            onClose={() => setModal(null)}
          />
        )}
      </div>
    </div>
  );
}

function TowerPlanOverlay({
  plan,
  apartmentTypeTitle,
  onClose,
}: {
  plan: TowerPlan;
  apartmentTypeTitle: string;
  onClose: () => void;
}) {
  const kpCount = plan.floorplates_images.length;

  return (
    <FloorPlanOverlayShell
      wrapperClassName="section-plans"
      kpCount={kpCount}
      onClose={onClose}
    >
      <div className="features">
        <h2>{plan.title}</h2>
        <div className="info-wrapper">
          <div className="info">{apartmentTypeTitle}</div>
          <div className="area">
            <div>
              <h4>Interiors</h4>
              <p>
                <span>{plan.interiors}</span> SF
              </p>
            </div>
            <div>
              <h4>Exteriors</h4>
              <p>
                <span>{plan.exteriors}</span> SF
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
