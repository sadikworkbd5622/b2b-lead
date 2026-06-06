import Database from 'better-sqlite3';
import path from 'path';
import { NextResponse } from 'next/server';

const DB_PATH = path.join(process.cwd(), '..', 'data', 'leads.db');

function getDb() {
  try {
    const db = new Database(DB_PATH, { readonly: true });
    return db;
  } catch {
    return null;
  }
}

export async function GET(request) {
  const db = getDb();
  if (!db) {
    return NextResponse.json({ leads: [], stats: {}, error: 'No database found' });
  }

  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const search = searchParams.get('search');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = (page - 1) * limit;

    let whereClauses = [];
    let params = [];

    if (status && status !== 'all') {
      whereClauses.push('lead_status = ?');
      params.push(status);
    }

    if (search) {
      whereClauses.push('(business_name LIKE ? OR phone_number LIKE ? OR email_address LIKE ?)');
      const pattern = `%${search}%`;
      params.push(pattern, pattern, pattern);
    }

    const where = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

    const countRow = db.prepare(`SELECT COUNT(*) as total FROM leads ${where}`).get(...params);
    const total = countRow.total;
    const totalPages = Math.ceil(total / limit);

    const leads = db.prepare(`SELECT * FROM leads ${where} ORDER BY created_at DESC LIMIT ? OFFSET ?`).all(...params, limit, offset);

    const stats = db.prepare(`
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN lead_status LIKE '%Qualified%' THEN 1 ELSE 0 END) as qualified,
        SUM(CASE WHEN lead_status LIKE '%Rejected%' THEN 1 ELSE 0 END) as rejected,
        SUM(CASE WHEN lead_status = 'Unprocessed - LLM Unavailable' THEN 1 ELSE 0 END) as unprocessed,
        SUM(CASE WHEN lead_status = 'Discovered - Awaiting Processing' THEN 1 ELSE 0 END) as raw_discovered,
        AVG(confidence_score) as avg_confidence
      FROM leads
    `).get();

    db.close();

    return NextResponse.json({
      leads,
      stats,
      pagination: { page, limit, total, totalPages },
    });
  } catch (err) {
    db.close();
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
