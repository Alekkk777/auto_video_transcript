# 🎙️ Whisper Transcription Ultra

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

**Trascrizione audio/video ultra-veloce con AI**

Powered by OpenAI Whisper • Ottimizzato per Apple Silicon

[Installazione](#-installazione-rapida) • [Documentazione](#-documentazione) • [Demo](#-performance)

</div>

---

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Performance](#-performance)
- [Requisiti](#️-requisiti)
- [Installazione Rapida](#-installazione-rapida)
- [Guida Rapida](#-guida-rapida)
- [Configurazione Avanzata](#️-configurazione-avanzata)
- [Documentazione](#-documentazione)
- [Troubleshooting](#-troubleshooting)
- [Contribuire](#-contribuire)
- [Roadmap](#-roadmap)
- [Licenza](#-licenza)

---

## ✨ Caratteristiche

- **🚀 Ultra-veloce** - Fino a 15x più veloce con accelerazione GPU CoreML
- **🎯 Alta precisione** - 90-98% di accuratezza grazie a OpenAI Whisper
- **📂 Multi-sorgente** - Supporta YouTube, file locali e upload diretto
- **⚡ Processing parallelo** - Divide automaticamente audio lunghi in chunk
- **🌍 Multi-lingua** - Supporta italiano, inglese, auto-detect e 50+ lingue
- **💾 Export facile** - Scarica trascrizioni in formato TXT
- **🎨 UI moderna** - Interfaccia web intuitiva e responsive
- **🔧 Zero configurazione** - Setup automatico in 5 minuti

---

## 📊 Performance

Tempi di trascrizione testati su **MacBook Pro M2** con modello Base:

| Durata Audio | Solo CPU | Con GPU (CoreML) | Speedup |
|:------------:|:--------:|:----------------:|:-------:|
| 30 minuti | ~45 min | ~3-4 min | **12x** |
| 2 ore | ~3 ore | ~10-12 min | **15x** |
| 4 ore | ~6 ore | ~20-25 min | **14x** |

> **Nota**: I tempi variano in base a modello AI, qualità audio e configurazione hardware.

---

## 🖥️ Requisiti

### Sistema Operativo
- **macOS** 11 Big Sur o superiore (consigliato Apple Silicon M1/M2/M3)
- Linux e Windows supportati con limitazioni

### Software
- Python 3.8 o superiore
- FFmpeg
- Git
- 4GB RAM minimo (8GB+ consigliato)
- 500MB spazio disco per modelli AI

---

## ⚡ Installazione Rapida

### Installazione Automatica (5 minuti)
```bash
# 1. Clona il repository
git clone https://github.com/tuousername/whisper-transcription-app.git
cd whisper-transcription-app

# 2. Esegui setup automatico
chmod +x setup.sh
./setup.sh

# 3. Avvia l'app
./start.sh