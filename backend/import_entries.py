#!/usr/bin/env python3
"""
Bulk Import Script for Library of Babel
This script imports all your entries from the PDF documents into the database.
"""

import requests
import json

# Your FastAPI server URL
API_BASE = "http://localhost:8000"

# All your entries from the documents
all_entries = [
    # Batch #2 (Foundational)
    {
        "type": "word",
        "title": "Bildungsroman",
        "content": "A literary genre focused on personal growth and psychological development",
        "source": "Came up while reflecting on Digital Pensieve's emotional arc",
        "whyItStuck": "The structure of that essay mirrored a bildungsroman—a slow, retrospective coming-of-age through browser tabs",
        "extendedNote": "Keeping it in mind for future essays that chart inner change.",
        "category": "Literary Terms",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "word",
        "title": "Interregnum",
        "content": "Originally a term for the pause between governments, but metaphorically rich for writing about periods of in-betweenness—pause, drift, or reshaping",
        "source": "Recalled during a reflective language exchange—struck me for its layered eeriness",
        "whyItStuck": "It felt eerie and poetic that it reappeared now. Represents creative limbo, political pause, or emotional transition",
        "extendedNote": "Originally a term for the pause between governments, but metaphorically rich for writing about periods of in-betweenness—pause, drift, or reshaping",
        "category": "Temporal Concepts",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "concept",
        "title": "Adagio & Allegro",
        "content": "Musical metaphor for writing pace and life phases. Adagio = slow, meditative, careful. Allegro = fast, fluid, expressive",
        "source": "Surfaced during a writing dialogue on tone and narrative rhythm while reworking the coda",
        "whyItStuck": "Gave a language to my own process—slow reflective edits vs sudden inspired bursts",
        "extendedNote": "These can describe writing pace, mood shifts, and even life phases",
        "category": "Writing Process",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "author",
        "title": "Isaiah Berlin",
        "content": "His pluralist framework resonates deeply with how I try to hold complexity in essays",
        "source": "Referenced during a layered discussion on contradiction and truth in personal writing",
        "whyItStuck": "His pluralist framework resonates deeply with how I try to hold complexity in essays",
        "extendedNote": "Freedom for the wolves has often meant death to the sheep. Themes: Liberty, moral complexity, intellectual humility",
        "category": "Philosophical Thinkers",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "author",
        "title": "Albert Camus",
        "content": "His resilience and grace under chaos echoed what I was reaching for in tone",
        "source": "Emerged in a conversation about emotional steadiness amidst absurdity",
        "whyItStuck": "His resilience and grace under chaos echoed what I was reaching for in tone",
        "extendedNote": "In the depth of winter, I finally learned that within me lay an invincible summer. Themes: Absurdism, dignity, emotional steadiness",
        "category": "Philosophical Thinkers",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "author",
        "title": "Milan Kundera",
        "content": "His obsession with what's remembered and what's lost paralleled my own preoccupations",
        "source": "Came up while discussing memory, erasure, and archival practices",
        "whyItStuck": "His obsession with what's remembered and what's lost paralleled my own preoccupations",
        "extendedNote": "The struggle of man against power is the struggle of memory against forgetting. Themes: Memory, resistance, digital documentation",
        "category": "Literary Influences",
        "tags": ["The Library Without a Roof", "Memory"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "author",
        "title": "Italo Calvino",
        "content": "His modular, poetic structures feel like a blueprint for the kind of writing I want to do",
        "source": "Mentioned during a meta-conversation about how I store language and ideas",
        "whyItStuck": "His modular, poetic structures feel like a blueprint for the kind of writing I want to do",
        "extendedNote": "Suggested Reading: Invisible Cities, If on a Winter's Night a Traveler. Themes: Memory architecture, lyrical structure, metafiction",
        "category": "Literary Influences",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "author",
        "title": "Marshall McLuhan",
        "content": "The medium is the message maps well onto how I think about browser tabs, notes, essays as format",
        "source": "Brought in during a reflection on writing form and tech",
        "whyItStuck": "The medium is the message maps well onto how I think about browser tabs, notes, essays as format",
        "extendedNote": "Themes: Form as message, media shapes perception",
        "category": "Media Theory",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },
    {
        "type": "word",
        "title": "Skein",
        "content": "Tangle of thread or flock of birds; metaphor for complexity and pattern. Keeping this one for cities and stories with knots.",
        "source": "Used by me in describing Chandni Chowk's spatial density",
        "whyItStuck": "It captured the layered, interwoven nature of streets, memory, and history",
        "extendedNote": "Tangle of thread or flock of birds; metaphor for complexity and pattern. Keeping this one for cities and stories with knots.",
        "category": "Spatial Metaphors",
        "tags": [],
        "batch": "Batch #2 (Foundational)",
        "dateAdded": "2025-01-15"
    },

    # Batch #3 (Anora & NYT Language Finds)
    {
        "type": "phrase",
        "title": "Her Glass Slipper Is a Swarovski Stiletto",
        "content": "Gorgeous twist on the Cinderella metaphor. The glass slipper becomes a hyper-curated symbol of glamor and consumerism.",
        "source": "NYT review of Anora",
        "whyItStuck": "Gorgeous twist on the Cinderella metaphor. The glass slipper becomes a hyper-curated symbol of glamor and consumerism.",
        "extendedNote": "Glass slipper = innocence, transformation. Swarovski stiletto = performance, image, commodity. Could be used in critique of modern fairy tales, Instagram femininity, love as lifestyle branding",
        "category": "Cultural Critique",
        "tags": ["Modern Metaphors"],
        "batch": "Batch #3 (Anora & NYT Language Finds)",
        "dateAdded": "2025-01-20"
    },
    {
        "type": "word",
        "title": "ingénue",
        "content": "French origin; means innocent/naïve woman in plays/films. Useful for critiquing gender tropes or reinterpreting them with irony",
        "source": "NYT article, lexicon tag",
        "whyItStuck": "Elegant word for a type—innocent, often scripted female role",
        "extendedNote": "French origin; means innocent/naïve woman in plays/films. Useful for critiquing gender tropes or reinterpreting them with irony",
        "category": "Gender & Performance",
        "tags": [],
        "batch": "Batch #3 (Anora & NYT Language Finds)",
        "dateAdded": "2025-01-20"
    },
    {
        "type": "phrase",
        "title": "At one point, characters walk, or really stalk, down the boardwalk as night falls.",
        "content": "The shift from walk to stalk electrifies the mood. Perfect example of tone-pivot through word choice.",
        "source": "NYT review of Anora",
        "whyItStuck": "The shift from walk to stalk electrifies the mood. Perfect example of tone-pivot through word choice.",
        "extendedNote": "A great tool for injecting menace or intent into plain sentences—will use this next time I need to raise the stakes without spelling it out",
        "category": "Writing Technique",
        "tags": [],
        "batch": "Batch #3 (Anora & NYT Language Finds)",
        "dateAdded": "2025-01-20"
    },
    {
        "type": "phrase",
        "title": "From diegetic to non-diegetic and back again",
        "content": "Diegetic = within the world of the character. Non-diegetic = only audience hears it. Might use this to map internal vs external awareness in essays",
        "source": "Used in article's description of film's soundscape",
        "whyItStuck": "Good for describing immersion vs narrative control—could work metaphorically in nonfiction too",
        "extendedNote": "Diegetic = within the world of the character. Non-diegetic = only audience hears it. Might use this to map internal vs external awareness in essays",
        "category": "Narrative Theory",
        "tags": [],
        "batch": "Batch #3 (Anora & NYT Language Finds)",
        "dateAdded": "2025-01-20"
    },
    {
        "type": "word",
        "title": "verisimilitude",
        "content": "It's about seeming real—not being real. Makes it ideal for writing about perception, fiction, and memory",
        "source": "Referenced in article vocab",
        "whyItStuck": "It's about seeming real—not being real. Makes it ideal for writing about perception, fiction, and memory",
        "extendedNote": "Useful when I want to write about post-truth, memoir, or aesthetic realism that still bends fact",
        "category": "Truth & Perception",
        "tags": [],
        "batch": "Batch #3 (Anora & NYT Language Finds)",
        "dateAdded": "2025-01-20"
    },

    # Batch #4 (11 April 2025)
    {
        "type": "phrase",
        "title": "If we ran on the audacity of hope, why did we govern on the possible?",
        "content": "A soft-spoken critique disguised as a rhetorical question. Lays bare the tension between campaign ideals and administrative caution.",
        "source": "Jon Stewart segment questioning the gap between Obama-era rhetoric and policy delivery",
        "whyItStuck": "A soft-spoken critique disguised as a rhetorical question. Lays bare the tension between campaign ideals and administrative caution. Also doubles as a framework for asking why ambition fades at the moment of application.",
        "extendedNote": "Filed under: Political Rhetoric, Expectation vs Execution",
        "category": "Political Rhetoric",
        "tags": ["Expectation vs Execution"],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "concept",
        "title": "Talmudic Structure",
        "content": "Frames ambiguity as method, not weakness. The Talmud privileges multi-voiced logic and sustained contradiction.",
        "source": "Rahm Emanuel's reply to Jon Stewart—described the answer as Talmudic—yes and no",
        "whyItStuck": "Frames ambiguity as method, not weakness. The Talmud privileges multi-voiced logic and sustained contradiction. Useful for describing arguments, essays, or decisions that are intentionally unresolved.",
        "extendedNote": "Yes and no becomes not evasion, but architecture. Applies to structures built around dialogue rather than conclusion",
        "category": "Form & Method",
        "tags": ["Philosophical Metaphors"],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "excerpt",
        "title": "the wreck and not the story of the wreck...",
        "content": "the wreck and not the story of the wreck\nthe thing itself and not the myth\nthe drowning face always staring\ntoward the sun\nthe evidence of damage\nworn by salt and sway into this threadbare beauty\nthe ribs of the disaster\ncurving their assertion\namong the tentative haunters.",
        "source": "Found on CEPT essay prize info page (Adrienne Rich, Diving into the Wreck)",
        "whyItStuck": "Rejects myth in favor of the damaged original. Values direct encounter with history, pain, and memory over interpretation. One of those anchor-texts that recalibrate what writing is for.",
        "extendedNote": "Filed under: Poetic Orientation, Myth vs Material",
        "category": "Poetic Orientation",
        "tags": ["Myth vs Material"],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "word",
        "title": "Infructuous",
        "content": "Means fruitless, legally or materially. Often found in legal filings (petition rendered infructuous). Useful when writing about doctrine that outpaces enforcement",
        "source": "Appeared in a discussion about how constitutional benches uphold rights without providing direct relief",
        "whyItStuck": "Captures the frustration of symbolic progress with no practical outcome. Particularly sharp when discussing judgments that expand jurisprudence while leaving petitioners empty-handed.",
        "extendedNote": "Means fruitless, legally or materially. Often found in legal filings (petition rendered infructuous). Useful when writing about doctrine that outpaces enforcement",
        "category": "Legal Language",
        "tags": ["The Library Without a Roof"],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "word",
        "title": "Desiderata",
        "content": "From Latin; plural of desideratum. Ideal for formal registers, policy documents, or philosophical lists of what should be",
        "source": "Found in a Print article critiquing India's U.S. policy—technology transfers have been our desiderata",
        "whyItStuck": "A rare, elegant way of naming aspirations that remain unfulfilled. Makes longing sound procedural. Useful in writing that names absence without sentimentality.",
        "extendedNote": "From Latin; plural of desideratum. Ideal for formal registers, policy documents, or philosophical lists of what should be. Can also link to poetic traditions (e.g., Max Ehrmann's Desiderata)",
        "category": "Policy Language",
        "tags": [],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "excerpt",
        "title": "You have brains in your head...",
        "content": "You have brains in your head.\nYou have feet in your shoes.\nYou can steer yourself any direction you choose.\nYou're on your own. And you know what you know.\nAnd YOU are the guy who'll decide where to go.",
        "source": "Dr. Seuss, Oh, the Places You'll Go!",
        "whyItStuck": "Unironically affirming. A distilled philosophy of agency that's impossible to forget. Simple, yes—but not simplistic.",
        "extendedNote": "Filed under: Poetic Orientation, Voice & Self",
        "category": "Voice & Self",
        "tags": [],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "phrase",
        "title": "Late-night Etruscan decision-making processes",
        "content": "Refers (actually) to Persians deliberating drunk, then confirming decisions sober. Misremembering it as Etruscan just adds to the charm",
        "source": "New York Times profile of Matt Levine; phrase recalled by friend Elie Mystal, later corrected by Levine to refer to Herodotus' anecdote about the Persians",
        "whyItStuck": "A perfect storm of wrong attribution, footnote-corrected history, and deadpan intellectualism. The phrase mocks our tendency to over-theorize even small social choices.",
        "extendedNote": "Classic Levinian tone: funny, precise, and footnoted",
        "category": "Smart Absurdism",
        "tags": ["Cultural References", "Historical Toneplay"],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },
    {
        "type": "word",
        "title": "Exegeses",
        "content": "Traditionally used in religious or literary contexts. In Levine's case, signals close reading as performance—daily, deliberate, and reader-specific",
        "source": "New York Times profile of Matt Levine—described as writing Wall Street exegeses",
        "whyItStuck": "Reframes financial commentary as interpretive labor. Elevates the act of explanation into something ritualistic and intellectually patterned.",
        "extendedNote": "Useful term for any genre of writing that attempts to extract meaning from complexity",
        "category": "Interpretive Frames",
        "tags": ["Finance-as-Language"],
        "batch": "Batch #4 (11 April 2025)",
        "dateAdded": "2025-04-11"
    },

    # Batch #5 (The Hindu and The Crown)
    {
        "type": "phrase",
        "title": "Continuously letting poetry win without allowing scholarship to lose",
        "content": "Captures the delicate balance in literary translation—holding onto feeling without letting go of fidelity. It reframes translation not as compromise, but as an act of tension well-managed.",
        "source": "The Hindu Sunday Magazine article Gained in Translation by Milli Krishnan",
        "whyItStuck": "Captures the delicate balance in literary translation—holding onto feeling without letting go of fidelity. It reframes translation not as compromise, but as an act of tension well-managed.",
        "extendedNote": "Filed under: Poetic Orientation, Translation Philosophy",
        "category": "Translation Philosophy",
        "tags": [],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "word",
        "title": "Gesso",
        "content": "A white primer used to prepare a canvas or surface for painting. Used metaphorically to describe feelings and emotions as the priming layer beneath language",
        "source": "Used metaphorically in the same article to describe feelings and emotions as the priming layer beneath language",
        "whyItStuck": "The image is precise—emotion as the invisible preparation that allows words to stick, to mean. Resonates with how tone and interiority precede articulation.",
        "extendedNote": "Filed under: Word Log, Material Metaphor, Language and Feeling",
        "category": "Material Metaphor",
        "tags": ["Language and Feeling"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "phrase",
        "title": "Gained in Translation",
        "content": "An inversion of the familiar phrase lost in translation. Here, translation is not a loss but a literary surplus—a creative act that adds rather than subtracts.",
        "source": "Title of the same article",
        "whyItStuck": "An inversion of the familiar phrase lost in translation. Here, translation is not a loss but a literary surplus—a creative act that adds rather than subtracts.",
        "extendedNote": "Filed under: Titles & Phrases, Linguistic Framing, Reversals",
        "category": "Linguistic Framing",
        "tags": ["Reversals"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "phrase",
        "title": "Strawberries or throne?",
        "content": "Richard III's disarming request for strawberries, while plotting regicide, becomes a moment of theatrical suspense. It's a phrase that now stands in for any veiled decision, coded request, or power cloaked in calm.",
        "source": "The Hindu Sunday Magazine, article on Richard III by Indira Parthasarathy",
        "whyItStuck": "Richard III's disarming request for strawberries, while plotting regicide, becomes a moment of theatrical suspense. It's a phrase that now stands in for any veiled decision, coded request, or power cloaked in calm.",
        "extendedNote": "Filed under: Literary Turns, Power & Language, Symbolic Compression",
        "category": "Power & Language",
        "tags": ["Symbolic Compression"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "concept",
        "title": "History as protagonist",
        "content": "History, in Shakespeare, is not setting—it acts. The article argues that it recurs as a force rather than as backdrop. The tragedies aren't about characters in history—they're about history doing the tragic work itself.",
        "source": "Same article's interpretation of Shakespeare's historical plays",
        "whyItStuck": "History, in Shakespeare, is not setting—it acts. The article argues that it recurs as a force rather than as backdrop. The tragedies aren't about characters in history—they're about history doing the tragic work itself.",
        "extendedNote": "Filed under: Structural Metaphors, Historiography, Shakespeare",
        "category": "Structural Metaphors",
        "tags": ["Historiography", "Shakespeare"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "concept",
        "title": "Michelangelo, Calvin, Cervantes, Shakespeare",
        "content": "This juxtaposition creates a symbolic framework—Shakespeare born in the shadow of Michelangelo's imagination and Calvin's morality, and dying with Cervantes, the father of modern narrative.",
        "source": "Opening of the Richard III article noting Shakespeare's birth and death alongside other towering figures",
        "whyItStuck": "This juxtaposition creates a symbolic framework—Shakespeare born in the shadow of Michelangelo's imagination and Calvin's morality, and dying with Cervantes, the father of modern narrative. The author subtly suggests that Shakespeare's work is a synthesis of these forces: form and faith, body and belief, realism and myth.",
        "extendedNote": "Michelangelo (d. 1564): Renaissance humanist; the imagination made visible. John Calvin (d. 1564): Protestant reformer; theological austerity and discipline. Cervantes (d. 1616): Don Quixote, the first modern novel—ironic, self-aware, structurally fractured",
        "category": "Literary Chronologies",
        "tags": ["Intellectual Lineage", "Structural Synthesis"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "word",
        "title": "Palaver",
        "content": "Prolonged or unnecessarily elaborate talk or fuss. Describes the now-strange effort of deciding what to delete in a digital world where remembering is frictionless.",
        "source": "Guardian article referencing Viktor Mayer-Schönberger's Delete",
        "whyItStuck": "Describes the now-strange effort of deciding what to delete in a digital world where remembering is frictionless. Carries a lightly ironic tone—mocking the bureaucratic or cognitive overhead of once-ordinary acts.",
        "extendedNote": "Filed under: Word Log, Digital Memory, Rhetorical Tone",
        "category": "Digital Memory",
        "tags": ["Rhetorical Tone"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "word",
        "title": "Peroration",
        "content": "The concluding part of a speech, intended to inspire, summarize, or drive home a final point",
        "source": "The Crown (TV series), used by a newscaster to describe Geoffrey Howe's speech",
        "whyItStuck": "It marked the quiet moment when rhetoric became action—Howe's words weren't loud, but they cracked something open in the political structure around Thatcher.",
        "extendedNote": "Filed under: Word Log, Political Rhetoric, Classical Structure",
        "category": "Political Rhetoric",
        "tags": ["Classical Structure"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "phrase",
        "title": "Estoppel by Silence",
        "content": "A legal doctrine barring a party from asserting something if their previous silence caused another to act to their detriment",
        "source": "The Good Wife courtroom scene",
        "whyItStuck": "Sounds literary, almost poetic—but is deeply legal. A form of accountability for inaction. Suggests that silence can carry implication, even intent.",
        "extendedNote": "Filed under: Legal Language, Rhetorical Force, Silence-as-Action",
        "category": "Legal Language",
        "tags": ["Rhetorical Force", "Silence-as-Action"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "word",
        "title": "Sesquipedalian",
        "content": "A person who uses long words. Characterized by long, obscure vocabulary",
        "source": "Instagram post mocking overcomplicated language",
        "whyItStuck": "The word makes fun of itself while describing the kind of person who would use it. It's a joke that loops back on itself—perfectly Babel.",
        "extendedNote": "Filed under: Word Log, Meta-Lexicon, Rhetorical Tone",
        "category": "Meta-Lexicon",
        "tags": ["Rhetorical Tone"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    },
    {
        "type": "word",
        "title": "Syllabificated",
        "content": "A mock or invented word used to describe something made of too many syllables or overly complicated language",
        "source": "Same Instagram post as sesquipedalian",
        "whyItStuck": "A parody of bad academic diction. Sounds smart at first glance, but reveals itself as inflated nonsense—like language mimicking depth.",
        "extendedNote": "Filed under: Word Log, Comic Lexicon, Mock-Intellectualism",
        "category": "Comic Lexicon",
        "tags": ["Mock-Intellectualism"],
        "batch": "Batch #5 (The Hindu and The Crown)",
        "dateAdded": "2025-04-15"
    }
]

def import_entries():
    """Import all entries to the FastAPI backend"""
    print(f"🚀 Starting bulk import of {len(all_entries)} entries...")
    print(f"📡 API Base: {API_BASE}")
    
    success_count = 0
    error_count = 0
    
    for i, entry in enumerate(all_entries, 1):
        try:
            print(f"📝 [{i:2d}/{len(all_entries)}] Importing: {entry['title'][:50]}...")
            
            response = requests.post(
                f"{API_BASE}/api/entries",
                json=entry,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"    ✅ Success!")
            else:
                error_count += 1
                print(f"    ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            error_count += 1
            print(f"    ❌ Error: {str(e)}")
    
    print(f"\n🎉 Import Complete!")
    print(f"✅ Successfully imported: {success_count} entries")
    print(f"❌ Failed to import: {error_count} entries")
    print(f"📊 Total processed: {success_count + error_count} entries")
    
    if success_count > 0:
        print(f"\n🌐 Check your app at: http://localhost:5173")
        print(f"📊 API endpoint: {API_BASE}/api/entries")

def clear_existing_entries():
    """Optional: Clear existing entries before import"""
    try:
        response = requests.get(f"{API_BASE}/api/entries")
        if response.status_code == 200:
            existing_entries = response.json()
            print(f"⚠️  Found {len(existing_entries)} existing entries")
            
            choice = input("Do you want to clear existing entries first? (y/N): ").lower()
            if choice == 'y':
                # Note: You'd need to implement a DELETE endpoint in your FastAPI
                print("ℹ️  Clear functionality would need a DELETE endpoint in your API")
                print("ℹ️  For now, new entries will be added alongside existing ones")
    except Exception as e:
        print(f"⚠️  Could not check existing entries: {e}")

if __name__ == "__main__":
    print("🏛️  Library of Babel - Bulk Import Tool")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ FastAPI server is running!")
        else:
            print("❌ FastAPI server responded with error")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to FastAPI server!")
        print("💡 Make sure your backend is running: python main.py")
        print(f"💡 Expected server at: {API_BASE}")
        exit(1)
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        exit(1)
    
    # Optional: Clear existing entries
    clear_existing_entries()
    
    print("\n🚀 Starting import process...")
    import_entries()
    
    print("\n🎯 Next steps:")
    print("1. Open http://localhost:5173 in your browser")  
    print("2. Your Library of Babel should now have all entries!")
    print("3. Try searching, filtering, and exploring your collection")
    print("4. Ready to deploy to Railway when you are!")