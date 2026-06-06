import Database from 'better-sqlite3';
import path from 'path';
import { NextResponse } from 'next/server';

const DB_PATH = path.join(process.cwd(), '..', 'data', 'leads.db');

export async function GET() {
  try {
    const db = new Database(DB_PATH, { readonly: true });

    const stats = db.prepare(`
      SELECT
        COUNT(*) as total_leads,
        SUM(CASE WHEN lead_status LIKE '%Qualified%' THEN 1 ELSE 0 END) as qualified_leads,
        ROUND(AVG(CASE WHEN lead_status LIKE '%Qualified%' THEN confidence_score ELSE NULL END), 0) as avg_confidence,
        COUNT(DISTINCT phone_number) as unique_phones,
        COUNT(DISTINCT email_address) as unique_emails,
        DATE(MIN(created_at)) as first_lead_date,
        DATE(MAX(created_at)) as last_run_date,
        SUM(CASE WHEN lead_status LIKE '%Qualified%' AND confidence_score >= 70 THEN 1 ELSE 0 END) as high_confidence_leads
      FROM leads
    `).get();

    const statuses = db.prepare(`
      SELECT lead_status, COUNT(*) as count
      FROM leads
      GROUP BY lead_status
      ORDER BY count DESC
    `).all();

    db.close();

    return NextResponse.json({ stats, statuses });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
