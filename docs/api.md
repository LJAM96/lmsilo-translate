# Translate API Reference

## Base URL
```
http://localhost:8083/api
```

## Endpoints

### Health Check
```
GET /health
```

---

## Translation

### Translate Text
```
POST /translate
```
**Request:**
```json
{
  "text": "Hello, how are you?",
  "source_lang": null,
  "target_lang": "spa_Latn"
}
```
Set `source_lang` to `null` for auto-detection.

**Response:**
```json
{
  "text": "Hello, how are you?",
  "source_lang": "eng_Latn",
  "target_lang": "spa_Latn",
  "translation": "Hola, ¿cómo estás?"
}
```

### Batch Translate
```
POST /translate/batch
```
**Request:**
```json
{
  "texts": ["Hello", "Goodbye"],
  "target_lang": "fra_Latn"
}
```

### Get Languages
```
GET /languages
```
Returns all 200+ supported NLLB languages.

---

## Models

### List Models
```
GET /models
```

### List Builtin Models
```
GET /models/builtin
```
Returns NLLB model variants.

### Register Model
```
POST /models
```
**Request:**
```json
{
  "name": "NLLB-200 Distilled 600M",
  "engine": "nllb-ct2",
  "source": "builtin",
  "model_id": "nllb-200-distilled-600M",
  "is_default": true
}
```

### Download Model
```
POST /models/{id}/download
```

### Set Default Model
```
POST /models/{id}/set-default
```

### Delete Model
```
DELETE /models/{id}
```

---

## Language Codes (NLLB)

Common codes:
| Language | Code |
|----------|------|
| English | eng_Latn |
| Spanish | spa_Latn |
| French | fra_Latn |
| German | deu_Latn |
| Chinese (Simplified) | zho_Hans |
| Arabic | arb_Arab |
| Russian | rus_Cyrl |
| Japanese | jpn_Jpan |
| Korean | kor_Hang |
| Portuguese | por_Latn |

Full list: 200+ languages via `/languages` endpoint.

---

## Error Responses
```json
{
  "detail": "Error message"
}
```
