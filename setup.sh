#!/bin/bash

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   🎙️  WHISPER TRANSCRIPTION ULTRA - SETUP            ║"
echo "║                                                        ║"
echo "║   Setup automatico in 5 minuti                        ║"
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
TOTAL_STEPS=8

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
    echo -e "${GREEN}✅ Apple Silicon ($ARCH) - Perfetto per GPU!${NC}"
else
    echo -e "${YELLOW}⚠️  Chip Intel - GPU non disponibile ma funzionerà${NC}"
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

echo "🔨 Compilazione con GPU (2-4 minuti)..."
if [[ "$ARCH" == "arm64" ]]; then
    WHISPER_COREML=1 make > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Compilato con accelerazione GPU!${NC}"
    else
        echo -e "${YELLOW}⚠️  GPU fallita, compilo versione CPU...${NC}"
        make > /dev/null 2>&1
    fi
else
    make > /dev/null 2>&1
    echo -e "${GREEN}✅ Compilato (CPU only)${NC}"
fi

cd ..

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
echo -e "${GREEN}✅ Tutto pronto!${NC}"
echo ""
echo "📋 COSA È STATO CONFIGURATO:"
echo "   • Homebrew e FFmpeg"
echo "   • Python e dipendenze"
echo "   • Whisper.cpp con GPU (se disponibile)"
echo "   • Directory e configurazioni"
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