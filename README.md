# 🎬 Video Cutter App

## 1. Objetivo
Aplicação para recorte de vídeos curtos (15–30s) para uso em apresentações.

## 2. Tecnologias
- Python
- FFmpeg
- customtkinter

## 3. Estrutura

- ui → interface gráfica
- services → regras de negócio
- infra → execução do FFmpeg
- utils → utilidades

## 4. Como executar

1. Instalar FFmpeg
2. Rodar:

python main.py

## 5. Observações

- O modo "copy" é mais rápido, mas pode falhar em alguns vídeos.
- O modo "reencode" é mais compatível.

## 6. Próximos passos

- Normalização de vídeos
- Suporte a múltiplos formatos
- Integração com calendário


## 7.Diferenças importantes no FFmpeg

### -ss antes vs depois do input

- Antes do input → mais rápido, menos preciso
- Depois do input → mais preciso, mais lento

### copy vs reencode

- copy → rápido, pode falhar em cortes exatos
- reencode → mais lento, mais compatível

### -map 0

Inclui todas as trilhas do vídeo (áudio, legenda, etc.)

## 8.Tratamento de tempo

O sistema aceita:

- HH:MM:SS
- HH:MM:SS.ms
- HH:MM:SS,ms

O tempo é convertido internamente para segundos (float), permitindo:

- Comparações precisas
- Validação de intervalo
- Futuras operações (ex: múltiplos cortes)

## 9.Validação de entrada

O sistema valida:

- Formato do tempo (HH:MM:SS)
- Valores válidos (minutos e segundos)
- Ordem lógica (tempo final maior que inicial)

Essa validação evita erros no processamento com FFmpeg.

## 10.Tratamento de streams

- Uso de -map 0:v:0 para vídeo
- Uso de -map 0:a:0? para áudio opcional
- Evita erro em vídeos sem faixa de áudio

## 11.Ajustes no comando FFmpeg

- Uso de -map 0:v:0 e -map 0:a:0 para evitar streams incompatíveis
- Uso de -y para evitar bloqueio ao sobrescrever arquivos
- Remoção de -hwaccel por questões de compatibilidade

## 12.Versionamento

O projeto utiliza Git com versionamento semântico.

Versões:

- v1.0: corte funcional com FFmpeg
- próximas versões incluirão normalização e integração

## 13.Normalização de vídeo

Foi implementado um processo de normalização que converte qualquer vídeo para:

- MP4
- H264 (vídeo)
- AAC (áudio)

Isso garante compatibilidade com o sistema de corte e com o PowerPoint.

## 14.Normalização inteligente

- Evita reprocessamento de vídeos já normalizados
- Mantém padrão MP4 (H264 + AAC)
- Aplica otimizações de reprodução (faststart)
- Normaliza áudio automaticamente (loudnorm)

## 15.Pipeline de processamento

O sistema gera dois arquivos:

1. Vídeo normalizado (completo)
2. Vídeo recortado

Isso permite reutilização do vídeo normalizado para múltiplos cortes,
evitando reprocessamento.

- Arquivos normalizados são armazenados em `videos/normalized/`
- O sistema evita reprocessamento de vídeos já normalizados

## 16.Modos de operação

O sistema possui dois modos:

- Modo rápido: realiza apenas o corte direto
- Modo compatível: normaliza o vídeo antes do corte

O modo compatível é recomendado para vídeos com problemas de codec ou origem diversa.

## Versão 1.2

- Implementação de modos de operação:
  - Modo rápido (corte direto)
  - Modo compatível (normalização + corte)
- Organização dos arquivos de saída em `videos/cuts`
- Melhor controle de desempenho pelo usuário