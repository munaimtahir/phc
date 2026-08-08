import { useEffect, useState } from "react";
import { api, type Indicator, type ComplianceSummary } from "../../lib/api";

const DOMAINS = ["AAC", "BSBS", "COP", "FMS", "HRM", "MER", "PRE", "QA", "ROM", "RRS"];
const CATEGORIES = ["physical", "one_time", "recurring"];
const FREQUENCIES = ["daily", "weekly", "monthly", "quarterly", "biannual", "annual", "as_needed"];

export default function RegistryPage() {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [compliance, setCompliance] = useState<ComplianceSummary | null>(null);
  const [domain, setDomain] = useState("");
  const [category, setCategory] = useState("");
  const [frequency, setFrequency] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<ComplianceSummary>("/compliance/").then(setCompliance).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (domain) params.set("domain", domain);
    if (category) params.set("category", category);
    if (frequency) params.set("frequency", frequency);
    api
      .get<Indicator[]>(`/registry/indicators/?${params.toString()}`)
      .then(setIndicators)
      .finally(() => setLoading(false));
  }, [domain, category, frequency]);

  const statusById = new Map(
    (compliance?.per_indicator ?? []).map((row) => [row.indicator_id, row.status])
  );

  return (
    <div className="mx-auto max-w-6xl p-4">
      {compliance && (
        <div className="mb-4 rounded-lg border border-slate-200 bg-white p-4">
          <div className="text-2xl font-semibold text-slate-900">
            {compliance.overall_pct.toFixed(2)}% compliant
          </div>
          <div className="text-sm text-slate-500">
            {compliance.earned_total.toFixed(1)} / {compliance.possible_total.toFixed(1)} weightage
          </div>
        </div>
      )}

      <div className="mb-4 flex gap-3">
        <select className="rounded border border-slate-300 px-2 py-1 text-sm" value={domain} onChange={(e) => setDomain(e.target.value)}>
          <option value="">All domains</option>
          {DOMAINS.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
        <select className="rounded border border-slate-300 px-2 py-1 text-sm" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select className="rounded border border-slate-300 px-2 py-1 text-sm" value={frequency} onChange={(e) => setFrequency(e.target.value)}>
          <option value="">All frequencies</option>
          {FREQUENCIES.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-3 py-2">#</th>
                <th className="px-3 py-2">Standard</th>
                <th className="px-3 py-2">Indicator</th>
                <th className="px-3 py-2">Weightage</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2">Frequency</th>
                <th className="px-3 py-2">Format</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {indicators.map((ind) => (
                <tr key={ind.id} className="border-t border-slate-100">
                  <td className="px-3 py-2">{ind.id}</td>
                  <td className="px-3 py-2">{ind.standard_code}</td>
                  <td className="px-3 py-2">{ind.text}</td>
                  <td className="px-3 py-2">
                    {ind.weightage}{ind.allows_partial ? " (partial ok)" : ""}
                  </td>
                  <td className="px-3 py-2">{ind.category}</td>
                  <td className="px-3 py-2">{ind.frequency ?? "—"}</td>
                  <td className="px-3 py-2">{ind.evidence_format}</td>
                  <td className="px-3 py-2">{statusById.get(ind.id) ?? "not_met"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
