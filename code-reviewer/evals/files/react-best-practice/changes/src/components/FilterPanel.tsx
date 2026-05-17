import { useEffect, useState } from "react";

type FilterPanelProps = {
  initialQuery: string;
  onQueryChange: (query: string) => void;
};

export function FilterPanel({ initialQuery, onQueryChange }: FilterPanelProps) {
  const [query, setQuery] = useState(initialQuery);

  if (query !== initialQuery) {
    setQuery(initialQuery);
  }

  useEffect(() => {
    window.setTimeout(() => {
      onQueryChange(query);
    }, 300);
  }, [query]);

  return (
    <input
      aria-label="Search"
      value={query}
      onChange={(event) => setQuery(event.target.value)}
    />
  );
}
