# Updated main.py with PostgreSQL support
import os
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import csv
import io
from datetime import datetime, date
import re
import tempfile

# Database imports - PostgreSQL support
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3

app = FastAPI(title="Library of Babel API - Enhanced", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models (same as before)
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

# Database connection logic
def get_database_url():
    """Get database URL from environment, fallback to SQLite"""
    return os.getenv('DATABASE_URL', 'sqlite:///babel.db')

def is_postgresql():
    """Check if we're using PostgreSQL"""
    return get_database_url().startswith('postgresql://')

def get_db_connection():
    """Get database connection - PostgreSQL or SQLite"""
    db_url = get_database_url()
    
    if is_postgresql():
        # PostgreSQL connection
        try:
            # Fix for Render's PostgreSQL URL format
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            # Fallback to SQLite
            conn = sqlite3.connect('babel.db')
            conn.row_factory = sqlite3.Row
            return conn
    else:
        # SQLite connection
        conn = sqlite3.connect('babel.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_postgresql():
        # PostgreSQL table creation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                whyItStuck TEXT,
                extendedNote TEXT,
                category TEXT,
                tags TEXT,
                batch TEXT,
                dateAdded DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # SQLite table creation (fallback)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                whyItStuck TEXT,
                extendedNote TEXT,
                category TEXT,
                tags TEXT,
                batch TEXT,
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
    conn.close()

# Smart Entry Parser (same as before)
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
            r'\(([^)]+)\)$'   # Parentheses at end
        ]
        
        for pattern in source_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return 'Smart Import'

# Initialize parser
smart_parser = SmartEntryParser()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Routes (same as before but with database compatibility)
@app.get("/")
async def root():
    return {"message": "Library of Babel API - Enhanced Version is running!", "database": "PostgreSQL" if is_postgresql() else "SQLite"}

@app.get("/api/entries", response_model=List[Entry])
async def get_entries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, type, title, content, source, whyItStuck, 
               extendedNote, category, tags, batch, dateAdded
        FROM entries 
        ORDER BY created_at DESC
    ''')
    entries = cursor.fetchall()
    conn.close()
    
    result = []
    for entry in entries:
        result.append(Entry(
            id=entry['id'],
            type=entry['type'],
            title=entry['title'],
            content=entry['content'],
            source=entry['source'] or "",
            whyItStuck=entry['whyItStuck'] or "",
            extendedNote=entry['extendedNote'] or "",
            category=entry['category'] or "",
            tags=json.loads(entry['tags']) if entry['tags'] else [],
            batch=entry['batch'] or "",
            dateAdded=str(entry['dateAdded'])
        ))
    return result

@app.get("/api/entries/search", response_model=List[Entry])
async def search_entries(q: str = "", type_filter: str = "all"):
    """Basic search endpoint for frontend compatibility"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query based on parameters
    if q and type_filter != "all":
        # Search with both text and type filter
        cursor.execute('''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE (title ILIKE %s OR content ILIKE %s OR source ILIKE %s) 
            AND type = %s
            ORDER BY created_at DESC
        ''' if is_postgresql() else '''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE (title LIKE ? OR content LIKE ? OR source LIKE ?) 
            AND type = ?
            ORDER BY created_at DESC
        ''', (f"%{q}%", f"%{q}%", f"%{q}%", type_filter))
    elif q:
        # Search with text only
        cursor.execute('''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE title ILIKE %s OR content ILIKE %s OR source ILIKE %s
            ORDER BY created_at DESC
        ''' if is_postgresql() else '''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE title LIKE ? OR content LIKE ? OR source LIKE ?
            ORDER BY created_at DESC
        ''', (f"%{q}%", f"%{q}%", f"%{q}%"))
    elif type_filter != "all":
        # Filter by type only
        cursor.execute('''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE type = %s
            ORDER BY created_at DESC
        ''' if is_postgresql() else '''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            WHERE type = ?
            ORDER BY created_at DESC
        ''', (type_filter,))
    else:
        # No filters, return all
        cursor.execute('''
            SELECT id, type, title, content, source, whyItStuck, 
                   extendedNote, category, tags, batch, dateAdded
            FROM entries 
            ORDER BY created_at DESC
        ''')
    
    entries = cursor.fetchall()
    conn.close()
    
    # Format results
    result = []
    for entry in entries:
        result.append(Entry(
            id=entry['id'],
            type=entry['type'],
            title=entry['title'],
            content=entry['content'],
            source=entry['source'] or "",
            whyItStuck=entry['whyItStuck'] or "",
            extendedNote=entry['extendedNote'] or "",
            category=entry['category'] or "",
            tags=json.loads(entry['tags']) if entry['tags'] else [],
            batch=entry['batch'] or "",
            dateAdded=str(entry['dateAdded'])
        ))
    return result

@app.post("/api/entries", response_model=Entry)
async def create_entry(entry: EntryCreate):
    if not entry.dateAdded:
        entry.dateAdded = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_postgresql():
        cursor.execute('''
            INSERT INTO entries (type, title, content, source, whyItStuck, 
                               extendedNote, category, tags, batch, dateAdded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded
        ))
        entry_id = cursor.fetchone()['id']
    else:
        cursor.execute('''
            INSERT INTO entries (type, title, content, source, whyItStuck, 
                               extendedNote, category, tags, batch, dateAdded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded
        ))
        entry_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return Entry(
        id=entry_id,
        type=entry.type,
        title=entry.title,
        content=entry.content,
        source=entry.source,
        whyItStuck=entry.whyItStuck,
        extendedNote=entry.extendedNote,
        category=entry.category,
        tags=entry.tags,
        batch=entry.batch,
        dateAdded=entry.dateAdded
    )

@app.put("/api/entries/{entry_id}")
async def update_entry(entry_id: int, entry: EntryCreate):
    """Update an existing entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_postgresql():
        cursor.execute('''
            UPDATE entries 
            SET type=%s, title=%s, content=%s, source=%s, whyItStuck=%s, 
                extendedNote=%s, category=%s, tags=%s, batch=%s, dateAdded=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
        ''', (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded, entry_id
        ))
    else:
        cursor.execute('''
            UPDATE entries 
            SET type=?, title=?, content=?, source=?, whyItStuck=?, 
                extendedNote=?, category=?, tags=?, batch=?, dateAdded=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (
            entry.type, entry.title, entry.content, entry.source,
            entry.whyItStuck, entry.extendedNote, entry.category,
            json.dumps(entry.tags), entry.batch, entry.dateAdded, entry_id
        ))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")
    
    conn.commit()
    conn.close()
    
    return Entry(
        id=entry_id,
        type=entry.type,
        title=entry.title,
        content=entry.content,
        source=entry.source,
        whyItStuck=entry.whyItStuck,
        extendedNote=entry.extendedNote,
        category=entry.category,
        tags=entry.tags,
        batch=entry.batch,
        dateAdded=entry.dateAdded
    )

@app.delete("/api/entries/{entry_id}")
async def delete_entry(entry_id: int):
    """Delete an entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_postgresql():
        cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
    else:
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")
    
    conn.commit()
    conn.close()
    return {"message": "Entry deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
