from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import csv
import io
import re
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

app = FastAPI(title="Library of Babel API - Enhanced", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Pydantic Models ---
class Entry(BaseModel):
    id: Optional[int] = None
    type: str
    title: str
    content: str
    source: str
    whyItStuck: str
    extendedNote: str
    category: str
    tags: List[str] = []
    batch: str
    dateAdded: str

class EntryCreate(BaseModel):
    type: str
    title: str
    content: str
    source: str = ""
    whyItStuck: str = ""
    extendedNote: str = ""
    category: str = ""
    tags: List[str] = []
    batch: str = ""
    dateAdded: Optional[str] = None

class SmartEntryResponse(BaseModel):
    suggested_entries: List[Dict[str, Any]]
    raw_text: str
    processing_notes: str

class AdvancedSearchParams(BaseModel):
    query: str = ""
    types: List[str] = []
    categories: List[str] = []
    tags: List[str] = []
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    batch: str = ""

# --- Database Helper Functions ---
def get_db_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        result = urlparse(DATABASE_URL)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port or 5432

        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
        )
        return conn
    else:
        conn = sqlite3.connect("babel.db")
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if os.environ.get("DATABASE_URL"):
        # PostgreSQL schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT DEFAULT '',
            whyItStuck TEXT DEFAULT '',
            extendedNote TEXT DEFAULT '',
            category TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            batch TEXT DEFAULT '',
            dateAdded TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            event_type TEXT NOT NULL,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    else:
        # SQLite schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT DEFAULT '',
            whyItStuck TEXT DEFAULT '',
            extendedNote TEXT DEFAULT '',
            category TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            batch TEXT DEFAULT '',
            dateAdded TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

# --- Smart Entry Parser (from your original code) ---
class SmartEntryParser:
    def __init__(self):
        self.type_keywords = {
            'word': ['word', 'term', 'vocabulary', 'definition'],
            'phrase': ['phrase', 'saying', 'expression', 'quote'],
            'author': ['author', 'writer', 'said', 'argues', 'writes'],
            'concept': ['concept', 'idea', 'theory', 'framework', 'approach'],
            'excerpt': ['excerpt', 'passage', 'text', 'reading']
        }
        
        self.category_keywords = {
            'Literary Terms': ['literary', 'genre', 'narrative', 'writing', 'essay'],
            'Philosophical Thinkers': ['philosophy', 'philosophical', 'thinker', 'argues'],
            'Cultural Critique': ['culture', 'society', 'critique', 'analysis'],
            'Writing Process': ['writing', 'process', 'editing', 'draft'],
            'Political Rhetoric': ['political', 'politics', 'rhetoric', 'speech'],
            'Legal Language': ['legal', 'law', 'court', 'doctrine'],
            'Translation Philosophy': ['translation', 'translate', 'language'],
            'Material Metaphor': ['metaphor', 'symbolism', 'represents']
        }

    def parse_unstructured_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse unstructured text into potential entries"""
        entries = []
        # Split text into potential entries (by double newlines, bullets, or numbers)
        segments = re.split(r'\n\s*\n|^\d+\.|^[-•*]\s+', text, flags=re.MULTILINE)
        segments = [s.strip() for s in segments if s.strip()]
        
        for segment in segments:
            if len(segment) < 20:  # Skip very short segments
                continue
            entry = self.extract_entry_from_segment(segment)
            if entry:
                entries.append(entry)
        return entries

    def extract_entry_from_segment(self, segment: str) -> Optional[Dict[str, Any]]:
        """Extract a structured entry from a text segment"""
        lines = [line.strip() for line in segment.split('\n') if line.strip()]
        if not lines:
            return None

        # Try to identify title (usually first line or quoted text)
        title = self.extract_title(lines)
        content = self.extract_content(lines, title)
        entry_type = self.determine_type(segment)
        category = self.determine_category(segment)
        source = self.extract_source(segment)

        # Create structured entry
        entry = {
            'type': entry_type,
            'title': title,
            'content': content,
            'source': source,
            'whyItStuck': '',
            'extendedNote': '',
            'category': category,
            'tags': [],
            'batch': f'Smart Import {datetime.now().strftime("%Y-%m-%d")}',
            'dateAdded': datetime.now().strftime("%Y-%m-%d")
        }
        return entry

    def extract_title(self, lines: List[str]) -> str:
        """Extract title from lines"""
        first_line = lines[0]
        # Look for quoted text
        quoted = re.search(r'"([^"]+)"', first_line)
        if quoted:
            return quoted.group(1)
        
        # Look for emphasized text (ALL CAPS, bold markers)
        if first_line.isupper() and len(first_line) < 100:
            return first_line
        
        # Look for single words or short phrases at start
        words = first_line.split()
        if len(words) <= 5 and len(first_line) < 50:
            return first_line
        
        # Extract first meaningful phrase
        sentences = re.split(r'[.!?]', first_line)
        if sentences and len(sentences[0]) < 100:
            return sentences[0].strip()
        
        # Fallback: first 50 characters
        return first_line[:50].strip()

    def extract_content(self, lines: List[str], title: str) -> str:
        """Extract main content, excluding title"""
        content_lines = []
        title_found = False
        for line in lines:
            if not title_found and title in line:
                # Include the line but remove the title part
                remaining = line.replace(title, '').strip(' -:')
                if remaining:
                    content_lines.append(remaining)
                title_found = True
            elif title_found or title not in line:
                content_lines.append(line)
        
        if not content_lines and lines:
            # If no content found, use everything except first line
            content_lines = lines[1:]
        
        return ' '.join(content_lines).strip()

    def determine_type(self, text: str) -> str:
        """Determine entry type based on content"""
        text_lower = text.lower()
        
        # Score each type
        type_scores = {}
        for entry_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            type_scores[entry_type] = score
        
        # Additional heuristics
        if '"' in text and text.count('"') >= 2:
            type_scores['excerpt'] = type_scores.get('excerpt', 0) + 2
        if any(word in text_lower for word in ['definition', 'means', 'refers to']):
            type_scores['word'] = type_scores.get('word', 0) + 2
        if len(text.split()) > 50:
            type_scores['excerpt'] = type_scores.get('excerpt', 0) + 1
        
        # Return type with highest score, default to 'concept'
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return 'concept'

    def determine_category(self, text: str) -> str:
        """Determine category based on content"""
        text_lower = text.lower()
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        if category_scores:
            max_score = max(category_scores.values())
            if max_score > 0:
                return max(category_scores, key=category_scores.get)
        return 'General'

    def extract_source(self, text: str) -> str:
        """Extract source information"""
        # Look for common source patterns
        source_patterns = [
            r'source[:\s]+([^\n]+)',
            r'from[:\s]+([^\n]+)',
            r'via[:\s]+([^\n]+)',
            r'—([^—\n]+)$',  # Em dash at end
            r'\(([^)]+)\)$'  # Parentheses at end
        ]
        
        for pattern in source_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return 'Smart Import'

# Initialize parser
smart_parser = SmartEntryParser()

# Initialize DB at startup
@app.on_event("startup")
async def startup_event():
    init_db()

# --- API Routes ---

@app.get("/")
async def root():
    return {"message": "Library of Babel API - Enhanced Version is running!"}

# Get all entries
@app.get("/api/entries", response_model=List[Entry])
async def get_entries():
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT id, type, title, content, source, whyItStuck,
                   extendedNote, category, tags, batch, dateAdded
            FROM entries
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        # JSON decode tags
        for row in rows:
            row['tags'] = json.loads(row['tags']) if row['tags'] else []
        cursor.close()
        conn.close()
        return rows
    else:
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT id, type, title, content, source, whyItStuck,
                   extendedNote, category, tags, batch, dateAdded
            FROM entries
            ORDER BY created_at DESC
        """).fetchall()
        entries = []
        for row in rows:
            entries.append(Entry(
                id=row['id'],
                type=row['type'],
                title=row['title'],
                content=row['content'],
                source=row['source'] or "",
                whyItStuck=row['whyItStuck'] or "",
                extendedNote=row['extendedNote'] or "",
                category=row['category'] or "",
                tags=json.loads(row['tags']) if row['tags'] else [],
                batch=row['batch'] or "",
                dateAdded=row['dateAdded']
            ))
        cursor.close()
        conn.close()
        return entries

# Basic search endpoint
@app.get("/api/entries/search", response_model=List[Entry])
async def search_entries(q: str = "", type_filter: str = "all"):
    conn = get_db_connection()
    query_params = []
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        base_query = """
            SELECT id, type, title, content, source, whyItStuck,
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE TRUE
        """
        if q and type_filter != "all":
            base_query += """ AND (title ILIKE %s OR content ILIKE %s OR source ILIKE %s) AND type = %s"""
            query_params.extend([f"%{q}%", f"%{q}%", f"%{q}%", type_filter])
        elif q:
            base_query += """ AND (title ILIKE %s OR content ILIKE %s OR source ILIKE %s)"""
            query_params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        elif type_filter != "all":
            base_query += " AND type = %s"
            query_params.append(type_filter)

        base_query += " ORDER BY created_at DESC"
        cursor.execute(base_query, query_params)
        rows = cursor.fetchall()
        # decode tags
        for row in rows:
            row['tags'] = json.loads(row['tags']) if row['tags'] else []
        cursor.close()
        conn.close()
        return rows
    else:
        cursor = conn.cursor()
        base_query = """
            SELECT id, type, title, content, source, whyItStuck,
                   extendedNote, category, tags, batch, dateAdded
            FROM entries
        """
        conditions = []
        if q and type_filter != "all":
            conditions.append("(title LIKE ? OR content LIKE ? OR source LIKE ?) AND type = ?")
            query_params.extend([f"%{q}%", f"%{q}%", f"%{q}%", type_filter])
        elif q:
            conditions.append("(title LIKE ? OR content LIKE ? OR source LIKE ?)")
            query_params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        elif type_filter != "all":
            conditions.append("type = ?")
            query_params.append(type_filter)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY created_at DESC"

        rows = cursor.execute(base_query, query_params).fetchall()
        entries = []
        for row in rows:
            entries.append(Entry(
                id=row['id'],
                type=row['type'],
                title=row['title'],
                content=row['content'],
                source=row['source'] or "",
                whyItStuck=row['whyItStuck'] or "",
                extendedNote=row['extendedNote'] or "",
                category=row['category'] or "",
                tags=json.loads(row['tags']) if row['tags'] else [],
                batch=row['batch'] or "",
                dateAdded=row['dateAdded']
            ))
        cursor.close()
        conn.close()
        return entries

# Create an entry
@app.post("/api/entries", response_model=Entry)
async def create_entry(entry: EntryCreate):
    if not entry.dateAdded:
        entry.dateAdded = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries 
                (type, title, content, source, whyItStuck, extendedNote, category, tags, batch, dateAdded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded
        ))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries 
                (type, title, content, source, whyItStuck, extendedNote, category, tags, batch, dateAdded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded
        ))
        new_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
    return Entry(
        id=new_id,
        type=entry.type,
        title=entry.title,
        content=entry.content,
        source=entry.source,
        whyItStuck=entry.whyItStuck,
        extendedNote=entry.extendedNote,
        category=entry.category,
        tags=entry.tags,
        batch=entry.batch,
        dateAdded=entry.dateAdded,
    )

# Update an existing entry
@app.put("/api/entries/{entry_id}", response_model=Entry)
async def update_entry(entry_id: int, entry: EntryCreate):
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE entries SET 
                type=%s, title=%s, content=%s, source=%s, whyItStuck=%s,
                extendedNote=%s, category=%s, tags=%s, batch=%s, dateAdded=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded,
            entry_id
        ))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found")
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE entries SET 
                type=?, title=?, content=?, source=?, whyItStuck=?,
                extendedNote=?, category=?, tags=?, batch=?, dateAdded=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded,
            entry_id
        ))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found")
        conn.commit()
        cursor.close()
        conn.close()
    return Entry(id=entry_id, **entry.dict())

# Delete an entry
@app.delete("/api/entries/{entry_id}")
async def delete_entry(entry_id: int):
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id=%s", (entry_id,))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found")
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found")
        conn.commit()
        cursor.close()
        conn.close()
    return {"message": "Entry deleted successfully"}

# Advanced search endpoint
@app.post("/api/entries/advanced-search")
async def advanced_search(params: AdvancedSearchParams):
    """Advanced search with multiple filters"""
    conn = get_db_connection()
    query_params = []
    
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT id, type, title, content, source, whyItStuck,
            extendedNote, category, tags, batch, dateAdded
            FROM entries
            WHERE TRUE
        """
        
        # Text search
        if params.query:
            query += " AND (title ILIKE %s OR content ILIKE %s OR source ILIKE %s OR category ILIKE %s)"
            search_term = f"%{params.query}%"
            query_params.extend([search_term, search_term, search_term, search_term])
        
        # Type filter
        if params.types:
            placeholders = ','.join(['%s' for _ in params.types])
            query += f" AND type IN ({placeholders})"
            query_params.extend(params.types)
        
        # Category filter
        if params.categories:
            placeholders = ','.join(['%s' for _ in params.categories])
            query += f" AND category IN ({placeholders})"
            query_params.extend(params.categories)
        
        # Date range
        if params.date_from:
            query += " AND dateAdded >= %s"
            query_params.append(params.date_from)
        if params.date_to:
            query += " AND dateAdded <= %s"
            query_params.append(params.date_to)
        
        # Batch filter
        if params.batch:
            query += " AND batch ILIKE %s"
            query_params.append(f"%{params.batch}%")
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, query_params)
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format results and handle tag filtering
        result = []
        for entry in entries:
            entry_tags = json.loads(entry['tags']) if entry['tags'] else []
            # Tag filter (done in Python)
            if params.tags:
                if not any(tag in entry_tags for tag in params.tags):
                    continue
            entry['tags'] = entry_tags
            result.append(entry)
        return result
    else:
        cursor = conn.cursor()
        query = """
            SELECT id, type, title, content, source, whyItStuck,
            extendedNote, category, tags, batch, dateAdded
            FROM entries
            WHERE 1=1
        """
        
        # Text search
        if params.query:
            query += " AND (title LIKE ? OR content LIKE ? OR source LIKE ? OR category LIKE ?)"
            search_term = f"%{params.query}%"
            query_params.extend([search_term, search_term, search_term, search_term])
        
        # Type filter
        if params.types:
            placeholders = ','.join(['?' for _ in params.types])
            query += f" AND type IN ({placeholders})"
            query_params.extend(params.types)
        
        # Category filter
        if params.categories:
            placeholders = ','.join(['?' for _ in params.categories])
            query += f" AND category IN ({placeholders})"
            query_params.extend(params.categories)
        
        # Date range
        if params.date_from:
            query += " AND dateAdded >= ?"
            query_params.append(params.date_from)
        if params.date_to:
            query += " AND dateAdded <= ?"
            query_params.append(params.date_to)
        
        # Batch filter
        if params.batch:
            query += " AND batch LIKE ?"
            query_params.append(f"%{params.batch}%")
        
        query += " ORDER BY created_at DESC"
        
        entries = cursor.execute(query, query_params).fetchall()
        cursor.close()
        conn.close()
        
        # Format results
        result = []
        for entry in entries:
            entry_tags = json.loads(entry['tags']) if entry['tags'] else []
            # Tag filter (done in Python since SQLite JSON support is limited)
            if params.tags:
                if not any(tag in entry_tags for tag in params.tags):
                    continue
            
            result.append(Entry(
                id=entry['id'],
                type=entry['type'],
                title=entry['title'],
                content=entry['content'],
                source=entry['source'] or "",
                whyItStuck=entry['whyItStuck'] or "",
                extendedNote=entry['extendedNote'] or "",
                category=entry['category'] or "",
                tags=entry_tags,
                batch=entry['batch'] or "",
                dateAdded=entry['dateAdded']
            ))
        return result

# Export entries endpoint
@app.get("/api/export/{format}")
async def export_entries(format: str):
    if format not in ["json", "csv", "markdown"]:
        raise HTTPException(status_code=400, detail="Format must be json, csv, or markdown")
    
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        entries = cursor.execute("SELECT * FROM entries ORDER BY created_at DESC").fetchall()
        cursor.close()
        conn.close()

    # Common function to parse tags for each entry
    def parse_tags(entry):
        if 'tags' in entry:
            try:
                return json.loads(entry['tags']) if entry['tags'] else []
            except Exception:
                return []
        return []

    if format == "json":
        data = []
        for e in entries:
            data.append({
                'id': e['id'],
                'type': e['type'],
                'title': e['title'],
                'content': e['content'],
                'source': e.get('source', ''),
                'whyItStuck': e.get('whyItStuck', ''),
                'extendedNote': e.get('extendedNote', ''),
                'category': e.get('category', ''),
                'tags': parse_tags(e),
                'batch': e.get('batch', ''),
                'dateAdded': e.get('dateAdded', '')
            })
        json_data = json.dumps(data, indent=2)
        return StreamingResponse(
            io.StringIO(json_data),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=babel_library.json"}
        )
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'ID', 'Type', 'Title', 'Content', 'Source', 'Why It Stuck',
            'Extended Note', 'Category', 'Tags', 'Batch', 'Date Added'
        ])
        for e in entries:
            writer.writerow([
                e['id'],
                e['type'],
                e['title'],
                e['content'],
                e.get('source', ''),
                e.get('whyItStuck', ''),
                e.get('extendedNote', ''),
                e.get('category', ''),
                '; '.join(parse_tags(e)),
                e.get('batch', ''),
                e.get('dateAdded', '')
            ])
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=babel_library.csv"}
        )
    else:  # markdown
        md_content = f"# Library of Babel Export\n\nExported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        current_batch = None
        for e in entries:
            batch = e.get('batch', '') or "Uncategorized"
            if batch != current_batch:
                md_content += f"## {batch}\n\n"
                current_batch = batch
            md_content += f"### {e['title']}\n\n"
            md_content += f"**Type:** {e['type']}\n\n"
            md_content += f"**Content:** {e['content']}\n\n"
            if e.get('source'):
                md_content += f"**Source:** {e['source']}\n\n"
            if e.get('whyItStuck'):
                md_content += f"**Why it stuck:** {e['whyItStuck']}\n\n"
            if e.get('extendedNote'):
                md_content += f"**Extended note:** {e['extendedNote']}\n\n"
            if e.get('category'):
                md_content += f"**Category:** {e['category']}\n\n"
            tags = parse_tags(e)
            if tags:
                md_content += f"**Tags:** {', '.join(tags)}\n\n"
            md_content += f"**Date added:** {e.get('dateAdded', '')}\n\n"
            md_content += "---\n\n"
        return StreamingResponse(
            io.StringIO(md_content),
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=babel_library.md"}
        )

# --- Analytics Summary ---
@app.get("/api/analytics/summary")
async def get_analytics_summary():
    conn = get_db_connection()

    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM entries")
        total_entries = cursor.fetchone()[0]

        # Type breakdown
        cursor.execute("SELECT type, COUNT(*) as count FROM entries GROUP BY type ORDER BY count DESC")
        type_breakdown = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count FROM entries 
            WHERE category != '' GROUP BY category ORDER BY count DESC LIMIT 10
        """)
        category_breakdown = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Recent activity (entries per month) - simplified for PostgreSQL
        cursor.execute("""
            SELECT DATE_TRUNC('month', TO_DATE(dateAdded, 'YYYY-MM-DD')) as month,
                   COUNT(*) as count FROM entries 
            GROUP BY month ORDER BY month DESC LIMIT 12
        """)
        monthly_activity = [{"month": row[0].strftime('%Y-%m'), "count": row[1]} for row in cursor.fetchall()]

        # Tag frequency
        cursor.execute("SELECT tags FROM entries WHERE tags != ''")
        tag_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        tag_frequency = {}
        for (tags_json,) in tag_rows:
            tags = json.loads(tags_json) if tags_json else []
            for tag in tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        top_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        top_tags_list = [{"tag": t, "count": c} for t, c in top_tags]
    else:
        cursor = conn.cursor()
        
        # Basic stats
        total_entries = cursor.execute("SELECT COUNT(*) FROM entries").fetchone()[0]

        # Type breakdown
        type_stats = cursor.execute("""
            SELECT type, COUNT(*) as count
            FROM entries
            GROUP BY type
            ORDER BY count DESC
        """).fetchall()
        type_breakdown = [{"type": row['type'], "count": row['count']} for row in type_stats]

        # Category breakdown
        category_stats = cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM entries
            WHERE category != ''
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()
        category_breakdown = [{"category": row['category'], "count": row['count']} for row in category_stats]

        # Recent activity (entries per month)
        activity_stats = cursor.execute("""
            SELECT
                strftime('%Y-%m', dateAdded) as month,
                COUNT(*) as count
            FROM entries
            GROUP BY strftime('%Y-%m', dateAdded)
            ORDER BY month DESC
            LIMIT 12
        """).fetchall()
        monthly_activity = [{"month": row['month'], "count": row['count']} for row in activity_stats]

        # Tag frequency
        all_entries = cursor.execute("SELECT tags FROM entries WHERE tags != ''").fetchall()
        tag_frequency = {}
        for entry in all_entries:
            tags = json.loads(entry['tags'])
            for tag in tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

        # Sort tags by frequency
        top_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        top_tags_list = [{"tag": tag, "count": count} for tag, count in top_tags]
        
        cursor.close()
        conn.close()

    return {
        "total_entries": total_entries,
        "type_breakdown": type_breakdown,
        "category_breakdown": category_breakdown,
        "monthly_activity": monthly_activity,
        "top_tags": top_tags_list,
        "generated_at": datetime.now().isoformat()
    }

# --- Smart Entry Upload ---
@app.post("/api/entries/smart-create")
async def smart_create_entries(file: UploadFile = File(...)):
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="Please upload a .txt or .md file")
    content = await file.read()
    text = content.decode('utf-8')

    # Parse with smart parser
    suggested_entries = smart_parser.parse_unstructured_text(text)

    # Log analytics event in DB
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analytics (event_type, event_data) VALUES (%s, %s)
        """, ("smart_upload", json.dumps({"filename": file.filename, "entries_found": len(suggested_entries)})))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analytics (event_type, event_data) VALUES (?, ?)
        """, ("smart_upload", json.dumps({"filename": file.filename, "entries_found": len(suggested_entries)})))
        conn.commit()
        cursor.close()
        conn.close()

    return SmartEntryResponse(
        suggested_entries=suggested_entries,
        raw_text=text,
        processing_notes=f"Found {len(suggested_entries)} potential entries from your notes. Review and edit before saving!"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)