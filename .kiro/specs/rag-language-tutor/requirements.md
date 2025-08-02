# Requirements Document

## Introduction

The RAG-based Language Learning Tutor is an advanced feature that enhances the existing language learning application by providing detailed, context-aware explanations for translated words and phrases. This feature leverages Retrieval-Augmented Generation (RAG) architecture to combine the power of the Gemini LLM with relevant information from the application's knowledge base, including Word of the Day entries and Common Phrases data. Users will receive comprehensive explanations that include meaning, examples, grammar tips, and cultural insights, making their language learning experience more enriching and effective.

## Requirements

### Requirement 1

**User Story:** As a language learner, I want to get detailed explanations for translated words or phrases, so that I can better understand their usage, context, and cultural significance.

#### Acceptance Criteria

1. WHEN a user has translated text displayed in the translator interface THEN the system SHALL provide an "Explain" button or similar UI element
2. WHEN a user clicks the "Explain" button THEN the system SHALL retrieve relevant context from the knowledge base using vector similarity search
3. WHEN relevant context is found THEN the system SHALL augment the LLM prompt with this context to generate a comprehensive explanation
4. WHEN the explanation is generated THEN the system SHALL display it in a structured format with sections for meaning, examples, grammar tips, and cultural insights
5. IF no relevant context is found in the knowledge base THEN the system SHALL still generate an explanation using the LLM's general knowledge and indicate that specific examples were not found

### Requirement 2

**User Story:** As a language learner, I want the tutor explanations to be based on the application's existing knowledge base, so that I receive consistent and relevant information that aligns with the content I'm already learning.

#### Acceptance Criteria

1. WHEN the system initializes the knowledge base THEN it SHALL process existing Word of the Day entries and Common Phrases data into vector embeddings
2. WHEN processing Word of the Day entries THEN the system SHALL include example sentences and cultural notes as separate searchable documents
3. WHEN processing Common Phrases THEN the system SHALL include phrase translations and category information as searchable documents
4. WHEN performing similarity search THEN the system SHALL use sentence transformers to encode queries and find the most relevant documents
5. WHEN retrieving context THEN the system SHALL filter results by the target language to ensure relevance
6. WHEN the knowledge base is empty THEN the system SHALL gracefully handle the situation and rely on general LLM knowledge

### Requirement 3

**User Story:** As a language learner, I want the tutor explanations to be well-structured and comprehensive, so that I can easily understand different aspects of the word or phrase.

#### Acceptance Criteria

1. WHEN generating an explanation THEN the system SHALL include a "Meaning & Nuances" section that explains literal meaning and subtle connotations
2. WHEN generating an explanation THEN the system SHALL provide 2-3 practical example sentences with English translations
3. WHEN generating an explanation THEN the system SHALL include a relevant grammar tip related to the phrase
4. WHEN generating an explanation THEN the system SHALL offer cultural insights when applicable
5. WHEN displaying the explanation THEN the system SHALL format it as a structured JSON response with specific keys: "meaning", "examples", "grammar_tip", "cultural_insight"
6. WHEN showing examples THEN each example SHALL include both the sentence in the target language and its English translation

### Requirement 4

**User Story:** As a language learner, I want the tutor feature to be easily accessible and provide visual feedback, so that I can use it intuitively without confusion.

#### Acceptance Criteria

1. WHEN translated text is available THEN the system SHALL display the "Explain" button in an accessible location near the translation output
2. WHEN the user clicks the "Explain" button THEN the system SHALL show a loading indicator while processing the request
3. WHEN the explanation is being generated THEN the system SHALL disable the "Explain" button to prevent duplicate requests
4. WHEN the explanation is ready THEN the system SHALL display it in a visually distinct component below the translation
5. WHEN no translation is available THEN the system SHALL disable the "Explain" button and show appropriate messaging if clicked
6. WHEN an error occurs THEN the system SHALL display a user-friendly error message and allow the user to retry

### Requirement 5

**User Story:** As a system administrator, I want the RAG system to be performant and maintainable, so that it can handle user requests efficiently without impacting the overall application performance.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL load the pre-built vector index from disk if available
2. WHEN the vector index is not found THEN the system SHALL log appropriate warnings and continue with LLM-only explanations
3. WHEN performing vector searches THEN the system SHALL limit results to the top 5 most similar documents to balance relevance and performance
4. WHEN generating embeddings THEN the system SHALL use the 'all-MiniLM-L6-v2' model for consistency and efficiency
5. WHEN storing the vector index THEN the system SHALL use FAISS with cosine similarity for fast retrieval
6. WHEN the knowledge base needs updating THEN the system SHALL provide a separate script to rebuild the vector index from the current database

### Requirement 6

**User Story:** As a developer, I want the RAG system to be properly integrated with the existing codebase, so that it follows established patterns and can be easily maintained.

#### Acceptance Criteria

1. WHEN implementing the backend service THEN the system SHALL create a dedicated VectorService class to manage embeddings and searches
2. WHEN adding the API endpoint THEN the system SHALL follow existing Flask routing patterns and include proper error handling
3. WHEN implementing the frontend component THEN the system SHALL use Material-UI components consistent with the existing design system
4. WHEN integrating with the translator THEN the system SHALL add the tutor functionality without disrupting existing translation features
5. WHEN handling API responses THEN the system SHALL include proper JSON parsing and error handling for malformed responses
6. WHEN managing dependencies THEN the system SHALL add required libraries (sentence-transformers, faiss-cpu) to requirements.txt