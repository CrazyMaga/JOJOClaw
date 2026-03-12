# JOJOClaw 🦞

> 基于 OpenClaw 的个人 AI 助手，专注于股票量化分析

> Personal AI assistant based on OpenClaw, focused on stock quantitative analysis

> Asistente de IA personal basado en OpenClaw, enfocado en análisis cuantitativo de acciones

## 简介 / Introduction / Introducción

这是一个运行在 OpenClaw 平台上的个人 AI 助手，主要用于 A股市场的量化分析和选股。

This is a personal AI assistant running on the OpenClaw platform, mainly used for quantitative analysis and stock selection in the A-share market.

Este es un asistente de IA personal que se ejecuta en la plataforma OpenClaw, principalmente utilizado para análisis cuantitativo y selección de acciones en el mercado A-share.

---

## 功能特性 / Features / Funciones

### 📊 股票初筛 / Stock Screening / Filtrado de Acciones

- 排除 ST/*ST 股票 / Exclude ST/*ST stocks / Excluir acciones ST/*ST
- 排除当日涨跌停股票 / Exclude limit-up/limit-down stocks / Excluir acciones con límite de precio
- 筛选成交额活跃的股票 / Filter stocks with active trading volume / Filtrar acciones con volumen activo
- 筛选波动幅度足够的股票 / Filter stocks with sufficient volatility / Filtrar acciones con volatilidad suficiente

### ⭐ 量化评分 / Quantitative Scoring / Puntuación Cuantitativa

- 价格动线分析（均线多头排列）/ Price trend analysis (moving average alignment) / Análisis de tendencia de precios (alineación de medias móviles)
- 资金流向追踪（主力资金净流入）/ Capital flow tracking (net inflow of main funds) / Seguimiento de flujo de capital (entrada neta de fondos principales)
- 流动性保障评估 / Liquidity assessment / Evaluación de liquidez
- 情绪与股性分析 / Sentiment and stock behavior analysis / Análisis de sentimiento y comportamiento de acciones
- 风险控制评估 / Risk control assessment / Evaluación de control de riesgos

### 📈 每日报告 / Daily Report / Informe Diario

- 自动生成量化评分 TOP 20 股票 / Auto-generate TOP 20 stocks by quantitative score / Generar automáticamente TOP 20 acciones por puntuación cuantitativa
- 定时推送至 Telegram / Scheduled push to Telegram / Envío programado a Telegram

---

## 定时任务 / Scheduled Tasks / Tareas Programadas

| 任务 / Task / Tarea | 时间 / Time / Hora | 说明 / Description / Descripción |
|-----|------|-----|
| 股票初筛 / Stock Screening / Filtrado | 每天 8:00 (周一至周五) / 8:00 daily (Mon-Fri) / 8:00 diario (Lun-Vie) | 运行初筛技能 / Run screening skill / Ejecutar habilidad de filtrado |
| 量化评分 / Quant Scoring / Puntuación | 每天 8:30 (周一至周五) / 8:30 daily (Mon-Fri) / 8:30 diario (Lun-Vie) | 对初筛结果评分 / Score screening results / Puntuar resultados del filtrado |
| 每日报告 / Daily Report / Informe | 每天 9:30 (周一至周五) / 9:30 daily (Mon-Fri) / 9:30 diario (Lun-Vie) | 生成报告并推送 / Generate and push report / Generar y enviar informe |

---

## 技术栈 / Tech Stack / Stack Tecnológico

- **平台 / Platform / Plataforma**: [OpenClaw](https://github.com/openclaw/openclaw)
- **数据源 / Data Source / Fuente de Datos**: [Tushare](https://tushare.pro/)
- **推送 / Push / Envío**: Telegram Bot

---

## 技能目录 / Skills Directory / Directorio de Habilidades

```
skills/
├── quant-score/        # 量化评分技能 / Quantitative scoring skill / Habilidad de puntuación cuantitativa
├── stock-filter/      # 股票初筛技能 / Stock screening skill / Habilidad de filtrado de acciones
├── daily_report/      # 每日报告技能 / Daily report skill / Habilidad de informe diario
└── ...
```

---

## 使用方法 / How to Use / Cómo Usar

### 运行股票初筛 / Run Stock Screening / Ejecutar Filtrado de Acciones

```bash
python skills/stock-filter/quant_score.py
```

### 运行量化评分 / Run Quant Scoring / Ejecutar Puntuación Cuantitativa

```bash
python skills/quant-score/score.py
```

### 运行每日报告 / Run Daily Report / Ejecutar Informe Diario

```bash
python skills/daily_report/report_sender.py
```

---

## 环境变量 / Environment Variables / Variables de Entorno

```bash
export TUSHARE_TOKEN="your_token_here"
```

---

## 联系方式 / Contact / Contacto

- Telegram: @JOJO_7743_new_bot

---

*由 AI 助手运行维护 / Maintained by AI assistant / Mantenido por asistente de IA*
