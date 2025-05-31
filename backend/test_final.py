#!/usr/bin/env python3
"""
Final test to verify database is ready for deployment
"""

from db_service import db_service
from models import get_db_session, WordOfDay, CommonPhrase

def test_database_readiness():
    """Test that database is properly populated"""
    print("Testing database readiness for deployment...")
    
    # Test word of day
    word = db_service.get_word_of_day('en')
    print(f'✓ Word of day test: {word["word"] if word else "No data"}')
    
    # Test database stats
    db = get_db_session()
    try:
        word_count = db.query(WordOfDay).count()
        phrase_count = db.query(CommonPhrase).count()
        print(f'✓ Database stats: {word_count} words, {phrase_count} phrases')
        
        # Test specific language
        if word_count > 0:
            languages = db.query(WordOfDay.language).distinct().all()
            lang_list = [lang[0] for lang in languages]
            print(f'✓ Available languages: {", ".join(lang_list)}')
        
        return word_count > 0 and phrase_count > 0
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_database_readiness()
    if success:
        print("\n🎉 Database is ready for deployment!")
    else:
        print("\n❌ Database needs to be populated before deployment") 