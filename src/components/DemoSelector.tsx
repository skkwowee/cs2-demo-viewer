"use client";

import { useEffect, useMemo, useState } from "react";

export interface DemoEntry {
  stem: string;
  map_name: string;
  rounds: number;
}

interface Props {
  onSelect: (demo: string, round: number) => void;
  selectedDemo: string | null;
  selectedRound: number;
}

export default function DemoSelector({
  onSelect,
  selectedDemo,
  selectedRound,
}: Props) {
  const [demos, setDemos] = useState<DemoEntry[]>([]);

  useEffect(() => {
    fetch("/viewer-data/index.json")
      .then((r) => r.json())
      .then((data: DemoEntry[]) => {
        setDemos(data);
        if (data.length > 0 && !selectedDemo) {
          onSelect(data[0].stem, 1);
        }
      })
      .catch(() => setDemos([]));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps -- load demo index once on mount

  const roundCount = useMemo(() => {
    if (!selectedDemo) return 0;
    const entry = demos.find((d) => d.stem === selectedDemo);
    return entry?.rounds ?? 0;
  }, [selectedDemo, demos]);

  return (
    <div className="flex flex-wrap items-center gap-4">
      <label className="flex items-center gap-2 text-sm">
        <span className="text-muted">Demo</span>
        <select
          className="rounded border border-border bg-card px-3 py-1.5 text-sm"
          value={selectedDemo ?? ""}
          onChange={(e) => {
            const stem = e.target.value;
            if (stem) onSelect(stem, 1);
          }}
        >
          {demos.map((d) => (
            <option key={d.stem} value={d.stem}>
              {d.stem} ({d.map_name})
            </option>
          ))}
        </select>
      </label>

      <label className="flex items-center gap-2 text-sm">
        <span className="text-muted">Round</span>
        <select
          className="rounded border border-border bg-card px-3 py-1.5 text-sm"
          value={selectedRound}
          onChange={(e) => {
            if (selectedDemo) onSelect(selectedDemo, Number(e.target.value));
          }}
        >
          {Array.from({ length: roundCount }, (_, i) => i + 1).map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
