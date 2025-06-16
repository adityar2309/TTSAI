#!/usr/bin/env python3
"""
Comprehensive script to populate word-of-day data for multiple languages
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models import create_tables
from backend.db_service import db_service
import json

# Comprehensive word data for multiple languages
MULTILINGUAL_WORDS = {
    'en': [
        {
            'word': 'hello',
            'translation': 'a greeting or expression of goodwill',
            'pronunciation': 'həˈloʊ',
            'part_of_speech': 'interjection',
            'difficulty': 'beginner',
            'example_sentence': 'Hello, how are you today?',
            'example_translation': 'A common greeting used when meeting someone.',
            'etymology': 'From Old English hæl (whole, healthy)',
            'related_words': ['hi', 'greetings', 'salutation'],
            'cultural_note': 'The most common greeting in English-speaking countries.'
        },
        {
            'word': 'serendipity',
            'translation': 'the occurrence of events by chance in a happy way',
            'pronunciation': 'ˌser.ənˈdɪp.ə.ti',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'It was pure serendipity that we met at the coffee shop.',
            'example_translation': 'Describes pleasant surprises or fortunate accidents.',
            'etymology': 'Coined by Horace Walpole in 1754 from the Persian fairy tale',
            'related_words': ['chance', 'fortune', 'luck', 'coincidence'],
            'cultural_note': 'A beloved English word expressing life\'s pleasant surprises.'
        },
        {
            'word': 'wanderlust',
            'translation': 'a strong desire to travel and explore the world',
            'pronunciation': 'ˈwɒn.də.lʌst',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Her wanderlust led her to visit 30 countries.',
            'example_translation': 'Used to describe someone with a passion for traveling.',
            'etymology': 'From German wandern (to hike) + lust (desire)',
            'related_words': ['travel', 'adventure', 'exploration'],
            'cultural_note': 'Reflects the human desire for exploration and discovery.'
        }
    ],
    'es': [
        {
            'word': 'sobremesa',
            'translation': 'time spent at the table after finishing a meal',
            'pronunciation': 'so.βɾeˈme.sa',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'La sobremesa duró más que la cena.',
            'example_translation': 'The after-dinner conversation lasted longer than dinner.',
            'etymology': 'From sobre (over) + mesa (table)',
            'related_words': ['charla', 'conversación', 'tertulia'],
            'cultural_note': 'An important social custom in Spanish-speaking countries.'
        },
        {
            'word': 'duende',
            'translation': 'a quality of passion and inspiration, especially in flamenco',
            'pronunciation': 'ˈdwen.de',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'El bailaor de flamenco tiene mucho duende.',
            'example_translation': 'The flamenco dancer has great spirit and charm.',
            'etymology': 'From dueño (owner), originally meaning a magical creature',
            'related_words': ['alma', 'espíritu', 'pasión'],
            'cultural_note': 'Essential concept in flamenco and Spanish arts.'
        }
    ],
    'fr': [
        {
            'word': 'dépaysement',
            'translation': 'the feeling of being in a foreign place',
            'pronunciation': 'de.pɛ.iz.mɑ̃',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Le dépaysement total lors de mon premier voyage à Tokyo.',
            'example_translation': 'The complete feeling of displacement during my first trip to Tokyo.',
            'etymology': 'From dé- (un-) + pays (country)',
            'related_words': ['voyage', 'étranger', 'expatriation'],
            'cultural_note': 'Unique French concept with no direct English equivalent.'
        },
        {
            'word': 'flâner',
            'translation': 'to wander aimlessly with pleasure',
            'pronunciation': 'flɑ.ne',
            'part_of_speech': 'verb',
            'difficulty': 'intermediate',
            'example_sentence': 'J\'aime flâner dans les rues de Paris.',
            'example_translation': 'I love strolling through the streets of Paris.',
            'etymology': 'From Old Norse flana (to rush about)',
            'related_words': ['se promener', 'errer', 'déambuler'],
            'cultural_note': 'Central to Parisian culture and the art of leisurely observation.'
        }
    ],
    'de': [
        {
            'word': 'Fernweh',
            'translation': 'longing for distant places; wanderlust',
            'pronunciation': 'ˈfɛʁn.veː',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Sie hat Fernweh nach den Bergen.',
            'example_translation': 'She longs for the mountains.',
            'etymology': 'From fern (far) + Weh (pain)',
            'related_words': ['Heimweh', 'Reisefieber', 'Wanderlust'],
            'cultural_note': 'Reflects German romantic ideals of travel and exploration.'
        },
        {
            'word': 'Gemütlichkeit',
            'translation': 'warmth, coziness, and good cheer',
            'pronunciation': 'ɡəˈmyːt.lɪç.kaɪt',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Die Gemütlichkeit des Cafés lädt zum Verweilen ein.',
            'example_translation': 'The coziness of the café invites you to linger.',
            'etymology': 'From Gemüt (mind, spirit) + -lich (like) + -keit (-ness)',
            'related_words': ['Behaglichkeit', 'Wärme', 'Geborgenheit'],
            'cultural_note': 'Central to German culture and hospitality.'
        }
    ],
    'ja': [
        {
            'word': '木漏れ日',
            'translation': 'sunlight filtering through trees',
            'pronunciation': 'ko-mo-re-bi',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '木漏れ日が森の中で踊っている。',
            'example_translation': 'Sunlight is dancing through the trees in the forest.',
            'etymology': 'From 木 (tree) + 漏れ (leak) + 日 (sun)',
            'related_words': ['日光', '森林', '陽射し'],
            'cultural_note': 'Reflects Japanese appreciation for subtle natural beauty.'
        },
        {
            'word': 'もったいない',
            'translation': 'regret over waste; too good to waste',
            'pronunciation': 'mot-tai-nai',
            'part_of_speech': 'adjective',
            'difficulty': 'intermediate',
            'example_sentence': 'まだ食べられるのに捨てるなんてもったいない。',
            'example_translation': 'It\'s wasteful to throw it away when it\'s still edible.',
            'etymology': 'From Buddhist concept of intrinsic value',
            'related_words': ['無駄', '惜しい', '節約'],
            'cultural_note': 'Reflects Japanese values of conservation and respect for resources.'
        }
    ],
    'zh': [
        {
            'word': '缘分',
            'translation': 'predestined relationship or connection',
            'pronunciation': 'yuán-fèn',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '我们能相遇真是缘分。',
            'example_translation': 'Our meeting is truly fate.',
            'etymology': 'From 缘 (connection) + 分 (portion)',
            'related_words': ['命运', '缘份', '注定'],
            'cultural_note': 'Important concept in Chinese philosophy and relationships.'
        },
        {
            'word': '面子',
            'translation': 'face; dignity and reputation in social contexts',
            'pronunciation': 'miàn-zi',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '给他留点面子吧。',
            'example_translation': 'Let\'s save some face for him.',
            'etymology': 'From 面 (face) + 子 (suffix)',
            'related_words': ['尊严', '脸面', '声誉'],
            'cultural_note': 'Crucial concept in Chinese social interactions.'
        }
    ],
    'it': [
        {
            'word': 'dolce far niente',
            'translation': 'the sweetness of doing nothing',
            'pronunciation': 'ˈdol.tʃe far ˈnjen.te',
            'part_of_speech': 'phrase',
            'difficulty': 'intermediate',
            'example_sentence': 'Oggi ho voglia di dolce far niente.',
            'example_translation': 'Today I feel like enjoying the sweetness of doing nothing.',
            'etymology': 'From dolce (sweet) + far (to do) + niente (nothing)',
            'related_words': ['riposo', 'relax', 'ozio'],
            'cultural_note': 'Italian appreciation for leisure and contemplation.'
        },
        {
            'word': 'passeggiata',
            'translation': 'evening stroll for socializing',
            'pronunciation': 'pas.sed.ˈdʒa.ta',
            'part_of_speech': 'noun',
            'difficulty': 'beginner',
            'example_sentence': 'Facciamo una passeggiata in centro?',
            'example_translation': 'Shall we take a stroll in the city center?',
            'etymology': 'From passeggiare (to walk, to stroll)',
            'related_words': ['camminata', 'giro', 'passeggiate'],
            'cultural_note': 'Important Italian social tradition, especially in small towns.'
        }
    ],
    'pt': [
        {
            'word': 'saudade',
            'translation': 'deep nostalgic longing for something absent',
            'pronunciation': 'saw.ˈda.dʒi',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Tenho saudade dos tempos de escola.',
            'example_translation': 'I have nostalgia for school days.',
            'etymology': 'From Latin solitas (solitude)',
            'related_words': ['nostalgia', 'longing', 'melancolia'],
            'cultural_note': 'Quintessential Portuguese emotion, untranslatable to other languages.'
        },
        {
            'word': 'cafuné',
            'translation': 'gently running fingers through someone\'s hair',
            'pronunciation': 'ka.fu.ˈnɛ',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Ela fazia cafuné no filho para ele dormir.',
            'example_translation': 'She gently stroked her son\'s hair to help him sleep.',
            'etymology': 'From African languages brought to Brazil',
            'related_words': ['carinho', 'caricia', 'mimo'],
            'cultural_note': 'Tender gesture common in Brazilian family relationships.'
        }
    ]
}

def populate_all_languages():
    """Populate word-of-day data for all languages"""
    print("🌍 Populating multilingual word-of-day database...")
    print("=" * 60)
    
    # Ensure database tables exist
    create_tables()
    
    total_added = 0
    total_failed = 0
    
    for language, words in MULTILINGUAL_WORDS.items():
        print(f"\n📚 Processing {language.upper()} ({len(words)} words)...")
        added_count = 0
        failed_count = 0
        
        for word_data in words:
            success = db_service.add_word_of_day(language, word_data)
            if success:
                added_count += 1
                total_added += 1
                print(f"  ✅ Added: {word_data['word']}")
            else:
                failed_count += 1
                total_failed += 1
                print(f"  ❌ Failed: {word_data['word']}")
        
        print(f"  📊 {language.upper()}: {added_count} added, {failed_count} failed")
        
        # Verify by getting a random word
        test_word = db_service.get_word_of_day(language)
        if test_word:
            print(f"  🔍 Verification: Found '{test_word['word']}'")
        else:
            print(f"  ⚠️  Verification failed for {language}")
    
    print("\n" + "=" * 60)
    print(f"🎉 COMPLETION SUMMARY:")
    print(f"   📊 Total words added: {total_added}")
    print(f"   ❌ Total failures: {total_failed}")
    print(f"   🌐 Languages processed: {len(MULTILINGUAL_WORDS)}")
    print(f"   ✨ Available languages: {', '.join(MULTILINGUAL_WORDS.keys())}")
    
    return total_added, total_failed

def test_random_words():
    """Test by getting random words from each language"""
    print("\n🎲 Testing random word retrieval...")
    print("-" * 40)
    
    for language in MULTILINGUAL_WORDS.keys():
        word_data = db_service.get_word_of_day(language)
        if word_data:
            print(f"🇺🇳 {language.upper()}: {word_data['word']} - {word_data['translation'][:50]}...")
        else:
            print(f"❌ {language.upper()}: No words found")

if __name__ == "__main__":
    try:
        added, failed = populate_all_languages()
        test_random_words()
        
        if added > 0:
            print(f"\n🎊 SUCCESS! Added {added} words across {len(MULTILINGUAL_WORDS)} languages!")
        else:
            print(f"\n💔 FAILED! No words were added to the database.")
            
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc() 