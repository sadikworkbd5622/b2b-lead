import Database from 'better-sqlite3';
import path from 'path';
import { NextResponse } from 'next/server';

const DB_PATH = path.join(process.cwd(), '..', 'data', 'leads.db');

export async function GET(request, { params }) {
  const { id } = await params;
  try {
    const db = new Database(DB_PATH, { readonly: true });
    const lead = db.prepare('SELECT * FROM leads WHERE id = ?').get(id);
    db.close();

    if (!lead) {
      return NextResponse.json({ error: 'Lead not found' }, { status: 404 });
    }

    return NextResponse.json({ lead });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
