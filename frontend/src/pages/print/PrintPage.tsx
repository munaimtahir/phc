import { useState } from "react";
import { API_BASE_URL } from "../../lib/api";

export default function PrintPage() {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setGenerating(true);
    setError("");
    try {
      const token = sessionStorage.getItem("phc_auth");
      const res = await fetch(`${API_BASE_URL}/exports/print-pack/`, {
        headers: token ? { Authorization: `Basic ${token}` } : {},
      });
      if (!res.ok) throw new Error("Failed to generate print pack.");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "phc_msds_print_pack.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl p-4">
      <h1 className="mb-4 text-xl font-semibold text-slate-900">Print Pack</h1>
      <p className="mb-4 text-sm text-slate-600">
        Compiles all 118 indicators with their current evidence and live compliance %,
        ordered to mirror PHC's own domain → standard → indicator checklist.
      </p>
      {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
      <button
        onClick={generate}
        disabled={generating}
        className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {generating ? "Generating…" : "Generate Print Pack"}
      </button>
    </div>
  );
}
