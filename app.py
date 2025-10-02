import streamlit as st
import yt_dlp
import subprocess
import os
import time
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

st.set_page_config(page_title="Trascrizione Whisper Ultra", layout="wide")

# Aumenta limite upload
try:
    from streamlit.web.server import server
    server.MAX_UPLOAD_SIZE_MB = 2000
except:
    pass

def check_and_install_whisper_cpp():
    """Verifica e installa whisper.cpp se necessario"""
    whisper_dir = "whisper.cpp"
    whisper_binary = os.path.join(whisper_dir, "build", "bin", "whisper-cli")
    
    if os.path.exists(whisper_binary):
        return True
    
    st.warning("Whisper.cpp non trovato. Installazione automatica in corso...")
    
    if not os.path.exists(whisper_dir):
        st.info("Clonazione whisper.cpp...")
        result = subprocess.run(
            ["git", "clone", "https://github.com/ggerganov/whisper.cpp.git"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            st.error(f"Errore nel clonare whisper.cpp: {result.stderr}")
            return False
    
    st.info("Compilazione whisper.cpp con CoreML (3-5 minuti)...")
    # Compila con CoreML per Apple Silicon
    result = subprocess.run(
        ["make", "WHISPER_COREML=1"], 
        cwd=whisper_dir, 
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        st.error("Errore nella compilazione")
        st.code(result.stderr)
        return False
    
    if os.path.exists(whisper_binary):
        st.success("✅ Whisper.cpp installato con accelerazione GPU!")
        return True
    
    return False

def download_model_if_missing(model="tiny"):
    """Scarica automaticamente il modello Whisper se non esiste"""
    model_dir = "whisper.cpp/models"
    model_path = f"{model_dir}/ggml-{model}.bin"
    
    if os.path.exists(model_path):
        return True
    
    os.makedirs(model_dir, exist_ok=True)
    
    st.warning(f"Modello {model} non trovato. Download automatico in corso...")
    
    url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{model}.bin"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def reporthook(block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            percent = min(int(downloaded / total_size * 100), 100)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            progress_bar.progress(percent)
            status_text.text(f"Scaricamento: {percent}% ({downloaded_mb:.1f} MB / {total_mb:.1f} MB)")
    
    try:
        urllib.request.urlretrieve(url, model_path, reporthook)
        status_text.empty()
        progress_bar.empty()
        st.success(f"Modello {model} scaricato!")
        time.sleep(1)
        st.rerun()
        return True
    except Exception as e:
        st.error(f"Errore download: {e}")
        return False

# Setup iniziale
if not check_and_install_whisper_cpp():
    st.error("Impossibile installare whisper.cpp. Verifica i prerequisiti.")
    st.stop()

if not os.path.exists("whisper.cpp/models/ggml-base.bin"):
    download_model_if_missing("base")
    st.stop()

st.title("🚀 Trascrizione Ultra-Veloce (GPU + Parallel)")

# Badge informativo
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("🔥 Accelerazione", "CoreML GPU")
with col_info2:
    st.metric("⚡ Processing", "Parallelo")
with col_info3:
    cpu_count = multiprocessing.cpu_count()
    st.metric("🖥️ CPU Cores", f"{cpu_count}")

operation = st.selectbox("Scegli un'operazione:", ["Trascrivi Audio", "Scarica Video"])

if operation == "Scarica Video":
    video_url = st.text_input("URL video YouTube:")
    save_path = st.text_input("Cartella destinazione:", os.path.expanduser("~/Videos"))

if operation == "Trascrivi Audio":
    source_type = st.radio("Fonte:", ["YouTube (URL)", "Carica file", "File locale"])
    
    if source_type == "YouTube (URL)":
        video_url = st.text_input("URL video YouTube:")
    
    elif source_type == "Carica file":
        st.info("💡 **Per file > 200MB**: usa l'opzione 'File locale'")
        
        uploaded_file = st.file_uploader(
            "Carica video/audio",
            type=["mp4", "mkv", "avi", "mov", "m4a", "mp3", "wav"]
        )
        
        if uploaded_file:
            st.session_state['uploaded_file'] = uploaded_file
            size_mb = uploaded_file.size / (1024 * 1024)
            st.write(f"✅ File: {uploaded_file.name} ({size_mb:.1f} MB)")
    
    else:  # File locale
        st.info("💡 **Consigliato per file grandi**")
        
        local_file_path = st.text_input(
            "Percorso completo del file:",
            placeholder="/Users/tuonome/Downloads/video.mp4"
        )
        
        if local_file_path and os.path.exists(local_file_path):
            size_mb = os.path.getsize(local_file_path) / (1024 * 1024)
            st.success(f"✅ File: {os.path.basename(local_file_path)} ({size_mb:.1f} MB)")
            st.session_state['local_file_path'] = local_file_path
        elif local_file_path:
            st.error("❌ File non trovato")
    
    st.subheader("⚙️ Impostazioni Avanzate")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        model_name = st.selectbox(
            "Modello:",
            ["base", "small", "tiny"],
            index=0,
            help="Base: ottimo compromesso velocità/qualità"
        )
        
        model_info = {
            "tiny": "⚡ Ultra-veloce (75MB) - 90% precisione",
            "base": "🎯 Raccomandato (142MB) - 95% precisione", 
            "small": "🔬 Massima qualità (466MB) - 98% precisione"
        }
        st.caption(model_info[model_name])
    
    with col2:
        language = st.selectbox("Lingua:", ["auto", "it", "en"])
    
    with col3:
        chunk_duration = st.selectbox(
            "Durata chunk:",
            [15, 20, 30, 45],
            index=2,
            help="Chunk più piccoli = più parallelo = più veloce"
        )
        st.caption(f"Audio diviso in segmenti da {chunk_duration}min")
    
    # Parallelizzazione
    max_workers = st.slider(
        "🔀 Worker paralleli:",
        min_value=1,
        max_value=min(cpu_count, 6),
        value=min(cpu_count - 1, 4),
        help=f"Max consigliato: {min(cpu_count - 1, 4)} (lascia 1 core libero)"
    )
    st.caption(f"⚡ Processa fino a {max_workers} chunk contemporaneamente")

def download_video(video_url, save_path):
    st.info("📥 Scaricamento...")
    os.makedirs(save_path, exist_ok=True)
    
    ydl_opts = {
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        downloaded_file = ydl.prepare_filename(info)
    
    st.success(f"✅ Salvato in: {save_path}")
    return downloaded_file

def save_uploaded_file(uploaded_file):
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    
    return file_path

def get_audio_duration(audio_path):
    """Ottieni durata audio in secondi"""
    command = [
        'ffprobe', '-i', audio_path,
        '-show_entries', 'format=duration',
        '-v', 'quiet',
        '-of', 'csv=p=0'
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0

def split_audio_chunks(audio_path, chunk_duration_minutes=30):
    """Divide audio in chunk usando ffmpeg"""
    st.info(f"📂 Divisione in segmenti da {chunk_duration_minutes} minuti...")
    
    duration = get_audio_duration(audio_path)
    if duration == 0:
        st.warning("Impossibile determinare durata, uso file intero")
        return [audio_path]
    
    duration_minutes = duration / 60
    
    if duration_minutes <= chunk_duration_minutes:
        st.info("✅ Audio breve, nessuna divisione necessaria")
        return [audio_path]
    
    chunk_duration_sec = chunk_duration_minutes * 60
    num_chunks = int(duration / chunk_duration_sec) + 1
    
    st.write(f"🔪 Creazione di {num_chunks} segmenti...")
    
    chunks = []
    os.makedirs("chunks", exist_ok=True)
    
    progress_bar = st.progress(0)
    
    for i in range(num_chunks):
        start_time = i * chunk_duration_sec
        chunk_path = f"chunks/chunk_{i:03d}.wav"
        
        command = [
            'ffmpeg', '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(chunk_duration_sec),
            '-ar', '16000', '-ac', '1',
            '-c:a', 'pcm_s16le',
            chunk_path, '-y'
        ]
        
        # FIX: rimosso capture_output
        result = subprocess.run(
            command, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        if result.returncode == 0 and os.path.exists(chunk_path):
            chunks.append(chunk_path)
        
        progress_bar.progress((i + 1) / num_chunks)
    
    progress_bar.empty()
    st.success(f"✅ {len(chunks)} segmenti pronti")
    
    return chunks

def convert_audio(video_path, output_path="audio.wav"):
    """Estrae audio ottimizzato per Whisper"""
    st.info("🎵 Estrazione audio...")
    
    command = [
        'ffmpeg', '-i', video_path,
        '-ar', '16000',  # 16kHz
        '-ac', '1',      # Mono
        '-c:a', 'pcm_s16le',
        output_path, '-y'
    ]
    
    # FIX: usa stdout e stderr invece di capture_output
    result = subprocess.run(
        command, 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if result.returncode == 0:
        return output_path
    return None

def transcribe_chunk(args):
    """Trascrivi un singolo chunk - ottimizzato per parallelizzazione"""
    chunk_path, language, model, chunk_number, total_chunks = args
    
    model_path = f"whisper.cpp/models/ggml-{model}.bin"
    
    # Comando ottimizzato con CoreML
    command = [
        './whisper.cpp/build/bin/whisper-cli',
        '-m', model_path,
        '-f', chunk_path,
        '--output-txt',
        '--language', language,
        '-t', '2',  # 2 thread per chunk (per non sovraccaricare)
        '-p', '1'
    ]
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True,
            timeout=600  # Timeout 10 min per chunk
        )
        
        transcript_file = f"{chunk_path}.txt"
        
        if os.path.exists(transcript_file):
            with open(transcript_file, "r") as f:
                text = f.read()
            
            # Pulizia immediata
            try:
                os.remove(transcript_file)
            except:
                pass
            
            return (chunk_number, text, True)
        else:
            return (chunk_number, f"[Errore chunk {chunk_number}]", False)
    
    except subprocess.TimeoutExpired:
        return (chunk_number, f"[Timeout chunk {chunk_number}]", False)
    except Exception as e:
        return (chunk_number, f"[Errore {chunk_number}: {str(e)}]", False)

def transcribe_parallel(chunks, language, model, max_workers=4):
    """Trascrizione parallela con progress bar"""
    
    if len(chunks) == 1:
        # Audio breve, trascrivi direttamente
        st.info("🎙️ Trascrizione in corso...")
        result = transcribe_chunk((chunks[0], language, model, 0, 1))
        return result[1] if result[2] else None
    
    st.info(f"🚀 Trascrizione parallela con {max_workers} worker...")
    
    # Prepara argomenti per ogni chunk
    chunk_args = [
        (chunk, language, model, i, len(chunks)) 
        for i, chunk in enumerate(chunks)
    ]
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = {}
    completed = 0
    
    # Esegui in parallelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(transcribe_chunk, arg): arg for arg in chunk_args}
        
        for future in as_completed(futures):
            chunk_number, text, success = future.result()
            results[chunk_number] = text
            
            completed += 1
            progress = completed / len(chunks)
            progress_bar.progress(progress)
            status_text.text(f"✅ Completati: {completed}/{len(chunks)} segmenti ({progress*100:.0f}%)")
            
            if not success:
                st.warning(f"⚠️ Problema con segmento {chunk_number}")
    
    progress_bar.empty()
    status_text.empty()
    
    # Riordina e concatena risultati
    sorted_results = [results[i] for i in sorted(results.keys())]
    full_text = "\n\n".join(sorted_results)
    
    return full_text

def cleanup_chunks():
    """Pulisci directory chunks"""
    try:
        if os.path.exists("chunks"):
            for file in os.listdir("chunks"):
                try:
                    os.remove(os.path.join("chunks", file))
                except:
                    pass
            shutil.rmtree("chunks")
    except:
        pass

if st.button("▶️ AVVIA TRASCRIZIONE ULTRA-VELOCE", type="primary", use_container_width=True):
    start_time = time.time()
    video_path = None
    video_name = "video"
    
    if operation == "Scarica Video":
        if video_url:
            download_video(video_url, save_path)
    
    elif operation == "Trascrivi Audio":
        # Ottieni file video
        if source_type == "YouTube (URL)" and video_url:
            os.makedirs("temp", exist_ok=True)
            video_path = download_video(video_url, "temp")
            video_name = os.path.splitext(os.path.basename(video_path))[0]
        
        elif source_type == "Carica file" and 'uploaded_file' in st.session_state:
            uploaded = st.session_state['uploaded_file']
            video_path = save_uploaded_file(uploaded)
            video_name = os.path.splitext(uploaded.name)[0]
        
        elif source_type == "File locale" and 'local_file_path' in st.session_state:
            local_path = st.session_state['local_file_path']
            video_name = os.path.splitext(os.path.basename(local_path))[0]
            video_path = local_path
        
        if video_path and os.path.exists(video_path):
            # Estrai audio
            audio_path = convert_audio(video_path)
            
            if audio_path:
                # Mostra info durata
                duration = get_audio_duration(audio_path)
                if duration > 0:
                    st.info(f"⏱️ Durata audio: {duration/60:.1f} minuti")
                
                # Dividi in chunk
                chunks = split_audio_chunks(audio_path, chunk_duration)
                
                # Trascrizione parallela
                text = transcribe_parallel(chunks, language, model_name, max_workers)
                
                # Pulizia chunk
                cleanup_chunks()
                
                if text:
                    elapsed = time.time() - start_time
                    
                    # Calcola velocità
                    if duration > 0:
                        speed_factor = duration / elapsed
                        st.success(f"🎉 COMPLETATO in {elapsed/60:.1f} minuti (velocità: {speed_factor:.1f}x)")
                    else:
                        st.success(f"🎉 COMPLETATO in {elapsed/60:.1f} minuti")
                    
                    # Salva trascrizione
                    os.makedirs("trascrizioni", exist_ok=True)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    final_path = f"trascrizioni/{video_name}_{timestamp}.txt"
                    
                    with open(final_path, "w") as f:
                        f.write(text)
                    
                    # Mostra risultati
                    st.subheader("📝 Trascrizione")
                    
                    # Statistiche
                    word_count = len(text.split())
                    char_count = len(text)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Parole", f"{word_count:,}")
                    with col2:
                        st.metric("📊 Caratteri", f"{char_count:,}")
                    with col3:
                        if duration > 0:
                            st.metric("⚡ Velocità", f"{speed_factor:.1f}x")
                    
                    st.text_area("", text, height=400)
                    st.info(f"💾 Salvato: {final_path}")
                    
                    st.download_button(
                        "📥 SCARICA TRASCRIZIONE",
                        text,
                        file_name=os.path.basename(final_path),
                        use_container_width=True
                    )
                else:
                    st.error("❌ Errore durante la trascrizione")
                
                # Pulizia file temporanei
                if os.path.exists(video_path) and "temp" in video_path:
                    try:
                        os.remove(video_path)
                    except:
                        pass
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except:
                        pass
            else:
                st.error("❌ Errore nell'estrazione audio")
        else:
            st.error("❌ Nessun file valido trovato")

# Footer informativo
st.markdown("---")
st.caption("🚀 Powered by Whisper.cpp + CoreML + Parallel Processing | Ottimizzato per Apple Silicon")