import { useEffect, useState } from "react";
import { api, type DueListItem } from "../../lib/api";

interface StructuredField {
  name: string;
  label: string;
  type: string;
  required: boolean;
  options?: string[];
}

function EntryForm({ item, onDone }: { item: DueListItem; onDone: () => void }) {
  const [status, setStatus] = useState("fully_met");
  const [file, setFile] = useState<File | null>(null);
  const [fields, setFields] = useState<StructuredField[]>([]);
  const [values, setValues] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (item.evidence_format === "structured_form") {
      api
        .get<{ fields: StructuredField[] }>(`/evidence/structured-form-schema/${item.indicator_id}/`)
        .then((r) => setFields(r.fields));
    }
  }, [item]);

  const submit = async () => {
    setSubmitting(true);
    setError("");
    try {
      const form = new FormData();
      form.set("indicator", String(item.indicator_id));
      form.set("status", status);
      if (file) form.set("file", file);
      for (const [k, v] of Object.entries(values)) form.set(k, v);
      await api.postForm("/evidence/submit/", form);
      onDone();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mt-2 rounded border border-slate-200 bg-slate-50 p-3">
      <div className="mb-2 flex gap-2">
        <select className="rounded border border-slate-300 px-2 py-1 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="fully_met">Fully met</option>
          <option value="partially_met">Partially met</option>
          <option value="not_met">Not met</option>
        </select>
      </div>

      {(item.evidence_format === "photo" || item.evidence_format === "document") && (
        <input
          type="file"
          accept={item.evidence_format === "photo" ? "image/*" : undefined}
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mb-2 block text-sm"
        />
      )}

      {item.evidence_format === "structured_form" && (
        <div className="mb-2 grid grid-cols-2 gap-2">
          {fields.map((f) => (
            <label key={f.name} className="text-xs text-slate-600">
              {f.label}
              {f.type === "select" ? (
                <select
                  className="mt-1 block w-full rounded border border-slate-300 px-2 py-1 text-sm"
                  value={values[f.name] ?? ""}
                  onChange={(e) => setValues({ ...values, [f.name]: e.target.value })}
                >
                  <option value="">—</option>
                  {f.options?.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
              ) : (
                <input
                  type={f.type === "number" ? "number" : f.type === "date" ? "date" : "text"}
                  className="mt-1 block w-full rounded border border-slate-300 px-2 py-1 text-sm"
                  value={values[f.name] ?? ""}
                  onChange={(e) => setValues({ ...values, [f.name]: e.target.value })}
                />
              )}
            </label>
          ))}
        </div>
      )}

      {error && <p className="mb-2 text-xs text-red-600">{error}</p>}
      <button
        disabled={submitting}
        onClick={submit}
        className="rounded bg-slate-900 px-3 py-1 text-sm text-white disabled:opacity-50"
      >
        Submit
      </button>
    </div>
  );
}

export default function DailyPage() {
  const [items, setItems] = useState<DueListItem[]>([]);
  const [openId, setOpenId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api
      .get<{ date: string; items: DueListItem[] }>("/evidence/due-list/")
      .then((r) => setItems(r.items))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  return (
    <div className="mx-auto max-w-4xl p-4">
      <h1 className="mb-4 text-xl font-semibold text-slate-900">Today's Due List</h1>
      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.indicator_id} className="rounded-lg border border-slate-200 bg-white p-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-slate-900">
                    #{item.indicator_id} {item.indicator_text}
                  </div>
                  <div className="text-xs text-slate-500">
                    {item.frequency} · {item.period_label} · {item.evidence_format}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`rounded px-2 py-1 text-xs ${item.done ? "bg-green-100 text-green-800" : "bg-amber-100 text-amber-800"}`}>
                    {item.done ? "Done" : "Due"}
                  </span>
                  <button
                    className="text-xs underline"
                    onClick={() => setOpenId(openId === item.indicator_id ? null : item.indicator_id)}
                  >
                    {openId === item.indicator_id ? "Close" : item.done ? "Update" : "Enter"}
                  </button>
                </div>
              </div>
              {openId === item.indicator_id && (
                <EntryForm item={item} onDone={() => { setOpenId(null); load(); }} />
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
