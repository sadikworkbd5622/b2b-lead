"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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
          </p>
        </div>
        <Link
          href="/pricing"
          className="bg-[var(--primary)] text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-[var(--primary-dark)] transition-colors"
        >
          Purchase Leads
        </Link>
      </div>

      <div className="flex gap-4 mb-6 items-center">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
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
                      <span
                        className={
                          lead.lead_status?.includes("Qualified")
                            ? "text-[var(--success)]"
                            : "text-[var(--danger)]"
                        }
                      >
                        {lead.lead_status?.includes("Qualified")
                          ? "Qualified"
                          : "Rejected"}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-gray-200 rounded-full">
                          <div
                            className="h-full rounded-full bg-[var(--primary)]"
                            style={{ width: `${lead.confidence_score || 0}%` }}
                          />
                        </div>
                        <span className="text-xs">{lead.confidence_score || 0}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-3">
                      <Link
                        href={`/leads/${lead.id}`}
                        className="text-[var(--primary)] hover:underline text-xs"
                      >
                        View
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
        <div className="flex justify-center gap-2 mt-6">
          {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map(
            (p) => (
              <button
                key={p}
                onClick={() => fetchLeads(p)}
                className={`px-3 py-1 rounded text-sm ${
                  p === pagination.page
                    ? "bg-[var(--primary)] text-white"
                    : "border border-[var(--border)] hover:bg-gray-50"
                }`}
              >
                {p}
              </button>
            )
          )}
        </div>
      )}
    </div>
  );
}
