import { useEffect, useState } from "react";
import { api, getStoredUsername, type Draft, type Indicator } from "../../lib/api";

export default function DraftingPage() {
  const [eligibleIds, setEligibleIds] = useState<number[]>([]);
  const [indicators, setIndicators] = useState<Record<number, Indicator>>({});
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [domainFilter, setDomainFilter] = useState("");
  const [existingDraftId, setExistingDraftId] = useState<number | null>(null);

  const [activeDraft, setActiveDraft] = useState<Draft | null>(null);
  const [pastedOutput, setPastedOutput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  // Review queue state
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState<Record<number, string>>({});
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const loadDrafts = async () => {
    const data = await api.get<Draft[]>("/drafting/drafts/");
    setDrafts(data);
  };

  useEffect(() => {
    api.get<number[]>("/drafting/drafts/eligible_indicators_list/").then(setEligibleIds);
    api.get<Indicator[]>("/registry/indicators/").then((all) => {
      const map: Record<number, Indicator> = {};
      all.forEach((i) => (map[i.id] = i));
      setIndicators(map);
    });
    loadDrafts();
  }, []);

  const toggleSelectIndicator = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleBuildPrompt = async () => {
    if (selectedIds.length === 0) return;
    setBusy(true);
    setError("");
    setCopied(false);
    try {
      const draft = await api.post<Draft>("/drafting/drafts/build_prompt/", {
        indicator_ids: selectedIds,
        created_by: getStoredUsername() || "operator",
        existing_draft_id: existingDraftId,
      });
      setActiveDraft(draft);
      setPastedOutput("");
      loadDrafts();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to build prompt");
    } finally {
      setBusy(false);
    }
  };

  const copyToClipboard = () => {
    if (!activeDraft?.prompt_text) return;
    navigator.clipboard.writeText(activeDraft.prompt_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadPromptTxt = () => {
    if (!activeDraft?.prompt_text) return;
    const blob = new Blob([activeDraft.prompt_text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `prompt_indicators_${activeDraft.indicator_ids.join("_")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSaveOutput = async () => {
    if (!activeDraft || !pastedOutput.trim()) return;
    setBusy(true);
    setError("");
    try {
      const updated = await api.post<Draft>(
        `/drafting/drafts/${activeDraft.id}/save_output/`,
        { raw_output: pastedOutput }
      );
      setActiveDraft(updated);
      loadDrafts();
      setExpandedId(updated.id);
      setEditContent((prev) => ({ ...prev, [updated.id]: updated.working_content }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save output");
    } finally {
      setBusy(false);
    }
  };

  const handleSaveContentEdit = async (draft: Draft) => {
    const content = editContent[draft.id] ?? draft.working_content;
    setBusy(true);
    try {
      await api.post(`/drafting/drafts/${draft.id}/update_content/`, {
        working_content: content,
      });
      loadDrafts();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save edits");
    } finally {
      setBusy(false);
    }
  };

  const actOnDraft = async (draft: Draft, action: "approve" | "reject") => {
    const reviewedBy = getStoredUsername() || prompt("Your name (for review record):") || "";
    if (!reviewedBy) return;
    setBusy(true);
    try {
      await api.post(`/drafting/drafts/${draft.id}/${action}/`, {
        reviewed_by: reviewedBy,
      });
      loadDrafts();
    } catch (e) {
      setError(e instanceof Error ? e.message : `Failed to ${action} draft`);
    } finally {
      setBusy(false);
    }
  };

  // Filtering eligible list
  const eligibleIndicators = eligibleIds
    .map((id) => indicators[id])
    .filter((ind) => ind !== undefined)
    .filter((ind) => {
      const matchesSearch =
        searchTerm === "" ||
        ind.id.toString().includes(searchTerm) ||
        ind.text.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesDomain = domainFilter === "" || ind.domain_code === domainFilter;
      return matchesSearch && matchesDomain;
    });

  const domains = Array.from(
    new Set(eligibleIds.map((id) => indicators[id]?.domain_code).filter(Boolean))
  );

  const approvedDrafts = drafts.filter((d) => d.status === "approved");
  const filteredReviewDrafts = drafts.filter((d) =>
    statusFilter === "all" ? true : d.status === statusFilter
  );

  return (
    <div className="mx-auto max-w-5xl p-4">
      <h1 className="mb-2 text-2xl font-bold text-slate-900">AI Drafting Assistant (Manual Round-Trip)</h1>
      <p className="mb-6 text-sm text-slate-600">
        Generate complete, structured prompts for external AI tools (ChatGPT, Claude, Gemini).
        Paste back responses to review, edit, and approve compliance evidence for Al Shifa Laboratory.
      </p>

      {error && (
        <div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* STEP 1: PROMPT BUILDER */}
      <div className="mb-8 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800">
            Step 1: Prompt Builder (Select Target Indicator/s)
          </h2>
          <span className="text-xs text-slate-500">
            {selectedIds.length} indicator(s) selected
          </span>
        </div>

        {/* Filters */}
        <div className="mb-3 flex flex-wrap gap-2">
          <input
            type="text"
            placeholder="Search indicator # or text..."
            className="rounded border border-slate-300 px-3 py-1 text-sm text-slate-800"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="rounded border border-slate-300 px-3 py-1 text-sm text-slate-800"
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
          >
            <option value="">All Domains</option>
            {domains.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
          {approvedDrafts.length > 0 && (
            <select
              className="rounded border border-slate-300 px-3 py-1 text-sm text-slate-800"
              value={existingDraftId ?? ""}
              onChange={(e) =>
                setExistingDraftId(e.target.value ? Number(e.target.value) : null)
              }
            >
              <option value="">Mode: Fresh Prompt</option>
              {approvedDrafts.map((ad) => (
                <option key={ad.id} value={ad.id}>
                  Mode: Revise Existing Draft #{ad.id} (v{ad.version_no})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Selection Box */}
        <div className="max-h-48 overflow-y-auto rounded border border-slate-200 bg-slate-50 p-2">
          {eligibleIndicators.length === 0 ? (
            <p className="p-2 text-xs text-slate-500">No eligible indicators match filter.</p>
          ) : (
            eligibleIndicators.map((ind) => (
              <label
                key={ind.id}
                className="flex cursor-pointer items-start gap-2 rounded p-1.5 hover:bg-slate-100"
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(ind.id)}
                  onChange={() => toggleSelectIndicator(ind.id)}
                  className="mt-0.5"
                />
                <span className="text-xs text-slate-800">
                  <strong className="font-semibold text-slate-900">#{ind.id}</strong> [{ind.domain_code}] ({ind.category} / {ind.evidence_format}) — {ind.text}
                </span>
              </label>
            ))
          )}
        </div>

        <div className="mt-3 flex gap-2">
          <button
            disabled={busy || selectedIds.length === 0}
            onClick={handleBuildPrompt}
            className="rounded bg-slate-900 px-4 py-1.5 text-sm font-medium text-white shadow hover:bg-slate-800 disabled:opacity-50"
          >
            {busy ? "Building..." : "Generate Prompt"}
          </button>
        </div>

        {/* Generated Prompt Viewer */}
        {activeDraft?.prompt_text && (
          <div className="mt-4 rounded border border-slate-300 bg-slate-900 p-4 text-slate-100">
            <div className="mb-2 flex items-center justify-between border-b border-slate-700 pb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Assembled Prompt ({activeDraft.kind} v{activeDraft.version_no})
              </span>
              <div className="flex gap-2">
                <button
                  onClick={copyToClipboard}
                  className="rounded bg-slate-800 px-3 py-1 text-xs text-slate-200 hover:bg-slate-700"
                >
                  {copied ? "✓ Copied!" : "📋 Copy to Clipboard"}
                </button>
                <button
                  onClick={downloadPromptTxt}
                  className="rounded bg-slate-800 px-3 py-1 text-xs text-slate-200 hover:bg-slate-700"
                >
                  💾 Download .txt
                </button>
              </div>
            </div>
            <pre className="max-h-60 overflow-y-auto whitespace-pre-wrap font-mono text-xs text-slate-200">
              {activeDraft.prompt_text}
            </pre>
          </div>
        )}
      </div>

      {/* STEP 2: OUTPUT RECEIVER */}
      {activeDraft && (
        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-1 text-base font-semibold text-slate-800">
            Step 2: Output Receiver (Paste AI Response)
          </h2>
          <p className="mb-3 text-xs text-slate-500">
            Paste the markdown output received from your external AI tool below. The output should include section headers: Purpose, Scope, Roles & responsibilities, Procedure, Records & evidence, References.
          </p>

          <textarea
            rows={8}
            placeholder="Paste raw Markdown response here..."
            className="w-full rounded border border-slate-300 p-3 font-mono text-xs text-slate-900 focus:border-slate-500 focus:outline-none"
            value={pastedOutput}
            onChange={(e) => setPastedOutput(e.target.value)}
          />

          <div className="mt-3 flex justify-end">
            <button
              disabled={busy || !pastedOutput.trim()}
              onClick={handleSaveOutput}
              className="rounded bg-green-600 px-4 py-1.5 text-sm font-medium text-white shadow hover:bg-green-700 disabled:opacity-50"
            >
              Save Draft & Send for Review
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: REVIEW & APPROVAL QUEUE */}
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800">
            Step 3: Document Review & Approval Queue
          </h2>
          <div className="flex gap-2">
            {["all", "pending_review", "draft", "approved", "rejected"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`rounded px-2.5 py-1 text-xs capitalize ${
                  statusFilter === st
                    ? "bg-slate-900 text-white font-medium"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {st.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        {filteredReviewDrafts.length === 0 ? (
          <p className="text-xs text-slate-500">No drafts in this queue view.</p>
        ) : (
          <ul className="space-y-3">
            {filteredReviewDrafts.map((draft) => {
              const isExpanded = expandedId === draft.id;
              const isPending = draft.status === "pending_review" || draft.status === "draft";
              return (
                <li
                  key={draft.id}
                  className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-900">
                          Draft #{draft.id} ({draft.kind} v{draft.version_no})
                        </span>
                        <span
                          className={`rounded px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${
                            draft.status === "approved"
                              ? "bg-green-100 text-green-800"
                              : draft.status === "rejected"
                              ? "bg-red-100 text-red-800"
                              : "bg-amber-100 text-amber-800"
                          }`}
                        >
                          {draft.status.replace("_", " ")}
                        </span>
                      </div>
                      <div className="mt-1 text-xs text-slate-600">
                        Indicators: {draft.indicator_ids.map((id) => `#${id}`).join(", ")}
                        {draft.reviewed_by && ` · Reviewed by ${draft.reviewed_by}`}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        className="rounded border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                        onClick={() => {
                          setExpandedId(isExpanded ? null : draft.id);
                          if (!editContent[draft.id]) {
                            setEditContent((prev) => ({
                              ...prev,
                              [draft.id]: draft.working_content,
                            }));
                          }
                        }}
                      >
                        {isExpanded ? "Close" : "Review / Edit"}
                      </button>

                      {isPending && (
                        <>
                          <button
                            disabled={busy}
                            className="rounded bg-green-600 px-3 py-1 text-xs font-medium text-white shadow hover:bg-green-700 disabled:opacity-50"
                            onClick={() => actOnDraft(draft, "approve")}
                          >
                            Approve
                          </button>
                          <button
                            disabled={busy}
                            className="rounded bg-red-600 px-3 py-1 text-xs font-medium text-white shadow hover:bg-red-700 disabled:opacity-50"
                            onClick={() => actOnDraft(draft, "reject")}
                          >
                            Reject
                          </button>
                        </>
                      )}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="mt-4 border-t border-slate-200 pt-4">
                      <div className="mb-2 flex items-center justify-between">
                        <label className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                          Working Content (Editable Document)
                        </label>
                        {isPending && (
                          <button
                            disabled={busy}
                            onClick={() => handleSaveContentEdit(draft)}
                            className="rounded border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
                          >
                            Save Edits
                          </button>
                        )}
                      </div>

                      <textarea
                        rows={10}
                        disabled={!isPending}
                        className="w-full rounded border border-slate-300 p-3 font-mono text-xs text-slate-900 focus:border-slate-500 focus:outline-none disabled:bg-slate-50"
                        value={editContent[draft.id] ?? draft.working_content}
                        onChange={(e) =>
                          setEditContent({ ...editContent, [draft.id]: e.target.value })
                        }
                      />

                      {/* Audit Details */}
                      <details className="mt-3 text-xs text-slate-500">
                        <summary className="cursor-pointer font-medium text-slate-700 hover:underline">
                          View Audit Trail (Immutable Prompt & Raw Output)
                        </summary>
                        <div className="mt-2 space-y-2 rounded bg-slate-50 p-3">
                          <div>
                            <strong className="block text-slate-700">Exact Generated Prompt (Immutable):</strong>
                            <pre className="mt-1 whitespace-pre-wrap font-mono text-[11px] text-slate-600">
                              {draft.prompt_text || "(None)"}
                            </pre>
                          </div>
                          <div>
                            <strong className="block text-slate-700">Verbatim Pasted Raw Output (Immutable):</strong>
                            <pre className="mt-1 whitespace-pre-wrap font-mono text-[11px] text-slate-600">
                              {draft.raw_output || "(None)"}
                            </pre>
                          </div>
                        </div>
                      </details>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
