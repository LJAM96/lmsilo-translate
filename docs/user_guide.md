# Translate User Guide

## Overview
Translate is an AI-powered translation tool using Meta's NLLB-200 model. It supports 200+ languages including many low-resource languages often underserved by commercial services.

## Getting Started

### Access
Navigate to **http://localhost:8083** in your browser.

### Translate Text
1. Enter text in the **Source** panel
2. Select target language (or leave source as auto-detect)
3. Click **Translate**
4. Copy result from the **Translation** panel

## Features

### Auto-Detection
Leave source language as "Auto-detect" to automatically identify the input language.

### Language Swap
Click the swap button (↔) to reverse source and target languages and swap text.

### Copy to Clipboard
Click the copy button to copy translation to clipboard.

### Model Management
Access **Models** page from the navigation to:
- View installed translation models
- Download new NLLB variants
- Set default model
- Search HuggingFace for models

## Models

### NLLB Variants
| Model | Size | VRAM | Quality |
|-------|------|------|---------|
| Distilled 600M | 1.2GB | 2GB | Good |
| Distilled 1.3B | 2.6GB | 4GB | Better |
| Full 1.3B | 5.2GB | 6GB | High |
| Full 3.3B | 13GB | 12GB | Best |

### Adding Models
1. Go to **Models** page
2. Click **Add Model**
3. Choose from popular NLLB models or search HuggingFace
4. Model downloads in background

## Supported Languages

NLLB-200 supports 200+ languages including:
- All major world languages
- Regional languages (Catalan, Welsh, etc.)
- Low-resource languages (Yoruba, Swahili, etc.)
- Multiple scripts (Latin, Cyrillic, Arabic, etc.)

## Tips

- Shorter text translates faster
- Context helps accuracy
- Formal/informal may vary by language
- Review translations for critical use

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No model available | Add model in Models page |
| Slow translation | Try smaller model variant |
| Poor quality | Try larger model |
| Language not detected | Specify source language |
