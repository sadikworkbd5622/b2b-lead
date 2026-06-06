"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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
      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${s}%` }} />
      </div>
      <span className="text-xs font-medium">{s}%</span>
    </div>
  );
}

export default function LeadsPage() {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({});
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1 });
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [loading, setLoading] = useState(true);

  async function fetchLeads(page = 1) {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, limit: 50 });
      if (search) params.set("search", search);
      if (status !== "all") params.set("status", status);

      const res = await fetch(`/api/leads?${params}`).then((r) => r.json());
      setLeads(res.leads || []);
      setStats(res.stats || {});
      setPagination(res.pagination || { page: 1, totalPages: 1 });
    } catch (e) {
      console.error("Failed to fetch", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLeads(1);
  }, [status]);

  function handleSearch(e) {
    e.preventDefault();
    fetchLeads(1);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Browse Leads</h1>
          <p className="text-[var(--muted)] mt-1">
            {stats.total || 0} total leads found
            {stats.qualified > 0 && <span className="ml-2">· {stats.qualified} qualified</span>}
            {stats.unprocessed > 0 && <span className="ml-2">· {stats.unprocessed} unprocessed</span>}
          </p>
        </div>
        <Link
          href="/pricing"
          className="bg-[var(--primary)] text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-[var(--primary-dark)] transition-colors"
        >
          Purchase Leads
        </Link>
      </div>

      <div className="flex gap-4 mb-6 items-center flex-wrap">
        <form onSubmit={handleSearch} className="flex-1 min-w-[200px] flex gap-2">
          <input
            type="text"
            placeholder="Search by business name, phone, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
          />
          <button
            type="submit"
            className="bg-[var(--primary)] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[var(--primary-dark)]"
          >
            Search
          </button>
        </form>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
        >
          <option value="all">All Status</option>
          <option value="Qualified - No Website">Qualified</option>
          <option value="Rejected - Has Website">Rejected</option>
          <option value="Unprocessed - LLM Unavailable">Unprocessed</option>
          <option value="Discovered - Awaiting Processing">Raw</option>
        </select>
      </div>

      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] bg-gray-50 text-[var(--muted)]">
                <th className="text-left px-6 py-3 font-medium">Business Name</th>
                <th className="text-left px-6 py-3 font-medium">Phone</th>
                <th className="text-left px-6 py-3 font-medium">Email</th>
                <th className="text-left px-6 py-3 font-medium">Decision Maker</th>
                <th className="text-left px-6 py-3 font-medium">Status</th>
                <th className="text-left px-6 py-3 font-medium">Confidence</th>
                <th className="text-left px-6 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-[var(--muted)]">
                    Loading...
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-[var(--muted)]">
                    No leads found.{" "}
                    <Link href="/" className="text-[var(--primary)] hover:underline">
                      Run the agent
                    </Link>{" "}
                    to generate leads.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr
                    key={lead.id}
                    className="border-b border-[var(--border)] hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-3 font-medium">{lead.business_name}</td>
                    <td className="px-6 py-3">{lead.phone_number || "—"}</td>
                    <td className="px-6 py-3 max-w-[200px] truncate">
                      {lead.email_address || "—"}
                    </td>
                    <td className="px-6 py-3">{lead.decision_maker_name || "—"}</td>
                    <td className="px-6 py-3">
                      <StatusBadge status={lead.lead_status} />
                    </td>
                    <td className="px-6 py-3">
                      <ConfidenceBar score={lead.confidence_score} />
                    </td>
                    <td className="px-6 py-3">
                      <Link
                        href={`/leads/${lead.id}`}
                        className="text-[var(--primary)] hover:underline text-xs font-medium"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {pagination.totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-6">
          <button
            onClick={() => fetchLeads(pagination.page - 1)}
            disabled={pagination.page <= 1}
            className="px-3 py-1.5 rounded text-sm border border-[var(--border)] hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ← Prev
          </button>
          <div className="flex gap-1">
            {Array.from({ length: Math.min(pagination.totalPages, 7) }, (_, i) => {
              let p;
              if (pagination.totalPages <= 7) {
                p = i + 1;
              } else if (pagination.page <= 4) {
                p = i + 1;
              } else if (pagination.page >= pagination.totalPages - 3) {
                p = pagination.totalPages - 6 + i;
              } else {
                p = pagination.page - 3 + i;
              }
              return (
                <button
                  key={p}
                  onClick={() => fetchLeads(p)}
                  className={`px-3 py-1.5 rounded text-sm ${
                    p === pagination.page
                      ? "bg-[var(--primary)] text-white"
                      : "border border-[var(--border)] hover:bg-gray-50"
                  }`}
                >
                  {p}
                </button>
              );
            })}
          </div>
          <button
            onClick={() => fetchLeads(pagination.page + 1)}
            disabled={pagination.page >= pagination.totalPages}
            className="px-3 py-1.5 rounded text-sm border border-[var(--border)] hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next →
          </button>
          <span className="text-xs text-[var(--muted)] ml-2">
            Page {pagination.page} of {pagination.totalPages}
          </span>
        </div>
      )}
    </div>
  );
}
