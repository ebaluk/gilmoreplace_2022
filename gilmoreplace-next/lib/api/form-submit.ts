/**
 * Form POST helpers for WtForm headless submit.
 * Uses the public origin (`NEXT_PUBLIC_API_URL`) so uploads work from the browser.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** JSON body from POST /api/v2/headless/forms/<id>/submit/ */
export interface FormSubmitResult {
  status: string;
  message_text?: string;
  message_title?: string;
  thank_you_url?: string;
  error?: string;
  errors?: Record<string, string[]>;
}

/** Thrown when HTTP fails or `status !== "success"`. */
export class FormSubmitError extends Error {
  constructor(public result: FormSubmitResult) {
    super(result.error || "Submission failed");
  }
}

/**
 * Submit multipart form data to a WtForm endpoint.
 *
 * @throws {FormSubmitError} On non-OK HTTP or API `status` other than success
 */
export async function submitForm(
  formId: number,
  formData: FormData,
): Promise<FormSubmitResult> {
  const res = await fetch(`${API_URL}/api/v2/headless/forms/${formId}/submit/`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new FormSubmitError({
      status: "error",
      error: `Server error: ${res.status}`,
    });
  }
  const result = (await res.json()) as FormSubmitResult;
  if (result.status !== "success") {
    throw new FormSubmitError(result);
  }
  return result;
}
