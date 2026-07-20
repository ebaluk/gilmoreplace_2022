import { describe, it, expect, vi, beforeEach } from "vitest";
import { submitForm, FormSubmitError } from "@/lib/api/form-submit";

const API_URL = "http://localhost:8000";

beforeEach(() => {
  vi.restoreAllMocks();
});

function mockFetch(status: number, body: unknown) {
  return vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  } as Response);
}

function makeFormData(data: Record<string, string>) {
  const fd = new FormData();
  Object.entries(data).forEach(([k, v]) => fd.append(k, v));
  return fd;
}

describe("FormSubmitError", () => {
  it("uses result.error as message when present", () => {
    const err = new FormSubmitError({
      status: "error",
      error: "Something went wrong",
    });
    expect(err.message).toBe("Something went wrong");
    expect(err.result.status).toBe("error");
  });

  it('falls back to "Submission failed" when no error field', () => {
    const err = new FormSubmitError({ status: "error" });
    expect(err.message).toBe("Submission failed");
  });
});

describe("submitForm", () => {
  it("returns result on successful submission", async () => {
    const result = {
      status: "success",
      message_text: "Thank you!",
      message_title: "Success",
    };
    mockFetch(200, result);

    const response = await submitForm(1, makeFormData({ name: "Test" }));

    expect(response.status).toBe("success");
    expect(response.message_text).toBe("Thank you!");
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/api/v2/headless/forms/1/submit/`,
      expect.objectContaining({ method: "POST" })
    );
  });

  it("throws FormSubmitError on non-ok response (Server error)", async () => {
    mockFetch(500, "Internal Server Error");

    await expect(
      submitForm(1, makeFormData({ name: "Test" }))
    ).rejects.toThrow(FormSubmitError);

    await expect(
      submitForm(1, makeFormData({ name: "Test" }))
    ).rejects.toThrow("Server error: 500");
  });

  it("throws FormSubmitError on 404 response", async () => {
    mockFetch(404, "Not Found");

    await expect(
      submitForm(99, makeFormData({ name: "Test" }))
    ).rejects.toThrow("Server error: 404");
  });

  it("throws FormSubmitError when result.status is not success", async () => {
    const errorResult = {
      status: "error",
      error: "Validation failed",
      errors: { email: ["This field is required."] },
    };
    mockFetch(200, errorResult);

    await expect(
      submitForm(1, makeFormData({ name: "Test" }))
    ).rejects.toThrow(FormSubmitError);

    await expect(
      submitForm(1, makeFormData({ name: "Test" }))
    ).rejects.toThrow("Validation failed");
  });

  it("throws FormSubmitError on network failure", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(
      new TypeError("Failed to fetch")
    );

    await expect(
      submitForm(1, makeFormData({ name: "Test" }))
    ).rejects.toThrow("Failed to fetch");
  });

  it("sends FormData in the request body", async () => {
    mockFetch(200, { status: "success" });
    const fd = makeFormData({ email: "test@example.com" });

    await submitForm(1, fd);

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ body: fd })
    );
  });
});
