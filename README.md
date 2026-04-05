# 🎬 Video Cutter Pro

## 🚀 Objetivo
Aplicação desktop para recorte de vídeos curtos (15–30s), ideal para uso em apresentações (ex: PowerPoint), com foco em simplicidade, velocidade e compatibilidade.

---

## ✨ Funcionalidades
*   **Corte de Vídeo:** Suporte a múltiplos intervalos por vídeo.
*   **Modos de Operação:** 
    *   *Modo Rápido (Stream Copy):* Sem perda de qualidade e instantâneo.
    *   *Modo Compatível (Reencode):* Garante execução em qualquer player/PowerPoint.
*   **Normalização Inteligente:** Conversão para MP4 (H264/AAC), ajuste de áudio (`loudnorm`) e uso de `faststart`.
*   **Performance:** Execução assíncrona (Threading) para manter a interface fluida.
*   **Interface Moderna:** Construída com `CustomTkinter`.
*   **Gestão de Arquivos:** Geração automática de saídas e sistema de logs robusto (AppData).

---

## 📂 Estrutura do Projeto
```text
video_cutter_app/
├── ui/          # Interface gráfica (CustomTkinter)
├── services/    # Regras de negócio e orquestração
├── infra/       # Execução de comandos (FFmpeg)
├── utils/       # Funções auxiliares (tempo, etc)
├── logs/        # Registros de depuração (Ambiente Dev)
├── videos/      # Saídas de cortes e normalizados (Ignorado no Git)
├── main.py      # Entry point da aplicação
└── .gitignore   # Filtro de arquivos para Git


---

## 🖥️ Tecnologias

* Python 3.11+
* FFmpeg (Engine de processamento)
* CustomTkinter (Interface UI)

---
## ▶️ Como executar

1. Instalar FFmpeg
2. Rodar:

```bash
python main.py
```

---

## 🎯 Como usar

1. Selecionar o vídeo
2. Definir tempo inicial e final
3. Adicionar cortes
4. Executar cortes

---

## ⚠️ Observações

* O modo "copy" é mais rápido, mas pode falhar em alguns vídeos
* O modo "reencode" é mais compatível

---

# 🧠 Documentação Técnica

## Diferenças importantes no FFmpeg

### -ss antes vs depois do input

* Antes do input → mais rápido, menos preciso
* Depois do input → mais preciso, mais lento

### copy vs reencode

* copy → rápido, pode falhar em cortes exatos
* reencode → mais lento, mais compatível

### -map 0

Inclui todas as trilhas do vídeo (áudio, legenda, etc.)

---

## Tratamento de tempo

O sistema aceita:

* HH:MM:SS
* HH:MM:SS.ms
* HH:MM:SS,ms

O tempo é convertido internamente para segundos (float), permitindo:

* Comparações precisas
* Validação de intervalo
* Futuras operações (ex: múltiplos cortes)

---

## Validação de entrada

O sistema valida:

* Formato do tempo
* Valores válidos
* Ordem lógica (tempo final maior que inicial)

---

## Tratamento de streams

* Uso de -map 0:v:0 para vídeo
* Uso de -map 0:a:0? para áudio opcional
* Evita erro em vídeos sem faixa de áudio

---

## Ajustes no comando FFmpeg

* Uso de -map 0:v:0 e -map 0:a:0
* Uso de -y para sobrescrita automática
* Remoção de -hwaccel por compatibilidade

---

## Normalização de vídeo

* Conversão para MP4 (H264 + AAC)
* Compatibilidade com PowerPoint
* Uso de `loudnorm` para áudio

---

## Normalização inteligente

* Evita reprocessamento
* Mantém padrão MP4
* Usa `faststart`
* Normaliza áudio automaticamente

---

## Pipeline de processamento

O sistema gera:

1. Vídeo normalizado
2. Vídeo recortado

Vantagens:

* Reutilização do vídeo
* Melhor desempenho

Arquivos:

* `videos/normalized/`
* `videos/cuts/`

---

## Modos de operação

* Modo rápido → corte direto
* Modo compatível → normalização + corte

---

## Execução assíncrona

Processamento em thread separada:

* Interface não trava
* Melhor experiência do usuário

---
## Logs da Aplicação

Os logs são armazenados em:

Windows:
%APPDATA%/VideoCutter/logs/app.log
## Versionamento

O projeto utiliza Git com versionamento semântico.

### Versões

* v1.0 → corte básico
* v1.2 → modos de operação
* v1.4 → múltiplos cortes + melhorias de UX

---

## Próximos passos

* Exportação inteligente (nome baseado no tempo)
* Embutir FFmpeg
* Barra de progresso real
* Integração com calendário

---

## 📌 Observação final

Este projeto foi desenvolvido com foco em aprendizado prático e aplicação real, abordando conceitos de:

* Arquitetura em camadas
* Integração com ferramentas externas
* UX em aplicações desktop
* Processamento assíncrono
