"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { Suspense, useState } from "react";
import Link from "next/link";

function CheckoutForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const plan = searchParams.get("plan");
  const leadId = searchParams.get("lead");

  const [form, setForm] = useState({ name: "", email: "", company: "" });
  const [submitted, setSubmitted] = useState(false);

  const plans = { starter: 49, growth: 149, enterprise: 499 };
  const price = plans[plan] || (leadId ? 5 : 0);
  const title = leadId
    ? "Single Lead Purchase"
    : plan
      ? `${plan.charAt(0).toUpperCase() + plan.slice(1)} Plan`
      : "Purchase";

  function handleSubmit(e) {
    e.preventDefault();
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center">
        <div className="text-[var(--success)] text-5xl mb-4">✓</div>
        <h2 className="text-2xl font-bold mb-2">Order Received!</h2>
        <p className="text-[var(--muted)] mb-6">
          Thank you for your purchase. We will send the lead data to{" "}
          <strong>{form.email}</strong> within 24 hours.
        </p>
        <Link
          href="/leads"
          className="text-[var(--primary)] hover:underline"
        >
          Browse more leads
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <Link href="/pricing" className="text-sm text-[var(--primary)] hover:underline mb-4 inline-block">
        ← Back to pricing
      </Link>
      <h1 className="text-3xl font-bold mb-2">{title}</h1>
      <p className="text-[var(--muted)] mb-8">
        {leadId
          ? "Purchase this single lead for $5"
          : `Total: $${price}/month`}
      </p>

      <form onSubmit={handleSubmit} className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Full Name</label>
          <input
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
            placeholder="John Doe"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Email Address</label>
          <input
            required
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
            placeholder="john@company.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Company</label>
          <input
            value={form.company}
            onChange={(e) => setForm({ ...form, company: e.target.value })}
            className="w-full border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
            placeholder="Acme Inc."
          />
        </div>
        <div className="pt-4 border-t border-[var(--border)]">
          <div className="flex justify-between text-sm mb-4">
            <span>Total</span>
            <span className="font-bold text-lg">
              {leadId ? "$5.00" : `$${price}.00`}
            </span>
          </div>
          <button
            type="submit"
            className="w-full bg-[var(--primary)] text-white py-3 rounded-lg font-semibold hover:bg-[var(--primary-dark)] transition-colors"
          >
            Purchase Now
          </button>
          <p className="text-xs text-[var(--muted)] mt-3 text-center">
            Secure checkout. Your data is safe with us.
          </p>
        </div>
      </form>
    </div>
  );
}

export default function Checkout() {
  return (
    <Suspense
      fallback={
        <div className="max-w-lg mx-auto px-4 py-12 text-center text-[var(--muted)]">
          Loading...
        </div>
      }
    >
      <CheckoutForm />
    </Suspense>
  );
}
