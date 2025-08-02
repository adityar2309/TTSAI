# backend/rag_error_handler.py
"""
Enhanced error handling for RAG-based Language Learning Tutor

This module provides comprehensive error handling, logging, and recovery mechanisms
for the RAG system components.
"""

import logging
import json
import time
from functools import wraps
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RAGError(Exception):
    """Base exception for RAG system errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "RAG_UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = time.time()

class VectorServiceError(RAGError):
    """Errors related to vector service operations"""
    pass

class IndexLoadError(VectorServiceError):
    """Errors when loading vector index"""
    def __init__(self, message: str, index_path: str = None, metadata_path: str = None):
        super().__init__(message, "INDEX_LOAD_ERROR", {
            "index_path": index_path,
            "metadata_path": metadata_path
        })

class SearchError(VectorServiceError):
    """Errors during vector search operations"""
    def __init__(self, message: str, query: str = None, k: int = None):
        super().__init__(message, "SEARCH_ERROR", {
            "query": query,
            "k": k
        })

class LLMError(RAGError):
    """Errors related to LLM API calls"""
    pass

class LLMResponseError(LLMError):
    """Errors when parsing LLM responses"""
    def __init__(self, message: str, raw_response: str = None, parse_error: str = None):
        super().__init__(message, "LLM_RESPONSE_ERROR", {
            "raw_response": raw_response[:500] if raw_response else None,  # Truncate for logging
            "parse_error": str(parse_error) if parse_error else None
        })

class APIError(RAGError):
    """Errors in API endpoint handling"""
    pass

class ValidationError(APIError):
    """Request validation errors"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {
            "field": field,
            "value": str(value) if value is not None else None
        })

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Enhanced error logging with context information.
    
    Args:
        error: The exception that occurred
        context: Additional context information
    """
    context = context or {}
    
    if isinstance(error, RAGError):
        logger.error(
            f"RAG Error [{error.error_code}]: {error.message}",
            extra={
                "error_code": error.error_code,
                "error_details": error.details,
                "timestamp": error.timestamp,
                "context": context
            },
            exc_info=True
        )
    else:
        logger.error(
            f"Unexpected error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "context": context
            },
            exc_info=True
        )

def handle_vector_service_errors(func):
    """
    Decorator for vector service methods to handle errors gracefully.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FileNotFoundError as e:
            error = IndexLoadError(
                f"Vector index files not found: {str(e)}",
                index_path=getattr(self, '_last_index_path', None),
                metadata_path=getattr(self, '_last_metadata_path', None)
            )
            log_error(error, {"method": func.__name__, "args": args, "kwargs": kwargs})
            return None if func.__name__ == 'load_index' else []
        except json.JSONDecodeError as e:
            error = IndexLoadError(
                f"Failed to parse metadata JSON: {str(e)}",
                metadata_path=getattr(self, '_last_metadata_path', None)
            )
            log_error(error, {"method": func.__name__})
            return None if func.__name__ == 'load_index' else []
        except Exception as e:
            if func.__name__ == 'search':
                error = SearchError(
                    f"Vector search failed: {str(e)}",
                    query=args[0] if args else None,
                    k=args[1] if len(args) > 1 else kwargs.get('k')
                )
            else:
                error = VectorServiceError(f"Vector service error in {func.__name__}: {str(e)}")
            
            log_error(error, {"method": func.__name__, "args": args, "kwargs": kwargs})
            return None if func.__name__ == 'load_index' else []
    
    return wrapper

def handle_api_errors(func):
    """
    Decorator for API endpoints to handle errors gracefully.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            log_error(e, {"endpoint": func.__name__})
            return {
                "error": e.message,
                "error_code": e.error_code,
                "details": e.details
            }, 400
        except LLMError as e:
            log_error(e, {"endpoint": func.__name__})
            return {
                "error": "Failed to generate explanation due to LLM service issues",
                "error_code": e.error_code,
                "details": "Please try again later"
            }, 503
        except VectorServiceError as e:
            log_error(e, {"endpoint": func.__name__})
            # Vector service errors shouldn't fail the request, just log and continue
            logger.warning(f"Vector service unavailable, falling back to LLM-only: {e.message}")
            return func(*args, **kwargs)  # Retry without vector context
        except RAGError as e:
            log_error(e, {"endpoint": func.__name__})
            return {
                "error": e.message,
                "error_code": e.error_code
            }, 500
        except Exception as e:
            log_error(e, {"endpoint": func.__name__})
            return {
                "error": "An unexpected error occurred",
                "error_code": "INTERNAL_SERVER_ERROR"
            }, 500
    
    return wrapper

def create_fallback_explanation(query: str, language: str, error_context: str = None) -> Dict[str, Any]:
    """
    Create a fallback explanation when the main RAG pipeline fails.
    
    Args:
        query: The original query text
        language: The target language
        error_context: Context about what went wrong
        
    Returns:
        Dict containing a basic explanation structure
    """
    return {
        "meaning": f"The phrase '{query}' in {language} requires further analysis. " + 
                  (f"({error_context})" if error_context else "Please try again later."),
        "examples": [
            {
                "sentence": f"Example usage of '{query}' would be provided here.",
                "translation": "English translation would be provided here."
            }
        ],
        "grammar_tip": "Grammar analysis would be provided with a properly formatted response.",
        "cultural_insight": "Cultural context would be provided with a properly formatted response."
    }

def validate_explanation_response(data: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Validate and sanitize explanation response data.
    
    Args:
        data: The explanation data to validate
        query: The original query for fallback content
        
    Returns:
        Dict containing validated explanation data
    """
    required_keys = ['meaning', 'examples', 'grammar_tip', 'cultural_insight']
    
    # Ensure all required keys exist
    for key in required_keys:
        if key not in data or not data[key]:
            if key == 'examples':
                data[key] = [{"sentence": f"Example with '{query}'", "translation": "English translation"}]
            else:
                data[key] = f"Information about {key.replace('_', ' ')} would be provided here."
    
    # Validate examples structure
    if not isinstance(data.get('examples'), list):
        data['examples'] = [{"sentence": f"Example with '{query}'", "translation": "English translation"}]
    
    # Ensure each example has required fields
    validated_examples = []
    for example in data['examples']:
        if isinstance(example, dict) and 'sentence' in example:
            validated_examples.append({
                'sentence': str(example.get('sentence', f"Example with '{query}'")),
                'translation': str(example.get('translation', 'English translation'))
            })
        elif isinstance(example, str):
            validated_examples.append({
                'sentence': example,
                'translation': 'Translation would be provided here.'
            })
    
    if not validated_examples:
        validated_examples = [{"sentence": f"Example with '{query}'", "translation": "English translation"}]
    
    data['examples'] = validated_examples
    
    # Ensure string fields are strings
    for key in ['meaning', 'grammar_tip', 'cultural_insight']:
        data[key] = str(data.get(key, f"Information about {key.replace('_', ' ')} would be provided here."))
    
    return data

def get_error_stats() -> Dict[str, Any]:
    """
    Get error statistics for monitoring and debugging.
    
    Returns:
        Dict containing error statistics
    """
    # This would typically integrate with a monitoring system
    # For now, return basic stats
    return {
        "error_tracking": "enabled",
        "last_check": time.time(),
        "status": "operational"
    }