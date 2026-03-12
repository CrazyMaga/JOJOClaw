<!-- 语言切换 / Language Switch / Cambio de Idioma -->
<script>
function showLang(lang) {
  document.querySelectorAll('.lang-section').forEach(el => el.style.display = 'none');
  document.getElementById(lang).style.display = 'block';
  document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelector('[onclick="showLang(\'' + lang + '\')"]').classList.add('active');
}
</script>

<style>
.lang-btn { padding: 5px 10px; margin: 2px; cursor: pointer; border: 1px solid #ddd; background: #f5f5f5; border-radius: 3px; }
.lang-btn.active { background: #007bff; color: white; border-color: #007bff; }
.lang-section { display: none; }
#zh { display: block; }
</style>

<div align="center">
  <button class="lang-btn active" onclick="showLang('zh')">🇨🇳 中文</button>
  <button class="lang-btn" onclick="showLang('en')">🇺🇸 English</button>
  <button class="lang-btn" onclick="showLang('es')">🇪🇸 Español</button>
</div>

---

<!-- 中文版 / Chinese / Chino -->
<div id="zh" class="lang-section">

# JOJOClaw 🦞

> 基于 OpenClaw 的个人 AI 助手，专注于股票量化分析

## 简介

这是一个运行在 OpenClaw 平台上的个人 AI 助手，主要用于 A股市场的量化分析和选股。

## 功能特性

### 📊 股票初筛

- 排除 ST/*ST 股票
- 排除当日涨跌停股票
- 筛选成交额活跃的股票
- 筛选波动幅度足够的股票

### ⭐ 量化评分

- 价格动线分析（均线多头排列）
- 资金流向追踪（主力资金净流入）
- 流动性保障评估
- 情绪与股性分析
- 风险控制评估

### 📈 每日报告

- 自动生成量化评分 TOP 20 股票
- 定时推送至 Telegram

## 定时任务

| 任务 | 时间 | 说明 |
|-----|------|-----|
| 股票初筛 | 每天 8:00 (周一至周五) | 运行初筛技能 |
| 量化评分 | 每天 8:30 (周一至周五) | 对初筛结果评分 |
| 每日报告 | 每天 9:30 (周一至周五) | 生成报告并推送 |

## 技术栈

- **平台**: [OpenClaw](https://github.com/openclaw/openclaw)
- **数据源**: [Tushare](https://tushare.pro/)
- **推送**: Telegram Bot

## 技能目录

```
skills/
├── quant-score/       # 量化评分技能
├── stock-filter/     # 股票初筛技能
├── daily_report/     # 每日报告技能
└── ...
```

## 使用方法

### 运行股票初筛

```bash
python skills/stock-filter/quant_score.py
```

### 运行量化评分

```bash
python skills/quant-score/score.py
```

### 运行每日报告

```bash
python skills/daily_report/report_sender.py
```

## 环境变量

```bash
export TUSHARE_TOKEN="your_token_here"
```

---

*由 AI 助手运行维护*

</div>

---

<!-- English / 英文 / Inglés -->
<div id="en" class="lang-section">

# JOJOClaw 🦞

> Personal AI assistant based on OpenClaw, focused on stock quantitative analysis

## Introduction

This is a personal AI assistant running on the OpenClaw platform, mainly used for quantitative analysis and stock selection in the A-share market.

## Features

### 📊 Stock Screening

- Exclude ST/*ST stocks
- Exclude limit-up/limit-down stocks
- Filter stocks with active trading volume
- Filter stocks with sufficient volatility

### ⭐ Quantitative Scoring

- Price trend analysis (moving average alignment)
- Capital flow tracking (net inflow of main funds)
- Liquidity assessment
- Sentiment and stock behavior analysis
- Risk control assessment

### 📈 Daily Report

- Auto-generate TOP 20 stocks by quantitative score
- Scheduled push to Telegram

## Scheduled Tasks

| Task | Time | Description |
|------|------|-------------|
| Stock Screening | 8:00 daily (Mon-Fri) | Run screening skill |
| Quant Scoring | 8:30 daily (Mon-Fri) | Score screening results |
| Daily Report | 9:30 daily (Mon-Fri) | Generate and push report |

## Tech Stack

- **Platform**: [OpenClaw](https://github.com/openclaw/openclaw)
- **Data Source**: [Tushare](https://tushare.pro/)
- **Push**: Telegram Bot

## Skills Directory

```
skills/
├── quant-score/       # Quantitative scoring skill
├── stock-filter/     # Stock screening skill
├── daily_report/      # Daily report skill
└── ...
```

## Usage

### Run Stock Screening

```bash
python skills/stock-filter/quant_score.py
```

### Run Quant Scoring

```bash
python skills/quant-score/score.py
```

### Run Daily Report

```bash
python skills/daily_report/report_sender.py
```

## Environment Variables

```bash
export TUSHARE_TOKEN="your_token_here"
```

---

*Maintained by AI assistant*

</div>

---

<!-- Español / 西班牙语 / Spanish -->
<div id="es" class="lang-section">

# JOJOClaw 🦞

> Asistente de IA personal basado en OpenClaw, enfocado en análisis cuantitativo de acciones

## Introducción

Este es un asistente de IA personal que se ejecuta en la plataforma OpenClaw, principalmente utilizado para análisis cuantitativo y selección de acciones en el mercado A-share.

## Funciones

### 📊 Filtrado de Acciones

- Excluir acciones ST/*ST
- Excluir acciones con límite de precio
- Filtrar acciones con volumen activo
- Filtrar acciones con volatilidad suficiente

### ⭐ Puntuación Cuantitativa

- Análisis de tendencia de precios (alineación de medias móviles)
- Seguimiento de flujo de capital (entrada neta de fondos principales)
- Evaluación de liquidez
- Análisis de sentimiento y comportamiento de acciones
- Evaluación de control de riesgos

### 📈 Informe Diario

- Generar automáticamente TOP 20 acciones por puntuación cuantitativa
- Envío programado a Telegram

## Tareas Programadas

| Tarea | Hora | Descripción |
|-------|------|-------------|
| Filtrado | 8:00 diario (Lun-Vie) | Ejecutar habilidad de filtrado |
| Puntuación | 8:30 diario (Lun-Vie) | Puntuar resultados del filtrado |
| Informe | 9:30 diario (Lun-Vie) | Generar y enviar informe |

## Stack Tecnológico

- **Plataforma**: [OpenClaw](https://github.com/openclaw/openclaw)
- **Fuente de Datos**: [Tushare](https://tushare.pro/)
- **Envío**: Telegram Bot

## Directorio de Habilidades

```
skills/
├── quant-score/        # Habilidad de puntuación cuantitativa
├── stock-filter/      # Habilidad de filtrado de acciones
├── daily_report/      # Habilidad de informe diario
└── ...
```

## Uso

### Ejecutar Filtrado de Acciones

```bash
python skills/stock-filter/quant_score.py
```

### Ejecutar Puntuación Cuantitativa

```bash
python skills/quant-score/score.py
```

### Ejecutar Informe Diario

```bash
python skills/daily_report/report_sender.py
```

## Variables de Entorno

```bash
export TUSHARE_TOKEN="your_token_here"
```

---

*Mantenido por asistente de IA*

</div>
