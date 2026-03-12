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
├── stock-filter/      # 股票初筛技能
├── daily_report/       # 每日报告技能
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

---

# English

## JOJOClaw 🦞

> Personal AI assistant based on OpenClaw, focused on stock quantitative analysis

### Introduction

This is a personal AI assistant running on the OpenClaw platform, mainly used for quantitative analysis and stock selection in the A-share market.

### Features

- **Stock Screening**: Exclude ST/*ST and limit-up/limit-down stocks
- **Quantitative Scoring**: Price trends, capital flow, liquidity, sentiment, risk control
- **Daily Report**: Auto-generate TOP 20 stocks and push to Telegram

### Scheduled Tasks

- Stock Screening: 8:00 daily (Mon-Fri)
- Quant Scoring: 8:30 daily (Mon-Fri)
- Daily Report: 9:30 daily (Mon-Fri)

---

# Español

## JOJOClaw 🦞

> Asistente de IA personal basado en OpenClaw, enfocado en análisis cuantitativo de acciones

### Introducción

Este es un asistente de IA personal que se ejecuta en la plataforma OpenClaw, principalmente utilizado para análisis cuantitativo y selección de acciones en el mercado A-share.

### Funciones

- **Filtrado de Acciones**: Excluir acciones ST/*ST y con límite de precio
- **Puntuación Cuantitativa**: Tendencias de precios, flujo de capital, liquidez, sentimiento, control de riesgos
- **Informe Diario**: Generar automáticamente TOP 20 y enviar a Telegram

### Tareas Programadas

- Filtrado: 8:00 diario (Lun-Vie)
- Puntuación: 8:30 diario (Lun-Vie)
- Informe: 9:30 diario (Lun-Vie)
