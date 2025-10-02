#!/bin/bash

echo "🚀 Avvio Whisper Transcription Ultra..."
echo ""

# Attiva ambiente virtuale
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Ambiente virtuale non trovato. Esegui prima: ./setup.sh"
    exit 1
fi

# Verifica whisper.cpp
if [ ! -f "whisper.cpp/build/bin/whisper-cli" ]; then
    echo "⚠️  Whisper.cpp non compilato. Esegui prima: ./setup.sh"
    exit 1
fi

# Avvia Streamlit
echo "✅ Avvio app su http://localhost:8501"
echo ""
streamlit run app.py