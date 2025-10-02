# 🤝 Come Contribuire

Grazie per l'interesse nel contribuire a Whisper Transcription Ultra! 

## 🐛 Segnalare Bug

1. Verifica che il bug non sia già stato segnalato nelle [Issues](../../issues)
2. Apri una nuova issue includendo:
   - ✏️ Descrizione chiara e concisa
   - 🔄 Passi per riprodurre il problema
   - ✅ Comportamento atteso
   - ❌ Comportamento attuale
   - 📸 Screenshot (se applicabile)
   - 💻 Sistema operativo e versione Python
   - 📋 Eventuali messaggi di errore

## ✨ Proporre Nuove Feature

1. Apri una issue con label "enhancement"
2. Descrivi dettagliatamente la feature proposta
3. Spiega perché sarebbe utile agli utenti
4. Attendi feedback della community prima di iniziare l'implementazione

## 🔧 Inviare Pull Request

### Setup Sviluppo
```bash
# Fork e clona il repository
git clone https://github.com/tuousername/whisper-transcription-app.git
cd whisper-transcription-app

# Crea branch per la tua feature
git checkout -b feature/nome-feature

# Installa dipendenze sviluppo
pip install -r requirements.txt
pip install black flake8 pytest