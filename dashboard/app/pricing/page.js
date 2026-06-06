"use client";

export default function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: 49,
      leads: 50,
      features: [
        "50 qualified leads",
        "CSV export",
        "Basic contact info",
        "Email support",
      ],
      popular: false,
    },
    {
      name: "Growth",
      price: 149,
      leads: 250,
      features: [
        "250 qualified leads",
        "CSV & JSON export",
        "Full contact info",
        "Priority email support",
        "API access",
      ],
      popular: true,
    },
    {
      name: "Enterprise",
      price: 499,
      leads: 1000,
      features: [
        "1000+ qualified leads",
        "All export formats",
        "Full contact info + enrichment",
        "Dedicated support",
        "API access + webhooks",
        "Custom targeting",
      ],
      popular: false,
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-3">Pricing</h1>
        <p className="text-lg text-[var(--muted)] max-w-xl mx-auto">
          Choose the plan that fits your needs. All leads are verified and ready
          to contact.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`relative bg-[var(--surface)] border rounded-2xl p-8 ${
              plan.popular
                ? "border-[var(--primary)] ring-2 ring-[var(--primary)]"
                : "border-[var(--border)]"
            }`}
          >
            {plan.popular && (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--primary)] text-white text-xs font-semibold px-4 py-1 rounded-full">
                Most Popular
              </span>
            )}
            <h3 className="text-xl font-bold mb-1">{plan.name}</h3>
            <p className="text-3xl font-bold mb-1">
              ${plan.price}
              <span className="text-base font-normal text-[var(--muted)]"> /mo</span>
            </p>
            <p className="text-sm text-[var(--muted)] mb-6">
              {plan.leads} leads per month
            </p>
            <ul className="space-y-3 mb-8">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm">
                  <span className="text-[var(--success)] mt-0.5">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            <a
              href={`/checkout?plan=${plan.name.toLowerCase()}`}
              className={`block text-center w-full py-3 rounded-lg font-semibold transition-colors ${
                plan.popular
                  ? "bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)]"
                  : "border border-[var(--primary)] text-[var(--primary)] hover:bg-blue-50"
              }`}
            >
              Get Started
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
