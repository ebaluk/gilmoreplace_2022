"use client";


/**
 * Stream-field block UI for `FormBlock`.
 */
import { useCallback, useMemo, useRef, useState, type ReactNode } from "react";
import { useForm, type FieldErrors } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import ReCAPTCHA from "react-google-recaptcha";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { type StreamFieldBlock } from "@/types/page";
import { type FormField, type FormResponse } from "@/lib/api/client";
import { FormSubmitError, submitForm } from "@/lib/api/form-submit";
import { formQuery } from "@/lib/api/queries";
import { wagtailUrlToNextPath } from "@/lib/urls";
import { Button } from "@/components/ui/button";
import { RichTextRenderer } from "@/components/shared/RichTextRenderer";
import { SiteContainer } from "@/components/layout/SiteContainer";

interface ResolvedForm {
  id: number;
  title: string;
  submit_url: string;
}

interface FormBlockValue {
  form_id: number;
  resolved_form?: ResolvedForm;
}

function buildFieldSchema(fields: FormField[]) {
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const field of fields) {
    if (["fieldsgroup", "sectiontitleh2", "sectiontitleh3"].includes(field.field_type)) continue;
    if (field.field_type === "checkbox") {
      shape[field.clean_name] = field.required
        ? z.literal(true, { errorMap: () => ({ message: "This field is required" }) })
        : z.boolean().optional();
    } else if (field.field_type === "checkboxes") {
      shape[field.clean_name] = field.required
        ? z.array(z.string()).min(1, "Please select at least one option")
        : z.array(z.string()).optional();
    } else if (field.field_type === "file") {
      shape[field.clean_name] = field.required
        ? z.any().refine((v) => v instanceof File || v !== null, "This field is required")
        : z.any().optional();
    } else if (field.field_type === "email") {
      shape[field.clean_name] = field.required
        ? z.string().min(1, "This field is required").email("Invalid email")
        : z.string().email("Invalid email").or(z.literal(""));
    } else if (field.field_type === "number") {
      shape[field.clean_name] = field.required
        ? z.string().min(1, "This field is required").refine((v) => !isNaN(Number(v)), "Must be a number")
        : z.string().refine((v) => !v || !isNaN(Number(v)), "Must be a number").or(z.literal(""));
    } else if (field.field_type === "url") {
      shape[field.clean_name] = field.required
        ? z.string().min(1, "This field is required").url("Invalid URL")
        : z.string().url("Invalid URL").or(z.literal(""));
    } else {
      shape[field.clean_name] = field.required
        ? z.string().min(1, "This field is required")
        : z.string().optional().or(z.literal(""));
    }
  }
  return z.object(shape);
}

function getDefaultValues(fields: FormField[]) {
  const defaults: Record<string, unknown> = {};
  for (const field of fields) {
    if (["fieldsgroup", "sectiontitleh2", "sectiontitleh3"].includes(field.field_type)) continue;
    if (field.field_type === "checkbox") {
      defaults[field.clean_name] = false;
    } else if (field.field_type === "checkboxes") {
      defaults[field.clean_name] = [];
    } else if (field.field_type === "file") {
      defaults[field.clean_name] = null;
    } else {
      defaults[field.clean_name] = field.default_value || "";
    }
  }
  return defaults;
}

function formatSubmitErrors(result: {
  error?: string;
  errors?: Record<string, string[]>;
}): string {
  if (result.errors) {
    const messages = Object.entries(result.errors).flatMap(([key, msgs]) =>
      msgs.map((msg) => (key === "__all__" ? msg : msg))
    );
    if (messages.length) return messages.join(" ");
  }
  return result.error || "Submission failed";
}

function appendFieldValue(
  formData: FormData,
  field: FormField,
  val: unknown
) {
  if (field.field_type === "file" && val instanceof File) {
    formData.append(field.clean_name, val);
  } else if (field.field_type === "checkbox") {
    if (val === true) {
      formData.append(field.clean_name, "on");
    }
  } else if (field.field_type === "checkboxes" && Array.isArray(val)) {
    for (const item of val) {
      formData.append(field.clean_name, item);
    }
  } else if (val !== undefined && val !== null && val !== "") {
    formData.append(field.clean_name, String(val));
  }
}

interface FormBlockSubmitState {
  submitted: boolean;
  submitError: string | null;
  messageText: string;
  messageTitle: string;
  thankYouUrl: string | null;
}

/** Wagtail form chooser — client form with mutation submit. */
export function FormBlock({
  block,
  locale,
}: {
  block: StreamFieldBlock;
  locale: string;
}) {
  const rawValue = block.value as unknown as FormBlockValue | number;
  const formId =
    typeof rawValue === "number"
      ? rawValue
      : rawValue.resolved_form?.id || rawValue.form_id;

  const {
    data: form,
    isPending: formLoading,
    isError: formLoadError,
    error: formLoadErrorDetail,
  } = useQuery(formQuery(formId ?? 0));

  if (!formId) return null;

  if (formLoading) {
    return (
      <article className="form-block page-layout-whole">
        <a className="form-anchor" id="form" aria-hidden="true" />
        <SiteContainer className="page-text-wrapper">
          <div className="form-links">
            <div className="text-center py-8">Loading form...</div>
          </div>
        </SiteContainer>
      </article>
    );
  }

  if (formLoadError) {
    return (
      <article className="form-block page-layout-whole">
        <a className="form-anchor" id="form" aria-hidden="true" />
        <SiteContainer className="page-text-wrapper">
          <div className="form-links">
            <div className="text-center py-8 text-red-500">
              Error: {formLoadErrorDetail?.message || "Failed to load form"}
            </div>
          </div>
        </SiteContainer>
      </article>
    );
  }

  if (!form) return null;

  return <FormBlockForm key={form.id} form={form} locale={locale} formId={formId} />;
}

function FormBlockForm({
  form,
  locale,
  formId,
}: {
  form: FormResponse;
  locale: string;
  formId: number;
}) {
  const router = useRouter();
  const [submitState, setSubmitState] = useState<FormBlockSubmitState>({
    submitted: false,
    submitError: null,
    messageText: "",
    messageTitle: "",
    thankYouUrl: null,
  });

  const formSchema = useMemo(() => buildFieldSchema(form.fields), [form.fields]);
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const recaptchaRef = useRef<ReCAPTCHA>(null);

  const submitMutation = useMutation({
    mutationFn: ({
      fields,
      data,
      token,
    }: {
      fields: FormField[];
      data: Record<string, unknown>;
      token: string | null;
    }) => {
      const formData = new FormData();
      for (const field of fields) {
        if (["fieldsgroup", "sectiontitleh2", "sectiontitleh3"].includes(field.field_type)) {
          continue;
        }
        appendFieldValue(formData, field, data[field.clean_name]);
      }
      if (token) {
        formData.append("g-recaptcha-response", token);
      }
      return submitForm(formId, formData);
    },
    onSuccess: (result) => {
      if (result.thank_you_url) {
        router.push(wagtailUrlToNextPath(result.thank_you_url, locale));
        return;
      }
      setSubmitState({
        submitted: true,
        submitError: null,
        messageText: result.message_text || "",
        messageTitle: result.message_title || "",
        thankYouUrl: null,
      });
    },
    onError: (err) => {
      recaptchaRef.current?.reset();
      setRecaptchaToken(null);
      if (err instanceof FormSubmitError) {
        setSubmitState((s) => ({
          ...s,
          submitError: formatSubmitErrors(err.result),
        }));
        return;
      }
      setSubmitState((s) => ({
        ...s,
        submitError: err instanceof Error ? err.message : "Submission failed",
      }));
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: getDefaultValues(form.fields),
  });

  const hasValidationErrors = Object.keys(errors).length > 0;

  const onSubmit = useCallback(
    async (data: Record<string, unknown>) => {
      if (!form) return;
      setSubmitState((s) => ({ ...s, submitError: null }));

      if (form.enable_recaptcha && !recaptchaToken) {
        setSubmitState((s) => ({
          ...s,
          submitError: "Please confirm you are not a robot.",
        }));
        return;
      }

      submitMutation.mutate({
        fields: form.fields,
        data,
        token: recaptchaToken,
      });
    },
    [form, recaptchaToken, submitMutation],
  );

  if (submitState.submitted) {
    return (
      <article className="form-block page-layout-whole">
        <SiteContainer className="page-text-wrapper">
          <div className="form-links">
            <div className="form-success">
              {submitState.messageTitle && (
                <h2 className="title h2">{submitState.messageTitle}</h2>
              )}
              {submitState.messageText && (
                <RichTextRenderer html={submitState.messageText} className="body-text" />
              )}
              {submitState.thankYouUrl && (
                <Button asChild variant="reverse">
                  <a href={submitState.thankYouUrl}>Continue</a>
                </Button>
              )}
            </div>
          </div>
        </SiteContainer>
      </article>
    );
  }

  const isSubmittingForm = isSubmitting || submitMutation.isPending;

  return (
    <article className="form-block page-layout-whole">
      <a className="form-anchor" id="form" aria-hidden="true" />
      <SiteContainer className="page-text-wrapper">
        <div className="form-links">
          {form.title && (
            <>
              <div className="separator"></div>
              <SiteContainer fluid>
                <div className="page-header insidetext text-center uppercase">
                  <div className="title-wrapper">
                    <h2 className="title h2">{form.title}</h2>
                  </div>
                </div>
              </SiteContainer>
            </>
          )}

          <div className="body-text">
            <div className="site-container site-container--fluid wtform-text" />
            <form
              className={`wtform${hasValidationErrors ? " has-errors" : ""}`}
              onSubmit={handleSubmit(onSubmit)}
              encType="multipart/form-data"
            >
              <div id="form-fields-container" className="form-fields-container">
                <FormFieldsLayout
                  fields={form.fields}
                  register={register}
                  errors={errors}
                />
              </div>

              {submitState.submitError && (
                <div className="form-submit-error text-center text-[rgb(var(--color-red))] py-2">
                  {submitState.submitError}
                </div>
              )}

              <div className="clearfix" />

              {form.enable_recaptcha && form.recaptcha_site_key && (
                <div className="wt-recaptcha-wrapper form-group">
                  <ReCAPTCHA
                    ref={recaptchaRef}
                    sitekey={form.recaptcha_site_key}
                    onChange={(token) => setRecaptchaToken(token)}
                    onExpired={() => setRecaptchaToken(null)}
                  />
                </div>
              )}

              <div className="text-center submit-wrapper">
                <Button type="submit" variant="reverse" disabled={isSubmittingForm}>
                  {isSubmittingForm ? "Submitting..." : "Submit"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </SiteContainer>
    </article>
  );
}

function getFieldChoices(field: FormField): { value: string; label: string }[] {
  if (field.choices_list?.length) {
    return field.choices_list;
  }
  if (field.choices) {
    return field.choices
      .split(/\r?\n/)
      .map((c) => c.trim())
      .filter(Boolean)
      .map((c) => ({ value: c, label: c }));
  }
  return [];
}

function getWidgetClass(fieldType: string): string {
  const map: Record<string, string> = {
    singleline: "widget-textinput",
    email: "widget-emailinput",
    multiline: "widget-textarea",
    number: "widget-numberinput",
    url: "widget-textinput",
    date: "widget-dateinput",
    time: "widget-timeinput",
    datetime: "widget-datetimeinput",
    file: "widget-wtfileinput",
    captcha: "widget-captchatextinput",
    checkbox: "widget-checkboxinput",
    checkboxes: "widget-checkboxselectmultiple",
  };
  return map[fieldType] || "";
}

function FormFieldsLayout({
  fields,
  register,
  errors,
}: {
  fields: FormField[];
  register: ReturnType<typeof useForm>["register"];
  errors: FieldErrors;
}) {
  const rows: ReactNode[] = [];
  let rowFields: FormField[] = [];
  let rowClass = "form-group-set-default";
  let rowKey = 0;

  const flushRow = () => {
    if (rowFields.length === 0) return;
    rows.push(
      <div key={`row-${rowKey++}`} className={`${rowClass} row`}>
        {rowFields.map((field) => (
          <FormFieldRenderer
            key={field.id}
            field={field}
            register={register}
            errors={errors}
          />
        ))}
      </div>
    );
    rowFields = [];
  };

  for (const field of fields) {
    if (field.field_type === "fieldsgroup") {
      flushRow();
      rowClass = field.add_css_class
        ? `form-group-set ${field.add_css_class}`
        : "form-group-set";
      continue;
    }

    if (field.field_type === "sectiontitleh2" || field.field_type === "sectiontitleh3") {
      flushRow();
      rows.push(
        <FormFieldRenderer
          key={field.id}
          field={field}
          register={register}
          errors={errors}
        />
      );
      continue;
    }

    rowFields.push(field);
  }

  flushRow();

  return (
    <SiteContainer fluid className={Object.keys(errors).length ? " has-errors" : ""}>
      {rows}
    </SiteContainer>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return (
    <ul className="errorlist">
      <li>{message}</li>
    </ul>
  );
}

function FormFieldRenderer({
  field,
  register,
  errors,
}: {
  field: FormField;
  register: ReturnType<typeof useForm>["register"];
  errors: FieldErrors;
}) {
  const fieldName = field.clean_name;
  const error = errors[fieldName] as { message?: string } | undefined;
  const fieldType = field.field_type;

  if (fieldType === "sectiontitleh2") {
    return <h2 className="col-sm-12">{field.label}</h2>;
  }

  if (fieldType === "sectiontitleh3") {
    return <h3 className="col-sm-12">{field.label}</h3>;
  }

  const choices = getFieldChoices(field);

  const widgetClass = getWidgetClass(fieldType);
  const baseClass = [
    "form-group",
    "clearfix",
    field.add_css_class,
    field.num != null ? `num-${field.num}` : "",
    `pk-${field.id}`,
    field.required ? "required" : "",
    widgetClass,
    error ? "has-field-error" : "",
  ]
    .filter(Boolean)
    .join(" ");

  if (fieldType === "checkbox") {
    return (
      <div className={`${baseClass} checkbox text-left`}>
        <label>
          {field.help_text && (
            <p style={{ marginLeft: "-20px" }}>
              <strong>{field.help_text}</strong>
            </p>
          )}
          <input type="checkbox" id={fieldName} {...register(fieldName)} />
          <span></span>
          <div>{field.label}</div>
        </label>
        {error && <FieldError message={error.message} />}
      </div>
    );
  }

  if (fieldType === "checkboxes") {
    return (
      <div className={`${baseClass} checkboxes`}>
        <div>
          <label htmlFor={fieldName}>{field.label}</label>
        </div>
        <div>
          <ul>
            {choices.map((choice) => (
              <li key={choice.value}>
                <label>
                  <input type="checkbox" value={choice.value} {...register(fieldName)} />
                  {choice.label}
                </label>
              </li>
            ))}
          </ul>
          {field.help_text && <p className="help-block">{field.help_text}</p>}
          {error && <FieldError message={error.message} />}
        </div>
      </div>
    );
  }

  if (fieldType === "dropdown") {
    return (
      <div className={baseClass}>
        <div>
          <label htmlFor={fieldName}>{field.label}</label>
        </div>
        <div>
          <select id={fieldName} {...register(fieldName)}>
            <option value="">{field.required ? "Please select *" : "Please select"}</option>
            {choices.map((choice) => (
              <option key={choice.value} value={choice.value}>{choice.label}</option>
            ))}
          </select>
          {error && <FieldError message={error.message} />}
          {field.help_text && <p className="help-block">{field.help_text}</p>}
        </div>
      </div>
    );
  }

  if (fieldType === "radio") {
    return (
      <div className={`${baseClass} radio`}>
        <div>
          <label>{field.label}</label>
        </div>
        <div>
          {choices.map((choice) => (
            <label key={choice.value}>
              <input type="radio" value={choice.value} {...register(fieldName)} />
              {choice.label}
            </label>
          ))}
          {field.help_text && <p className="help-block">{field.help_text}</p>}
          {error && <FieldError message={error.message} />}
        </div>
      </div>
    );
  }

  if (fieldType === "multiline") {
    return (
      <div className={baseClass}>
        <div>
          <label htmlFor={fieldName}>{field.label}</label>
        </div>
        <div>
          <textarea id={fieldName} rows={4} {...register(fieldName)} />
          {error && <FieldError message={error.message} />}
          {field.help_text && <p className="help-block">{field.help_text}</p>}
        </div>
      </div>
    );
  }

  if (fieldType === "file") {
    return (
      <div className={baseClass}>
        <div>
          <label htmlFor={fieldName}>{field.label}</label>
        </div>
        <div>
          <input id={fieldName} type="file" {...register(fieldName)} />
          {error && <FieldError message={error.message} />}
          {field.help_text && <p className="help-block">{field.help_text}</p>}
        </div>
      </div>
    );
  }

  if (fieldType === "date") {
    return (
      <div className={baseClass}>
        <div>
          <label htmlFor={fieldName}>{field.label}</label>
        </div>
        <div>
          <input id={fieldName} type="date" {...register(fieldName)} />
          {error && <FieldError message={error.message} />}
          {field.help_text && <p className="help-block">{field.help_text}</p>}
        </div>
      </div>
    );
  }

  const inputType =
    fieldType === "email" ? "email" :
    fieldType === "number" ? "number" :
    fieldType === "url" ? "url" :
    "text";

  return (
    <div className={baseClass}>
      <div>
        <label htmlFor={fieldName}>{field.label}</label>
      </div>
      <div>
        <input id={fieldName} type={inputType} {...register(fieldName)} />
        {error && <FieldError message={error.message} />}
        {field.help_text && <p className="help-block">{field.help_text}</p>}
      </div>
    </div>
  );
}
