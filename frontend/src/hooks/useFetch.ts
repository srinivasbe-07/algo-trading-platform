import { useCallback, useEffect, useState } from "react";

// Runs an async fetcher on mount; exposes data/loading/error + a reload().
// `fn` must be a stable reference (e.g. a module-level API function).
export function useFetch<T>(fn: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fn()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, [fn]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
