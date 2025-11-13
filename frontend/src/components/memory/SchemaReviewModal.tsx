import { useState } from "react";
import { approveSchema } from "../../api/memory";

type Proposal = {
  proposal_id: string;
  table: string;
  summary: string;
  diff: Record<string, unknown>;
};

type Props = {
  proposals: Proposal[];
  onRefresh: () => void;
};

export default function SchemaReviewModal({ proposals, onRefresh }: Props) {
  const [selected, setSelected] = useState<Proposal | null>(null);
  const [reason, setReason] = useState("");
  const [saving, setSaving] = useState(false);

  const handleDecision = async (approved: boolean) => {
    if (!selected) return;
    setSaving(true);
    try {
      await approveSchema(selected.proposal_id, approved, reason);
      onRefresh();
      setSelected(null);
      setReason("");
    } finally {
      setSaving(false);
    }
  };

  if (!proposals.length) return null;

  return (
    <div className="schema-modal">
      <div className="schema-list">
        <h3>Schema Proposals</h3>
        <ul>
          {proposals.map((p) => (
            <li key={p.proposal_id} onClick={() => setSelected(p)}>
              <strong>{p.table}</strong> – {p.summary}
            </li>
          ))}
        </ul>
      </div>

      {selected ? (
        <div className="schema-detail">
          <h4>{selected.table}</h4>
          <pre>{JSON.stringify(selected.diff, null, 2)}</pre>
          <textarea
            placeholder="Approval notes"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <div className="schema-actions">
            <button disabled={saving} onClick={() => handleDecision(false)}>
              Reject
            </button>
            <button disabled={saving} onClick={() => handleDecision(true)}>
              Approve
            </button>
          </div>
        </div>
      ) : (
        <div className="schema-detail-empty">Select a proposal to review</div>
      )}
    </div>
  );
}
