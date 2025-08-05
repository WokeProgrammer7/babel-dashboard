import React, { useState, useEffect } from 'react';
import { Search, Plus, Moon, Sun, BookOpen, Quote, User, Lightbulb, ExternalLink, X, Eye, Edit, Trash2 } from 'lucide-react';

// Auto-detect API URL based on environment
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://babel-dashboard.onrender.com'  // Your live Render URL
  : 'http://localhost:8000';

const LibraryOfBabel = () => {
  const [entries, setEntries] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [loading, setLoading] = useState(true);

  // Fetch entries from API
  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/entries`);
      if (response.ok) {
        const data = await response.json();
        setEntries(data);
        console.log('Loaded entries:', data);
      } else {
        console.error('Failed to fetch entries');
      }
    } catch (error) {
      console.error('Error fetching entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const [newEntry, setNewEntry] = useState({
    type: 'word',
    title: '',
    content: '',
    source: '',
    whyItStuck: '',
    extendedNote: '',
    category: '',
    tags: [],
    batch: '',
    dateAdded: new Date().toISOString().split('T')[0]
  });

  // Search entries using API
  const performSearch = async (query, filter) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/entries/search?q=${encodeURIComponent(query)}&type_filter=${filter}`
      );
      if (response.ok) {
        const data = await response.json();
        setEntries(data);
      }
    } catch (error) {
      console.error('Error searching entries:', error);
    }
  };

  // Update search when term or filter changes
  useEffect(() => {
    if (searchTerm || selectedFilter !== 'all') {
      performSearch(searchTerm, selectedFilter);
    } else {
      fetchEntries();
    }
  }, [searchTerm, selectedFilter]);

  const filteredEntries = entries;

  const getTypeIcon = (type) => {
    switch (type) {
      case 'word': return <BookOpen className="w-4 h-4" />;
      case 'phrase': return <Quote className="w-4 h-4" />;
      case 'author': return <User className="w-4 h-4" />;
      case 'concept': return <Lightbulb className="w-4 h-4" />;
      case 'excerpt': return <Quote className="w-4 h-4" />;
      default: return <BookOpen className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type) => {
    if (darkMode) {
      switch (type) {
        case 'word': return 'bg-blue-900/30 text-blue-300 border-blue-700/50';
        case 'phrase': return 'bg-emerald-900/30 text-emerald-300 border-emerald-700/50';
        case 'author': return 'bg-purple-900/30 text-purple-300 border-purple-700/50';
        case 'concept': return 'bg-amber-900/30 text-amber-300 border-amber-700/50';
        case 'excerpt': return 'bg-rose-900/30 text-rose-300 border-rose-700/50';
        default: return 'bg-gray-700/30 text-gray-300 border-gray-600/50';
      }
    } else {
      switch (type) {
        case 'word': return 'bg-blue-50 text-blue-700 border-blue-200';
        case 'phrase': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
        case 'author': return 'bg-purple-50 text-purple-700 border-purple-200';
        case 'concept': return 'bg-amber-50 text-amber-700 border-amber-200';
        case 'excerpt': return 'bg-rose-50 text-rose-700 border-rose-200';
        default: return 'bg-gray-50 text-gray-700 border-gray-200';
      }
    }
  };

  const handleAddEntry = async () => {
    if (newEntry.title && newEntry.content) {
      try {
        const response = await fetch(`${API_BASE}/api/entries`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newEntry),
        });

        if (response.ok) {
          const savedEntry = await response.json();
          setEntries([savedEntry, ...entries]);
          setNewEntry({
            type: 'word',
            title: '',
            content: '',
            source: '',
            whyItStuck: '',
            extendedNote: '',
            category: '',
            tags: [],
            batch: '',
            dateAdded: new Date().toISOString().split('T')[0]
          });
          setShowAddForm(false);
        } else {
          console.error('Failed to save entry');
        }
      } catch (error) {
        console.error('Error saving entry:', error);
      }
    }
  };

  const handleEditEntry = async () => {
    if (editingEntry && editingEntry.title && editingEntry.content) {
      try {
        const response = await fetch(`${API_BASE}/api/entries/${editingEntry.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(editingEntry),
        });

        if (response.ok) {
          const updatedEntry = await response.json();
          setEntries(entries.map(entry => 
            entry.id === updatedEntry.id ? updatedEntry : entry
          ));
          setEditingEntry(null);
        } else {
          console.error('Failed to update entry');
        }
      } catch (error) {
        console.error('Error updating entry:', error);
      }
    }
  };

  const handleDeleteEntry = async (entryId) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      try {
        const response = await fetch(`${API_BASE}/api/entries/${entryId}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          setEntries(entries.filter(entry => entry.id !== entryId));
          setSelectedEntry(null);
        } else {
          console.error('Failed to delete entry');
        }
      } catch (error) {
        console.error('Error deleting entry:', error);
      }
    }
  };

  const themeClasses = darkMode 
    ? 'min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-800 text-gray-100'
    : 'min-h-screen bg-gradient-to-br from-stone-50 via-amber-50 to-orange-50 text-gray-900';

  const cardClasses = darkMode
    ? 'bg-gray-800/50 border-gray-700/50 backdrop-blur-sm'
    : 'bg-white/80 border-gray-200 backdrop-blur-sm';

  const inputClasses = darkMode
    ? 'bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400 focus:ring-amber-500 focus:border-amber-500'
    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-amber-500 focus:border-amber-500';

  if (loading) {
    return (
      <div className={themeClasses}>
        <div className="container mx-auto px-4 py-8 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto mb-4"></div>
            <p className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Loading your library...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={themeClasses}>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-light tracking-wide mb-2">Library of Babel</h1>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} italic font-light`}>
                This repository begins where the myth ends. It embraces fragmentation not as failure, but as foundation.
              </p>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-3 rounded-full transition-colors ${
                darkMode 
                  ? 'bg-gray-700 hover:bg-gray-600 text-amber-400' 
                  : 'bg-white hover:bg-gray-50 text-amber-600 shadow-sm border'
              }`}
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <div className={`${cardClasses} rounded-xl shadow-sm border p-6 mb-8`}>
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search words, phrases, sources, tags..."
                className={`w-full pl-10 pr-4 py-3 ${inputClasses} rounded-lg transition-colors`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="flex gap-3">
              <select
                className={`px-4 py-3 ${inputClasses} rounded-lg transition-colors`}
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value)}
              >
                <option value="all">All Types</option>
                <option value="word">Words</option>
                <option value="phrase">Phrases</option>
                <option value="author">Authors</option>
                <option value="concept">Concepts</option>
                <option value="excerpt">Excerpts</option>
              </select>
              <button
                onClick={() => setShowStats(!showStats)}
                className={`px-4 py-3 rounded-lg transition-colors flex items-center gap-2 ${
                  darkMode
                    ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                <Eye className="w-4 h-4" />
                Stats
              </button>
              <button
                onClick={() => setShowAddForm(true)}
                className="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors flex items-center gap-2 font-medium"
              >
                <Plus className="w-4 h-4" />
                Add Entry
              </button>
            </div>
          </div>
        </div>

        {showStats && (
          <div className={`${cardClasses} rounded-xl shadow-sm border p-6 mb-8`}>
            <h3 className={`text-lg font-medium mb-4 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
              Collection Statistics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {['word', 'phrase', 'author', 'concept', 'excerpt'].map(type => {
                const count = entries.filter(e => e.type === type).length;
                const filteredCount = filteredEntries.filter(e => e.type === type).length;
                return (
                  <div key={type} className={`p-4 rounded-lg border ${darkMode ? 'bg-gray-700/30 border-gray-600' : 'bg-gray-50 border-gray-200'}`}>
                    <div className={`inline-flex items-center justify-center w-10 h-10 rounded-full ${getTypeColor(type)} mb-3`}>
                      {getTypeIcon(type)}
                    </div>
                    <div className={`text-2xl font-bold ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>
                      {selectedFilter === 'all' ? count : filteredCount}
                    </div>
                    <div className={`text-sm capitalize ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                      {type}s
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filteredEntries.map(entry => (
            <div 
              key={entry.id} 
              className={`${cardClasses} rounded-xl shadow-sm border hover:shadow-lg transition-all duration-200 group relative`}
            >
              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingEntry({...entry});
                  }}
                  className={`p-2 rounded-full transition-colors ${
                    darkMode
                      ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                  }`}
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteEntry(entry.id);
                  }}
                  className="p-2 rounded-full bg-red-100 hover:bg-red-200 text-red-600 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div 
                className="p-6 cursor-pointer"
                onClick={() => setSelectedEntry(entry)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${getTypeColor(entry.type)}`}>
                    {getTypeIcon(entry.type)}
                    {entry.type}
                  </div>
                  <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400" />
                </div>
                
                <h3 className={`font-semibold text-lg mb-3 line-clamp-2 ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>
                  {entry.title}
                </h3>
                
                <p className={`text-sm mb-4 line-clamp-3 leading-relaxed ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  {entry.content}
                </p>
                
                <div className={`text-xs mb-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span className="font-medium">Source:</span> {entry.source}
                </div>
                
                {entry.tags && entry.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {entry.tags.slice(0, 3).map((tag, index) => (
                      <span 
                        key={index} 
                        className={`px-2 py-1 rounded-full text-xs ${
                          darkMode 
                            ? 'bg-gray-700 text-gray-300' 
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                
                <div className={`flex justify-between text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                  <span>{entry.batch}</span>
                  <span>{entry.dateAdded}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredEntries.length === 0 && !loading && (
          <div className="text-center py-12">
            <div className="mb-4 text-gray-400">
              <Search className="w-12 h-12 mx-auto" />
            </div>
            <p className={darkMode ? 'text-gray-400' : 'text-gray-600'}>
              No entries found. Click "Add Entry" to create your first entry!
            </p>
          </div>
        )}

        {/* Add Entry Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className={`${cardClasses} rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto`}>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className={`text-xl font-semibold ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>
                    Add New Entry
                  </h2>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className={`${darkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'}`}
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Type
                    </label>
                    <select
                      className={`w-full p-3 ${inputClasses} rounded-lg`}
                      value={newEntry.type}
                      onChange={(e) => setNewEntry({ ...newEntry, type: e.target.value })}
                    >
                      <option value="word">Word</option>
                      <option value="phrase">Phrase</option>
                      <option value="author">Author</option>
                      <option value="concept">Concept</option>
                      <option value="excerpt">Excerpt</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Title *
                    </label>
                    <input
                      type="text"
                      className={`w-full p-3 ${inputClasses} rounded-lg`}
                      value={newEntry.title}
                      onChange={(e) => setNewEntry({ ...newEntry, title: e.target.value })}
                      placeholder="Enter the word, phrase, or title..."
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Content *
                    </label>
                    <textarea
                      className={`w-full p-3 ${inputClasses} rounded-lg h-24`}
                      value={newEntry.content}
                      onChange={(e) => setNewEntry({ ...newEntry, content: e.target.value })}
                      placeholder="Definition, description, or excerpt..."
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Source/Trigger
                    </label>
                    <input
                      type="text"
                      className={`w-full p-3 ${inputClasses} rounded-lg`}
                      value={newEntry.source}
                      onChange={(e) => setNewEntry({ ...newEntry, source: e.target.value })}
                      placeholder="Where did you encounter this?"
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Why It Stuck
                    </label>
                    <textarea
                      className={`w-full p-3 ${inputClasses} rounded-lg h-20`}
                      value={newEntry.whyItStuck}
                      onChange={(e) => setNewEntry({ ...newEntry, whyItStuck: e.target.value })}
                      placeholder="What resonated about this?"
                    />
                  </div>
                </div>
                
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={handleAddEntry}
                    className="flex-1 bg-amber-600 text-white py-3 rounded-lg hover:bg-amber-700 transition-colors font-medium"
                  >
                    Add Entry
                  </button>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className={`px-6 py-3 rounded-lg transition-colors ${
                      darkMode
                        ? 'border border-gray-600 hover:bg-gray-700 text-gray-300'
                        : 'border border-gray-300 hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Edit Entry Modal */}
        {editingEntry && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className={`${cardClasses} rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto`}>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className={`text-xl font-semibold ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>
                    Edit Entry
                  </h2>
                  <button
                    onClick={() => setEditingEntry(null)}
                    className={`${darkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'}`}
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Type
                    </label>
                    <select
                      className={`w-full p-3 ${inputClasses} rounded-lg`}
                      value={editingEntry.type}
                      onChange={(e) => setEditingEntry({ ...editingEntry, type: e.target.value })}
                    >
                      <option value="word">Word</option>
                      <option value="phrase">Phrase</option>
                      <option value="author">Author</option>
                      <option value="concept">Concept</option>
                      <option value="excerpt">Excerpt</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Title *
                    </label>
                    <input
                      type="text"
                      className={`w-full p-3 ${inputClasses} rounded-lg`}
                      value={editingEntry.title}
                      onChange={(e) => setEditingEntry({ ...editingEntry, title: e.target.value })}
                      placeholder="Enter the word, phrase, or title..."
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Content *
                    </label>
                    <textarea
                      className={`w-full p-3 ${inputClasses} rounded-lg h-24`}
                      value={editingEntry.content}
                      onChange={(e) => setEditingEntry({ ...editingEntry, content: e.target.value })}
                      placeholder="Definition, description, or excerpt..."
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Source/Trigger
                    </label>
                    <input
                      type="text"
                      className={`w-full p-3 ${inputClasses} rounded-lg`}
                      value={editingEntry.source}
                      onChange={(e) => setEditingEntry({ ...editingEntry, source: e.target.value })}
                      placeholder="Where did you encounter this?"
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Why It Stuck
                    </label>
                    <textarea
                      className={`w-full p-3 ${inputClasses} rounded-lg h-20`}
                      value={editingEntry.whyItStuck}
                      onChange={(e) => setEditingEntry({ ...editingEntry, whyItStuck: e.target.value })}
                      placeholder="What resonated about this?"
                    />
                  </div>
                </div>
                
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={handleEditEntry}
                    className="flex-1 bg-amber-600 text-white py-3 rounded-lg hover:bg-amber-700 transition-colors font-medium"
                  >
                    Update Entry
                  </button>
                  <button
                    onClick={() => setEditingEntry(null)}
                    className={`px-6 py-3 rounded-lg transition-colors ${
                      darkMode
                        ? 'border border-gray-600 hover:bg-gray-700 text-gray-300'
                        : 'border border-gray-300 hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* View Entry Modal */}
        {selectedEntry && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className={`${cardClasses} rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto`}>
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border ${getTypeColor(selectedEntry.type)}`}>
                    {getTypeIcon(selectedEntry.type)}
                    {selectedEntry.type}
                  </div>
                  <button
                    onClick={() => setSelectedEntry(null)}
                    className={`${darkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'}`}
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <h2 className={`text-2xl font-bold mb-6 ${darkMode ? 'text-gray-100' : 'text-gray-900'}`}>
                  {selectedEntry.title}
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <h3 className={`font-semibold mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Content
                    </h3>
                    <p className={`whitespace-pre-line leading-relaxed ${darkMode ? 'text-gray-200' : 'text-gray-600'}`}>
                      {selectedEntry.content}
                    </p>
                  </div>
                  
                  {selectedEntry.source && (
                    <div>
                      <h3 className={`font-semibold mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        Source/Trigger
                      </h3>
                      <p className={darkMode ? 'text-gray-200' : 'text-gray-600'}>
                        {selectedEntry.source}
                      </p>
                    </div>
                  )}
                  
                  {selectedEntry.whyItStuck && (
                    <div>
                      <h3 className={`font-semibold mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        Why It Stuck
                      </h3>
                      <p className={`leading-relaxed ${darkMode ? 'text-gray-200' : 'text-gray-600'}`}>
                        {selectedEntry.whyItStuck}
                      </p>
                    </div>
                  )}
                  
                  {selectedEntry.extendedNote && (
                    <div>
                      <h3 className={`font-semibold mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        Extended Note
                      </h3>
                      <p className={`leading-relaxed ${darkMode ? 'text-gray-200' : 'text-gray-600'}`}>
                        {selectedEntry.extendedNote}
                      </p>
                    </div>
                  )}
                  
                  <div className={`pt-4 border-t ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
                    <div className={`flex justify-between text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      <span><strong>Batch:</strong> {selectedEntry.batch || 'N/A'}</span>
                      <span><strong>Added:</strong> {selectedEntry.dateAdded}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LibraryOfBabel;