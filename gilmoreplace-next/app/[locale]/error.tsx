"use client";

/**
 * Segment error UI for `/{locale}/…`.
 */

export default function LocaleError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="page-error" role="alert">
      <p>Something went wrong loading this page.</p>
      <button type="button" onClick={reset}>
        Try again
      </button>
      {process.env.NODE_ENV === "development" ? (
        <pre>{error.message}</pre>
      ) : null}
    </div>
  );
}
