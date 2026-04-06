# 🎬 Video Cutter Pro + OBS

Aplicativo desktop em Python para corte de vídeos com múltiplos trechos, integração com OBS Studio e preview rápido via FFmpeg.

---

## 🚀 Funcionalidades

### ✂️ Corte de Vídeo

* Múltiplos cortes por arquivo
* Execução rápida via FFmpeg (copy ou reencode)
* Nomes únicos de saída (sem sobrescrita)
* Barra de progresso com feedback

### 🎥 Integração com OBS

* Iniciar/parar gravação diretamente pelo app
* Importação automática do vídeo gravado
* Compatível com OBS WebSocket (porta 4455)

### 🎬 Preview de Vídeo

* Preview rápido usando **ffplay**
* Compatível com qualquer formato suportado pelo FFmpeg
* Não trava a interface

### 📋 Gerenciamento de Cortes

* Fila de cortes por sessão
* Limpeza automática após execução
* Interface clara e organizada

### 📜 Histórico

* Histórico persistente em JSON
* Exibição dos últimos cortes realizados
* Não interfere na execução atual

---

## 🧠 Arquitetura

```text
ui/
 └── main_window.py

services/
 ├── video_cutter.py
 ├── video_normalizer.py
 └── obs_controller.py

ffmpeg/
 ├── ffmpeg.exe
 └── ffplay.exe
```

---

## ⚙️ Requisitos

* Python 3.10+
* FFmpeg (incluso no projeto)
* OBS Studio com WebSocket habilitado

---

## ▶️ Execução (Desenvolvimento)

```bash
python main.py
```

---

## 📦 Executável (.exe)

Gerado com PyInstaller.

* FFmpeg embutido
* Logs em AppData
* Funciona offline

---

## 🛠️ Tecnologias

* Python
* CustomTkinter
* FFmpeg / ffplay
* OBS WebSocket

---

## 📌 Versão Atual

**v1.7**

✔ Preview com ffplay
✔ Integração OBS estável
✔ Histórico persistente
✔ UI refinada
✔ Execução robusta com threading

---

## 🔜 Próximos Passos

* Preview com tempo inicial (start)
* Preview de trecho (start → end)
* Validação de formato de tempo (HH:MM:SS)
* Exportação avançada

---

## 📄 Licença

Uso pessoal / estudo
