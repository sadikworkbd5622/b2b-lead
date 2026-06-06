import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "LeadMarket — B2B Lead Marketplace",
  description: "Buy qualified B2B leads for your business",
};

function Navbar() {
  return (
    <nav className="border-b border-[var(--border)] bg-[var(--surface)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="text-xl font-bold text-[var(--primary)]">
            LeadMarket
          </Link>
          <div className="flex gap-6 items-center">
            <Link href="/" className="text-sm font-medium hover:text-[var(--primary)] transition-colors">
              Home
            </Link>
            <Link href="/leads" className="text-sm font-medium hover:text-[var(--primary)] transition-colors">
              Browse Leads
            </Link>
            <Link
              href="/pricing"
              className="bg-[var(--primary)] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[var(--primary-dark)] transition-colors"
            >
              Buy Leads
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)] mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-8 text-center text-sm text-[var(--muted)]">
        LeadMarket — B2B Lead Generation Marketplace
      </div>
    </footer>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
