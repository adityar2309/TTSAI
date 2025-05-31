# Database Migration: JSON to SQLite

This document describes the migration from JSON file-based storage to SQLite database for the TTSAI backend.

## Overview

The TTSAI backend has been migrated from using JSON files for data storage to using an SQLite database with SQLAlchemy ORM. This improves:

- **Performance**: Faster queries and better indexing
- **Data Integrity**: ACID transactions and foreign key constraints
- **Concurrency**: Better handling of multiple users
- **Scalability**: Easier to optimize and scale
- **Features**: Advanced querying, relationships, and analytics

## Database Schema

### Tables

#### `users`
- `id` (Primary Key): User identifier
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_active`: Last activity timestamp

#### `words_of_day`
- `id` (Primary Key): Auto-incrementing ID
- `language`: Language code (indexed)
- `word`: The word
- `translation`: Word translation/meaning
- `pronunciation`: IPA pronunciation
- `part_of_speech`: Grammar category
- `difficulty`: Beginner/Intermediate/Advanced
- `example_sentence`: Usage example
- `example_translation`: Example translation
- `etymology`: Word origin
- `related_words`: JSON array of related words
- `cultural_note`: Cultural context
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### `common_phrases`
- `id` (Primary Key): Auto-incrementing ID
- `language`: Language code (indexed)
- `phrase`: The phrase
- `translation`: Phrase translation
- `category`: Category (greetings, travel, etc.) (indexed)
- `difficulty`: Difficulty level (indexed)
- `pronunciation`: IPA pronunciation
- `usage_context`: When to use this phrase
- `created_at`: Creation timestamp

#### `flashcards`
- `id` (Primary Key): UUID
- `user_id` (Foreign Key): References users.id
- `original_text`: Source text
- `translated_text`: Target text
- `source_lang`: Source language
- `target_lang`: Target language
- `difficulty`: Difficulty level
- `category`: Category
- `notes`: User notes
- `review_count`: Number of reviews
- `mastery_level`: Spaced repetition level (0-5)
- `success_rate`: Review success percentage
- `next_review`: Next review date
- `last_review`: Last review date
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### `flashcard_reviews`
- `id` (Primary Key): Auto-incrementing ID
- `flashcard_id` (Foreign Key): References flashcards.id
- `correct`: Boolean indicating if review was correct
- `time_taken`: Time spent in seconds
- `timestamp`: Review timestamp

#### `quiz_scores`
- `id` (Primary Key): Auto-incrementing ID
- `user_id` (Foreign Key): References users.id
- `quiz_id`: Quiz identifier
- `score`: Quiz score (0-100)
- `total_questions`: Number of questions
- `correct_answers`: Number of correct answers
- `language`: Quiz language
- `difficulty`: Quiz difficulty
- `answers`: JSON object with user answers
- `timestamp`: Quiz completion time

#### `practice_sessions`
- `id` (Primary Key): Auto-incrementing ID
- `user_id` (Foreign Key): References users.id
- `session_type`: Type of practice (conversation, flashcard, quiz)
- `language`: Practice language
- `context`: Practice context
- `proficiency`: User proficiency level
- `duration`: Session duration in seconds
- `performance`: Performance score
- `data`: JSON object with session-specific data
- `timestamp`: Session timestamp

#### `user_preferences`
- `id` (Primary Key): Auto-incrementing ID
- `user_id` (Foreign Key): References users.id (unique)
- `default_source_lang`: Default source language
- `default_target_lang`: Default target language
- `voice_gender`: TTS voice preference
- `speech_speed`: TTS speed preference
- `auto_play_translations`: Auto-play setting
- `save_history`: History saving preference
- `theme`: UI theme preference
- `notifications_enabled`: Notification setting
- `study_reminders`: Reminder setting
- `daily_goal`: Daily study goal
- `preferred_difficulty`: Preferred difficulty level
- `updated_at`: Last update timestamp

#### `analytics`
- `id` (Primary Key): UUID
- `user_id` (Foreign Key): References users.id (nullable)
- `event_type`: Type of event (indexed)
- `event_data`: JSON object with event data
- `session_id`: Session identifier
- `user_agent`: Browser user agent
- `ip_address`: User IP address
- `timestamp`: Event timestamp (indexed)

### Indexes

- `idx_flashcards_user_lang`: (user_id, target_lang) for flashcard queries
- `idx_quiz_scores_user_lang`: (user_id, language) for quiz score queries
- `idx_practice_sessions_user`: (user_id, timestamp) for session queries
- `idx_analytics_user_event`: (user_id, event_type) for analytics queries

## Migration Process

### 1. Data Migration

The migration script (`migrate_to_sqlite.py`) converts existing JSON data:

```bash
python migrate_to_sqlite.py
```

This script:
- Creates all database tables
- Migrates word of day data from `word_of_day.json`
- Migrates common phrases from `common_phrases.json`
- Migrates user progress data from `user_progress.json`
- Migrates user preferences from `user_preferences.json`
- Migrates analytics data from `learning_analytics.json`

### 2. API Updates

All API endpoints have been updated to use the new database service:

- `/api/word-of-day` - Uses `db_service.get_word_of_day()`
- `/api/flashcards` - Uses `db_service.get_flashcards()` and `db_service.save_flashcard()`
- `/api/flashcards/{id}/review` - Uses `db_service.review_flashcard()`
- `/api/progress` - Uses `db_service.get_user_progress()`
- `/api/user/preferences` - Uses `db_service.get_user_preferences()` and `db_service.save_user_preferences()`
- `/api/analytics` - Uses `db_service.track_event()`

### 3. Database Service Layer

The `db_service.py` module provides a clean interface between the Flask app and the database:

- **Connection Management**: Automatic session handling
- **Error Handling**: Comprehensive error logging and rollback
- **Data Validation**: Input validation and sanitization
- **Performance**: Optimized queries with proper indexing
- **Relationships**: Automatic foreign key management

## Configuration

### Environment Variables

- `DATABASE_URL`: SQLite database path (default: `sqlite:///ttsai.db`)

### Development Setup

```bash
# Install dependencies
pip install sqlalchemy

# Run migration
python migrate_to_sqlite.py

# Test database
python test_db.py

# Start server
python app.py
```

### Production Deployment

The Dockerfile has been updated to:
- Install SQLite3
- Set proper database path
- Create data directory
- Handle database initialization

## Benefits of Migration

### Performance Improvements
- **Faster Queries**: SQL queries vs JSON file parsing
- **Indexing**: Proper database indexes for common queries
- **Memory Usage**: Lower memory footprint
- **Caching**: Better query optimization

### Data Integrity
- **ACID Transactions**: Atomic operations
- **Foreign Keys**: Referential integrity
- **Constraints**: Data validation at database level
- **Backups**: Standard database backup tools

### Scalability
- **Concurrent Access**: Multiple users simultaneously
- **Query Optimization**: Advanced SQL features
- **Analytics**: Complex reporting queries
- **Future Growth**: Easy to migrate to PostgreSQL/MySQL later

### Developer Experience
- **ORM Benefits**: Object-relational mapping with SQLAlchemy
- **Type Safety**: Better data modeling
- **Migrations**: Version-controlled schema changes
- **Testing**: Easier unit testing with in-memory database

## Testing

### Database Tests

Run the test suite to verify functionality:

```bash
python test_db.py
```

### Backend Integration Tests

Test the full backend with database:

```bash
python test_backend.py
```

## Maintenance

### Database Backup

```bash
# Create backup
sqlite3 ttsai.db ".backup backup.db"

# Restore backup
sqlite3 ttsai.db ".restore backup.db"
```

### Performance Monitoring

Key metrics to monitor:
- Query execution time
- Database file size
- Connection pool usage
- Cache hit rates

### Schema Updates

For future schema changes:
1. Create migration script
2. Update models.py
3. Update db_service.py
4. Test migrations
5. Deploy with proper rollback plan

## Troubleshooting

### Common Issues

1. **Database Locked Error**
   - Check for long-running transactions
   - Verify proper session cleanup

2. **Migration Failures**
   - Check file permissions
   - Verify JSON file formats
   - Review error logs

3. **Performance Issues**
   - Add missing indexes
   - Optimize query patterns
   - Check database size

### Debug Commands

```bash
# Check database schema
sqlite3 ttsai.db ".schema"

# View table data
sqlite3 ttsai.db "SELECT * FROM users LIMIT 10;"

# Check database integrity
sqlite3 ttsai.db "PRAGMA integrity_check;"
```

## Future Enhancements

- **Full-text Search**: SQLite FTS for search functionality
- **Backup Automation**: Scheduled database backups
- **Analytics Dashboard**: Advanced reporting queries
- **Migration to PostgreSQL**: For larger scale deployments
- **Read Replicas**: For improved read performance 