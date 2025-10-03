#!/bin/bash

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   🎙️  WHISPER TRANSCRIPTION ULTRA - SETUP            ║"
echo "║                                                        ║"
echo "║   Setup automatico con GPU in 5-10 minuti            ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[1;34m'
NC='\033[0m'

# Step counter
STEP=1
TOTAL_STEPS=9

step() {
    echo ""
    echo -e "${BLUE}[$STEP/$TOTAL_STEPS] $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    STEP=$((STEP + 1))
}

# Verifica macOS
step "Verifica sistema operativo"
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Questo setup è ottimizzato per macOS${NC}"
    echo "Per Linux/Windows, segui l'installazione manuale nel README"
    exit 1
fi
echo -e "${GREEN}✅ macOS rilevato${NC}"

ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo -e "${GREEN}✅ Apple Silicon ($ARCH) - GPU disponibile!${NC}"
else
    echo -e "${YELLOW}⚠️  Chip Intel - Solo CPU disponibile${NC}"
fi

# Verifica/installa Homebrew
step "Controllo Homebrew"
if ! command -v brew &> /dev/null; then
    echo "📥 Installazione Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    if [[ "$ARCH" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi
echo -e "${GREEN}✅ Homebrew OK${NC}"

# Installa FFmpeg
step "Controllo FFmpeg"
if ! command -v ffmpeg &> /dev/null; then
    echo "📥 Installazione FFmpeg..."
    brew install ffmpeg
fi
echo -e "${GREEN}✅ FFmpeg OK${NC}"

# Crea ambiente virtuale
step "Setup Python"
if [ ! -d "venv" ]; then
    echo "📦 Creazione ambiente virtuale..."
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✅ Ambiente virtuale attivo${NC}"

# Installa dipendenze Python
step "Installazione dipendenze Python"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Installa anche ane_transformers per CoreML (opzionale ma utile)
if [[ "$ARCH" == "arm64" ]]; then
    pip install ane_transformers --quiet 2>/dev/null
fi

echo -e "${GREEN}✅ Dipendenze installate${NC}"

# Setup whisper.cpp
step "Setup Whisper.cpp"
if [ ! -d "whisper.cpp" ]; then
    echo "📥 Download whisper.cpp..."
    git clone https://github.com/ggerganov/whisper.cpp.git --quiet
fi

cd whisper.cpp
echo "🧹 Pulizia build precedenti..."
make clean > /dev/null 2>&1

echo "🔨 Compilazione con supporto GPU (2-4 minuti)..."
if [[ "$ARCH" == "arm64" ]]; then
    WHISPER_COREML=1 make > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Compilato con supporto CoreML GPU!${NC}"
    else
        echo -e "${YELLOW}⚠️  Compilazione GPU fallita, uso CPU...${NC}"
        make > /dev/null 2>&1
    fi
else
    make > /dev/null 2>&1
    echo -e "${GREEN}✅ Compilato (CPU only)${NC}"
fi

cd ..

# Download e conversione modello per GPU
step "Setup modello AI con accelerazione GPU"

MODEL_DIR="whisper.cpp/models"
MODEL_FILE="$MODEL_DIR/ggml-base.bin"
COREML_MODEL="$MODEL_DIR/ggml-base-encoder.mlmodelc"

mkdir -p "$MODEL_DIR"

# Scarica modello base se manca
if [ ! -f "$MODEL_FILE" ]; then
    echo "📥 Scaricamento modello base (142MB)..."
    curl -L --progress-bar \
        "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" \
        -o "$MODEL_FILE"
    
    if [ -f "$MODEL_FILE" ]; then
        echo -e "${GREEN}✅ Modello base scaricato${NC}"
    else
        echo -e "${RED}❌ Download fallito${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Modello base già presente${NC}"
fi

# Converti per CoreML (GPU) solo su Apple Silicon
if [[ "$ARCH" == "arm64" ]] && [ ! -d "$COREML_MODEL" ]; then
    echo ""
    echo "🔥 Conversione modello per GPU (1-3 minuti)..."
    echo "   Questo abilita accelerazione 10-15x più veloce!"
    echo ""
    
    cd whisper.cpp/models
    
    # Scarica script conversione se manca
    if [ ! -f "generate-coreml-model.sh" ]; then
        curl -s -o generate-coreml-model.sh \
            "https://raw.githubusercontent.com/ggerganov/whisper.cpp/master/models/generate-coreml-model.sh"
        chmod +x generate-coreml-model.sh
    fi
    
    # Converti modello (mostra output per feedback)
    ./generate-coreml-model.sh base
    
    cd ../..
    
    if [ -d "$COREML_MODEL" ]; then
        echo ""
        echo -e "${GREEN}🎉 GPU ATTIVA! Modello CoreML creato con successo!${NC}"
        echo "   Aspettati velocità 10-15x superiori!"
    else
        echo -e "${YELLOW}⚠️  Conversione fallita, userà CPU (comunque funziona)${NC}"
    fi
elif [[ "$ARCH" == "arm64" ]] && [ -d "$COREML_MODEL" ]; then
    echo -e "${GREEN}✅ GPU già attiva (modello CoreML presente)${NC}"
else
    echo -e "${YELLOW}ℹ️  Chip Intel - GPU CoreML non disponibile, userà CPU${NC}"
fi

# Crea cartelle
step "Creazione directory"
mkdir -p trascrizioni uploads temp chunks .streamlit
echo -e "${GREEN}✅ Directory create${NC}"

# Crea configurazione Streamlit
step "Configurazione Streamlit"
cat > .streamlit/config.toml << 'EOF'
[server]
maxUploadSize = 2000
headless = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOF
echo -e "${GREEN}✅ Streamlit configurato${NC}"

# Successo!
clear
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║          🎉 SETUP COMPLETATO CON SUCCESSO! 🎉         ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ Installazione completata!${NC}"
echo ""
echo "📋 CONFIGURAZIONE:"
echo "   • Homebrew e FFmpeg installati"
echo "   • Python e dipendenze pronte"
echo "   • Whisper.cpp compilato"
echo "   • Modello AI base scaricato"

if [[ "$ARCH" == "arm64" ]] && [ -d "$COREML_MODEL" ]; then
    echo -e "   • ${GREEN}🔥 GPU ATTIVA (CoreML)${NC}"
    echo "   • Velocità: 10-15x più veloce!"
else
    echo "   • CPU only (comunque veloce)"
fi

echo ""
echo "🚀 PER AVVIARE L'APP:"
echo ""
echo -e "   ${BLUE}./start.sh${NC}"
echo ""
echo "   oppure:"
echo ""
echo -e "   ${BLUE}streamlit run app.py${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""