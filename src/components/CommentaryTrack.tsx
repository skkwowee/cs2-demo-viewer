"use client";

import { useEffect, useRef } from "react";

export interface CommentaryLine {
  round_num: number;
  tick_start: number;
  tick_end: number;
  bucket: string; // tactical | vague | offtopic | silence
  specific_hits?: string[];
  t_vod?: number;
  text: string;
}

interface Props {
  lines: CommentaryLine[];
  currentTick: number;
  meta?: {
    source?: string;
    alignment?: string;
  } | null;
}

const BUCKET_STYLE: Record<string, string> = {
  tactical: "text-emerald-400",
  vague: "text-amber-400/80",
  offtopic: "text-muted/60",
  silence: "text-muted/40",
};

/**
 * Caster commentary, time-synced to the demo timeline. The line whose tick
 * range contains the current frame's tick is highlighted and auto-scrolled
 * into view — the visual demonstration that commentary overlaps ticks.
 */
export default function CommentaryTrack({ lines, currentTick, meta }: Props) {
  const activeRef = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const activeIdx = lines.findIndex(
    (l) => currentTick >= l.tick_start && currentTick < l.tick_end
  );

  // Auto-scroll the active line into view (within the panel only).
  useEffect(() => {
    if (activeRef.current && containerRef.current) {
      const c = containerRef.current;
      const a = activeRef.current;
      const top = a.offsetTop - c.offsetTop - c.clientHeight / 2 + a.clientHeight / 2;
      c.scrollTo({ top, behavior: "smooth" });
    }
  }, [activeIdx]);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
          Commentary
        </h3>
        <span className="text-[10px] uppercase tracking-wider text-emerald-400/70">
          tick-synced
        </span>
      </div>

      {lines.length === 0 ? (
        <div className="mt-2 text-xs text-muted">
          No commentary for this round.
        </div>
      ) : (
        <div
          ref={containerRef}
          className="mt-2 max-h-72 space-y-2 overflow-y-auto pr-1"
        >
          {lines.map((l, i) => {
            const active = i === activeIdx;
            const tone = BUCKET_STYLE[l.bucket] ?? "text-foreground";
            return (
              <div
                key={`${l.tick_start}-${i}`}
                ref={active ? activeRef : null}
                className={`rounded border-l-2 px-2 py-1 text-xs leading-snug transition-colors ${
                  active
                    ? "border-emerald-400 bg-emerald-400/10 text-foreground"
                    : `border-transparent ${tone}`
                }`}
              >
                <div className="flex items-center gap-2 font-mono text-[10px] text-muted">
                  <span>t{l.tick_start}</span>
                  <span
                    className={`rounded px-1 ${
                      l.bucket === "tactical"
                        ? "bg-emerald-400/15 text-emerald-400"
                        : "bg-muted/10"
                    }`}
                  >
                    {l.bucket}
                  </span>
                  {l.specific_hits && l.specific_hits.length > 0 && (
                    <span className="truncate text-emerald-400/60">
                      {l.specific_hits.slice(0, 4).join(" ")}
                    </span>
                  )}
                </div>
                <div className="mt-0.5">{l.text}</div>
              </div>
            );
          })}
        </div>
      )}

      {meta?.alignment && (
        <p className="mt-2 border-t border-border pt-2 text-[10px] leading-tight text-muted/70">
          {meta.source}. {meta.alignment}
        </p>
      )}
    </div>
  );
}
