"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function LeadDetail() {
  const { id } = useParams();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/leads/${id}`)
      .then((r) => r.json())
      .then((d) => {
        setLead(d.lead);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-[var(--muted)]">
        Loading...
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold mb-2">Lead Not Found</h2>
        <Link href="/leads" className="text-[var(--primary)] hover:underline">
          Back to leads
        </Link>
      </div>
    );
  }

  const fields = [
    { label: "Business Name", value: lead.business_name },
    { label: "Decision Maker", value: lead.decision_maker_name },
    { label: "Phone Number", value: lead.phone_number },
    { label: "Email Address", value: lead.email_address },
    { label: "Social Media", value: lead.social_media_link },
    { label: "Lead Status", value: lead.lead_status },
    { label: "Confidence Score", value: `${lead.confidence_score}%` },
    { label: "Created At", value: lead.created_at },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <Link
        href="/leads"
        className="text-sm text-[var(--primary)] hover:underline mb-4 inline-block"
      >
        ← Back to leads
      </Link>

      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl">
        <div className="px-6 py-5 border-b border-[var(--border)]">
          <h1 className="text-2xl font-bold">{lead.business_name}</h1>
          <span
            className={`inline-block mt-1 text-sm font-medium ${
              lead.lead_status?.includes("Qualified")
                ? "text-[var(--success)]"
                : "text-[var(--danger)]"
            }`}
          >
            {lead.lead_status?.includes("Qualified") ? "Qualified" : "Rejected"}
          </span>
        </div>

        <div className="px-6 py-5 space-y-4">
          {fields.map((f) => (
            <div key={f.label} className="flex">
              <span className="w-40 text-sm text-[var(--muted)] shrink-0">
                {f.label}
              </span>
              <span className="text-sm font-medium break-all">
                {f.value && f.value !== "Not Found" ? f.value : "—"}
              </span>
            </div>
          ))}

          {lead.reasoning_log && (
            <div className="pt-4 border-t border-[var(--border)]">
              <p className="text-sm text-[var(--muted)] mb-1">Reasoning</p>
              <p className="text-sm">{lead.reasoning_log}</p>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-[var(--border)] bg-gray-50 rounded-b-xl flex gap-3">
          <Link
            href={`/checkout?lead=${lead.id}`}
            className="bg-[var(--primary)] text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-[var(--primary-dark)] transition-colors"
          >
            Purchase This Lead
          </Link>
          <Link
            href="/leads"
            className="border border-[var(--border)] px-5 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors"
          >
            Back to List
          </Link>
        </div>
      </div>
    </div>
  );
}
