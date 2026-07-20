/**
 * Site layout: ThemeStyles.
 */

import { getThemes } from "@/lib/api/client";

export async function ThemeStyles() {
  let css = "";
  try {
    const { themes } = await getThemes();
    css = themes.map((theme) => theme.rendered_css || "").join("\n");
  } catch {
    // API unavailable during build or offline — static theme rules in site.css still apply
  }

  if (!css) return null;

  return <style dangerouslySetInnerHTML={{ __html: css }} />;
}
