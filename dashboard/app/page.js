"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

function StatCard({ label, value, sub, color, icon }) {
  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-[var(--muted)]">{label}</p>
          <p className={`text-3xl font-bold mt-1 ${color || "text-[var(--foreground)]"}`}>
            {value ?? "—"}
          </p>
        </div>
        {icon && <span className="text-2xl opacity-30">{icon}</span>}
      </div>
      {sub && <p className="text-xs text-[var(--muted)] mt-1">{sub}</p>}
    </div>
  );
}

function StatusBadge({ status }) {
  if (status?.includes("Qualified")) {
    return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Qualified</span>;
  }
  if (status?.includes("Rejected")) {
    return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Rejected</span>;
  }
  if (status === "Unprocessed - LLM Unavailable") {
    return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Unprocessed</span>;
  }
  if (status === "Discovered - Awaiting Processing") {
    return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Raw</span>;
  }
  return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status || "Unknown"}</span>;
}

function ConfidenceBar({ score }) {
  const s = score || 0;
  let color = "bg-red-500";
  if (s >= 70) color = "bg-green-500";
  else if (s >= 40) color = "bg-yellow-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-gray-200 rounded-full">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${s}%` }} />
      </div>
      <span className="text-xs">{s}%</span>
    </div>
  );
}

export default function Home() {
  const [stats, setStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, leadsRes] = await Promise.all([
          fetch("/api/stats").then((r) => r.json()),
          fetch("/api/leads?limit=10").then((r) => r.json()),
        ]);
        setStats(statsRes.stats);
        setLeads(leadsRes.leads || []);
      } catch (e) {
        console.error("Failed to fetch data", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-[var(--muted)]">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Lead Marketplace</h1>
          <p className="text-[var(--muted)] mt-1">
            Buy qualified B2B leads for your business
          </p>
        </div>
        <Link
          href="/pricing"
          className="bg-[var(--primary)] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[var(--primary-dark)] transition-colors"
        >
          Purchase Leads
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard
          label="Total Leads"
          value={stats?.total_leads ?? 0}
          color="text-[var(--primary)]"
          icon="📊"
        />
        <StatCard
          label="Qualified"
          value={stats?.qualified_leads ?? 0}
          color="text-[var(--success)]"
          sub={`${stats?.high_confidence_leads ?? 0} high confidence`}
          icon="✅"
        />
        <StatCard
          label="Unprocessed"
          value={stats?.unprocessed_leads ?? 0}
          color="text-[var(--warning)]"
          sub={`${stats?.raw_discovered ?? 0} raw discovered`}
          icon="⏳"
        />
        <StatCard
          label="Avg Confidence"
          value={stats?.avg_confidence ? `${stats.avg_confidence}%` : "—"}
          color="text-[var(--info)]"
          sub={`Last run: ${stats?.last_run_date ?? "—"}`}
          icon="🎯"
        />
      </div>

      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl">
        <div className="px-6 py-4 border-b border-[var(--border)] flex justify-between items-center">
          <h2 className="font-semibold text-lg">Recent Leads</h2>
          <Link href="/leads" className="text-sm text-[var(--primary)] hover:underline">
            View all
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] text-[var(--muted)]">
                <th className="text-left px-6 py-3 font-medium">Business</th>
                <th className="text-left px-6 py-3 font-medium">Phone</th>
                <th className="text-left px-6 py-3 font-medium">Email</th>
                <th className="text-left px-6 py-3 font-medium">Status</th>
                <th className="text-left px-6 py-3 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {leads.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[var(--muted)]">
                    No leads yet. Run the agent to generate leads.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr
                    key={lead.id}
                    className="border-b border-[var(--border)] hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-3">
                      <Link
                        href={`/leads/${lead.id}`}
                        className="font-medium text-[var(--primary)] hover:underline"
                      >
                        {lead.business_name}
                      </Link>
                    </td>
                    <td className="px-6 py-3">{lead.phone_number || "—"}</td>
                    <td className="px-6 py-3">{lead.email_address || "—"}</td>
                    <td className="px-6 py-3">
                      <StatusBadge status={lead.lead_status} />
                    </td>
                    <td className="px-6 py-3">
                      <ConfidenceBar score={lead.confidence_score} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
