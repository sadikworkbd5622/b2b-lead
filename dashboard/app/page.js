"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

function StatCard({ label, value, sub, color }) {
  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6">
      <p className="text-sm text-[var(--muted)]">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color || "text-[var(--foreground)]"}`}>
        {value ?? "—"}
      </p>
      {sub && <p className="text-xs text-[var(--muted)] mt-1">{sub}</p>}
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
        />
        <StatCard
          label="Qualified"
          value={stats?.qualified_leads ?? 0}
          color="text-[var(--success)]"
          sub={`${stats?.high_confidence_leads ?? 0} high confidence`}
        />
        <StatCard
          label="Avg Confidence"
          value={stats?.avg_confidence ? `${stats.avg_confidence}%` : "—"}
          color="text-[var(--warning)]"
        />
        <StatCard
          label="Last Run"
          value={stats?.last_run_date ?? "—"}
          color="text-[var(--muted)]"
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
                      <span
                        className={
                          lead.lead_status?.includes("Qualified")
                            ? "text-[var(--success)]"
                            : "text-[var(--danger)]"
                        }
                      >
                        {lead.lead_status?.includes("Qualified") ? "Qualified" : "Rejected"}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-gray-200 rounded-full">
                          <div
                            className="h-full rounded-full bg-[var(--primary)]"
                            style={{ width: `${lead.confidence_score || 0}%` }}
                          />
                        </div>
                        <span className="text-xs">{lead.confidence_score || 0}%</span>
                      </div>
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
