# 原始资料:关于 TuyaOpen(涂鸦开源 AIoT SDK)

> 来源:https://tuyaopen.ai/zh/docs/about-tuyaopen(涂鸦官方文档,Apache 2.0)
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/08-harness/tuyaopen-ai-hardware.md(AI 硬件 Harness 专题收录)

## 核心内容(摘要存档)
- 定位:跨平台 C/C++ SDK,构建下一代 AI 智能体硬件;支持涂鸦 T 系列 Wi-Fi/蓝牙芯片、树莓派、ESP32 等;搭配涂鸦云低延迟多模态 AI(拖拽式工作流),集成 ChatGPT/Gemini/Qwen/Doubao 等
- 能力:语音(ASR/KWS/TTS/STT)、LLM 集成(Deepseek/ChatGPT/Claude/Gemini)、多模态 AI(文本/语音/视觉/传感器)、涂鸦云(远程控制/监控/OTA)、Google Home/Alexa、Powered by Tuya
- 五层架构:TKL Kernel Layer(硬件适配/通用驱动 PWM ADC DAC GPIO I2C/异构 BSP)→ TAL Abstract Layer(OS+Device API/连接性 Wi-Fi Ethernet LTE Cat.1 BT/安全)→ Libraries(网络协议 MQTT/mbedTLS/HTTP/WebSocket、资源管理器 AI Service Manager/Display/Audio、多媒体 P2P/RTSP/RTP、工具 LVGL/cJSON/QR)→ Services(跨平台开发工具 tos.py/Arduino/Lua/MicroPython、涂鸦云 AI Agent/Multi-Model/Cloud ASR/VAD/IoT PaaS/LLM Model/RAG、外设驱动 TDD、音频 ASR VAD/DOA/AEC/Wake-Word)→ Applications(工业/户外/视觉/音频/AI 智能体/机器人/运动健康/安防/智能家居)
- 支持平台:BK7231X/ESP32/ESP32-C3/ESP32-S3/LN882H/T2/T3/T5AI/Ubuntu(平台矩阵:Windows/Linux/macOS)
- 版本:release(稳定,生产)/master(测试)/dev(开发);稳定版 1-2 月,测试版每周三
- 相关:TuyaOpenClaw(AI 硬件伴侣 Agent,原 DuckyClaw)、TuyaOpen IDE(AI Coding Agent 开发 TuyaOpen 的插件)、tyutool(GUI/CLI 串口烧录)、WebTool(浏览器串口)、GitHub:https://github.com/tuya/TuyaOpen(1.6k★)
