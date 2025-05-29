# Romanization Feature

This document explains the romanization functionality added to the TTSAI (Text-to-Speech AI) translation application.

## Overview

Romanization is the conversion of text from non-Latin scripts (like Chinese, Japanese, Arabic, Hindi, etc.) into Latin script for easier reading by speakers of languages that use the Latin alphabet.

## Implementation

### Backend Changes

#### 1. Advanced Translation Endpoint (`/api/advanced-translate`)

The advanced translation prompt now includes romanization for non-Latin script languages:

```python
# Languages that require romanization
non_latin_languages = ['ar', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'hi', 'ru', 'th', 'he', 'ur', 'fa', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'pa', 'ne', 'si', 'my', 'km', 'lo', 'ka', 'am', 'ti', 'dv']
```

Response format includes:
```json
{
  "pronunciation": {
    "ipa": "IPA notation",
    "syllables": "syllable breakdown", 
    "stress": "stress markers",
    "phonetic": "phonetic spelling",
    "romanization": "Latin script version",
    "romanization_system": "System used (e.g., Pinyin, Hepburn)"
  }
}
```

#### 2. Basic Translation Endpoint (`/api/translate`)

For non-Latin script target languages, the basic translation now returns:

```json
{
  "translation": "original script translation",
  "romanization": "Latin script version", 
  "romanization_system": "System name",
  "source_lang": "source language",
  "target_lang": "target language"
}
```

#### 3. Supported Romanization Systems

- **Chinese**: Pinyin
- **Japanese**: Hepburn romanization
- **Korean**: Revised Romanization of Korean
- **Arabic**: Standard Arabic romanization
- **Hindi**: IAST (International Alphabet of Sanskrit Transliteration)
- **Russian**: Scientific transliteration
- **Thai**: Royal Thai General System

### Frontend Changes

#### 1. State Management

Added romanization state management:

```javascript
// Romanization state
const [romanizationData, setRomanizationData] = useState(null);
```

#### 2. Translation Display

Basic translation view now shows romanization when available:

```javascript
{/* Display romanization if available */}
{romanizationData && romanizationData.romanization && (
  <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
      <Typography variant="body2" color="text.secondary">
        Romanization:
      </Typography>
      <Tooltip title="Copy romanization">
        <IconButton 
          size="small" 
          onClick={() => handleCopyText(romanizationData.romanization)}
        >
          <ContentCopyIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
    <Typography variant="body1" color="text.primary" sx={{ fontStyle: 'italic' }}>
      {romanizationData.romanization}
    </Typography>
    {romanizationData.romanization_system && (
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
        System: {romanizationData.romanization_system}
      </Typography>
    )}
  </Box>
)}
```

#### 3. Advanced Translation View

The advanced translation component shows romanization in the pronunciation tab:

```javascript
{translation.pronunciation.romanization && (
  <>
    <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
      Romanization: {translation.pronunciation.romanization}
    </Typography>
    {translation.pronunciation.romanization_system && (
      <Typography variant="body2" color="text.secondary">
        System: {translation.pronunciation.romanization_system}
      </Typography>
    )}
  </>
)}
```

## Usage Examples

### Basic Translation with Romanization

**Input**: "Hello, how are you?" (English to Japanese)

**Response**:
```json
{
  "translation": "こんにちは、元気ですか？",
  "romanization": "Konnichiwa, genki desu ka?",
  "romanization_system": "Hepburn",
  "source_lang": "en",
  "target_lang": "ja"
}
```

### Advanced Translation with Romanization

**Input**: "Thank you" (English to Chinese)

**Response**:
```json
{
  "main_translation": "谢谢",
  "pronunciation": {
    "ipa": "/ʃjɛ̀ʃjɛ̀/",
    "syllables": "xiè-xiè",
    "romanization": "xièxiè", 
    "romanization_system": "Pinyin"
  }
}
```

## Testing

A test script is provided to verify romanization functionality:

```bash
cd backend
python test_romanization.py
```

This script tests:
- Basic translation with romanization for various language pairs
- Advanced translation with romanization 
- API health and service availability

## Benefits

1. **Accessibility**: Makes non-Latin scripts accessible to users who can't read the original script
2. **Learning**: Helps language learners understand pronunciation
3. **Communication**: Enables easier sharing and discussion of translations
4. **Consistency**: Uses standard romanization systems for accuracy

## Language Support

Romanization is automatically provided for translations to these language families:
- **East Asian**: Chinese (Simplified/Traditional), Japanese, Korean
- **South Asian**: Hindi, Bengali, Tamil, Telugu, Malayalam, etc.
- **Middle Eastern**: Arabic, Hebrew, Persian, Urdu
- **Cyrillic**: Russian
- **Southeast Asian**: Thai, Myanmar, Khmer, Lao
- **Other**: Georgian, Armenian, Amharic

For Latin-script languages (English, Spanish, French, German, etc.), no romanization is provided as it's not needed.

## Implementation Notes

- Romanization is generated by the Gemini AI model and quality depends on the model's training
- The system automatically detects which languages need romanization
- Romanization data is cached along with translations for performance
- Users can copy romanization text independently of the main translation
- Romanization is cleared when switching languages or changing input significantly 