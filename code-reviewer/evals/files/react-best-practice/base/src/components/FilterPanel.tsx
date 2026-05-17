import { useEffect, useState } from "react";

type FilterPanelProps = {
  initialQuery: string;
  onQueryChange: (query: string) => void;
};

export function FilterPanel({ initialQuery, onQueryChange }: FilterPanelProps) {
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      onQueryChange(query);
    }, 300);

    return () => window.clearTimeout(timeoutId);
  }, [onQueryChange, query]);

  return (
    <input
      aria-label="Search"
      value={query}
      onChange={(event) => setQuery(event.target.value)}
    />
  );
}
