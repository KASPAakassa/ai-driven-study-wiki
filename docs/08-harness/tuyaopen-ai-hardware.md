# TuyaOpen:AI 智能体硬件的开源 Harness(涂鸦全栈 AIoT SDK)

> **一句话摘要**:软件 Agent 的 harness 是"执行外壳",**AI 硬件 Agent 的 harness 还要管物理世界**:语音(ASR/KWS/TTS/STT)、LLM 集成、多模态感知、云连接、OTA。TuyaOpen 是涂鸦的开源全栈 AIoT SDK(C/C++,GitHub 1.6k★,Apache 2.0):五层架构(TKL 内核 → TAL 抽象 → Libraries → Services → Applications)一次开发、多端部署,支持涂鸦 T 系列/ESP32/树莓派/Linux,拖拽式云工作流集成 ChatGPT/Gemini/Qwen 等模型,并配套 TuyaOpenClaw(硬件 Agent)、TuyaOpen IDE(AI Coding 插件)。
>
> **来源**:涂鸦官方文档《关于 TuyaOpen》,https://tuyaopen.ai/zh/docs/about-tuyaopen;仓库:https://github.com/tuya/TuyaOpen;原始资料存档于 `docs/inbox/tuyaopen-source.md`

## 概念:AI 硬件 Harness 与软件 Harness 的区别

!!! tip "定位一句话"
    TuyaOpen 是一套灵活的跨平台 C/C++ SDK,用于构建**下一代 AI 智能体硬件**——它是"AI 硬件 Agent 的 harness":给硬件设备装上语音大脑、LLM 能力、多模态感知与云连接,让设备从"智能家电"变成"能对话、能推理、能行动的硬件 Agent"。

| 维度 | 软件 Agent harness(站内 08 章节) | AI 硬件 harness(TuyaOpen) |
| --- | --- | --- |
| 执行对象 | 代码/文件/API | **物理设备**(传感器/麦克风/屏幕/网络) |
| 感知 | 文本/工具结果 | **语音/视觉/传感器**(ASR/VAD/AEC/唤醒词) |
| 输出 | 文本/动作 | **TTS 语音/UI/设备动作/云服务** |
| 部署 | 云/终端 | **芯片固件**(T5AI/ESP32/树莓派) |

!!! note "与站内 [Harness 概念](../08-harness/index.md) 的对照"
    Harness 定义(让模型作为 Agent 运行的系统)在硬件场景延伸为:**让 LLM 运行在物理设备上并安全操作硬件能力**——TuyaOpen 是这条线的开源代表。

## 原理:五层架构详解

```
⑤ Applications   应用层:工业/户外/视觉/音频/AI 智能体/机器人/智能家居/安防…
④ Services       服务层:涂鸦云(AI Agent/Multi-Model/Cloud ASR/VAD/IoT PaaS/LLM/RAG)+
                          跨平台工具(tos.py/Arduino/Lua/MicroPython)+ 外设驱动 TDD + 音频 ASR
③ Libraries      库层:网络协议(MQTT/mbedTLS/HTTP/WebSocket)+ 资源管理器(AI Service/Display/Audio)+
                         多媒体(P2P/RTSP/RTP)+ 工具(LVGL/cJSON/QR)
② TAL Abstract   抽象层:TuyaOpen API(OS+Device:内存/日志/事件/线程/安全存储)+
                         连接性(Wi-Fi/Ethernet/LTE Cat.1/BT)+ 安全(算法/引擎)
① TKL Kernel     内核层:硬件平台 SDK(T 系列 MCU/ESP32 IDF/树莓派 Pico)+
                         通用驱动(PWM/ADC/DAC/GPIO/I2C)+ 异构 BSP(ARM SoCs/Linux)
```

| 层 | 一句话 | 对 AI Agent 的意义 |
| --- | --- | --- |
| **TKL 内核** | 硬件基石(芯片 SDK + 通用驱动) | 开发者通常无需关注,芯片能力的对接与映射 |
| **TAL 抽象** | 中间桥梁(OS+Device API/连接性/安全) | 统一接口:内存/日志/线程/时间 + Wi-Fi/BT + 加密 |
| **Libraries** | 即拿即用组件(MQTT/HTTP/WebSocket、AI Service Manager、LVGL/cJSON) | 联网协议与资源管理开箱即用 |
| **Services** | 应用创新支撑(涂鸦云 **AI Agent**/LLM/RAG、Cloud ASR/VAD、音频 ASR) | **AI 能力层**:云端工作流 + 语音管道 |
| **Applications** | 终端应用(AI 智能体/机器人/智能家居等) | 业务场景落地 |

!!! tip "分层设计的核心优势**
    底层灵活适配硬件,中间层能力可复用,上层应用基于标准化服务开发——**"一次开发,多端部署"**,加速 AIoT 应用落地。

## 代码 / 实现:硬件 Agent 能力编排演示(纯 Python)

把"语音输入 → LLM 推理 → TTS 输出 + 云上报"的硬件 Agent 管线落成可运行演示:

```python
# —— 硬件 AI Agent 的能力编排(TuyaOpen Services 层的简化模拟)——
class HardwareAgent:
    def __init__(self):
        self.asr = lambda audio: "今天天气怎么样"      # 语音识别(ASR)
        self.llm = lambda text: "晴,24°C"             # LLM 推理
        self.tts = lambda text: f"[语音播报] {text}"   # 语音合成(TTS)
        self.cloud = lambda msg: f"[云上报] {msg}"     # 涂鸦云

    def handle_voice(self, audio):
        text = self.asr(audio)
        print(f"  ASR: {text}")
        if text:                                     # 唤醒词/意图路由后调 LLM
            reply = self.llm(text)
            print(f"  LLM: {reply}")
            print(f"  {self.tts(reply)}")
            print(f"  {self.cloud(reply)}")
            return reply
        return "未识别"

agent = HardwareAgent()
print(agent.handle_voice("audio_sample"))
assert agent.handle_voice("x") == "晴,24°C"
print("\n代码验证通过 ✔")
```

## 实践 / 应用:平台、版本与生态

### 支持平台矩阵(节选)

| 平台 | Windows | Linux | macOS |
| --- | --- | --- | --- |
| ESP32 / ESP32-S3 / T5AI | ✅ | ✅ | ✅ |
| BK7231X / LN882H / T2 / T3 | ⌛️ | ✅ | ⌛️ |
| Ubuntu | ➖ | ✅ | ➖ |

### 版本策略

- **release**(稳定,推荐生产)/ **master**(测试,每周三合并 dev)/ **dev**(最新功能,可能不稳定);
- 稳定版 1-2 个月发布一次。

### 生态组件

| 组件 | 说明 |
| --- | --- |
| **TuyaOpenClaw** | AI 硬件伴侣 Agent(原 DuckyClaw)——给硬件装上的"伴侣 Agent" |
| **TuyaOpen IDE** | 用 AI Coding Agent 开发 TuyaOpen 的 IDE 插件 |
| **tyutool / WebTool** | GUI/CLI 串口烧录工具 / 浏览器串口工具 |
| **tos.py** | 跨平台辅助工具(编译/烧录/调试) |
| **云端与 AI** | 拖拽式工作流、LLM Model、RAG、Cloud ASR/VAD、IoT PaaS |

### 与站内其他文章的呼应

- [Harness 概念与收录清单](index.md):TuyaOpen 是"AI 硬件 Harness"方向的专题补充(现有专题都是软件 Harness);
- [生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md):TuyaOpen 五层可对照 9 层(L1 算力底座→TKL/TAL;L3 上下文→Libraries;L4 编排→Services 的 AI Agent 工作流);
- [AI 原生组织方法论](../06-enterprise/ontology-agent-adoption/ai-native-organization-methodology.md):硬件 Agent(智能体硬件)是 Agent 落地的物理形态;
- [落地方法论](../06-enterprise/ontology-agent-adoption/agent-landing-micro-agents.md):"确定性代码包围模型"在硬件侧 = TAL 抽象层 + 安全引擎兜底。

## 总结

- **定位**:AI 智能体硬件的开源全栈 SDK——语音 + LLM + 多模态 + 云连接,给硬件装"大脑";
- **五层架构**:TKL(硬件基石)→ TAL(统一接口/连接/安全)→ Libraries(协议/资源管理)→ Services(涂鸦云 AI Agent/LLM/RAG/语音)→ Applications(场景落地);
- **生态**:TuyaOpenClaw(硬件 Agent)、TuyaOpen IDE(AI Coding)、tyutool、tos.py、拖拽式云工作流;
- **一句话**:当 Agent 的"执行环境"从终端变成物理设备,harness 就要多管语音、多模态、芯片与云——TuyaOpen 是这条"AI 硬件 harness"路线的开源起点。

## 延伸阅读

- 官方:https://tuyaopen.ai/zh/docs/about-tuyaopen;仓库:https://github.com/tuya/TuyaOpen(Arduino 版/Luanode 版见官方页);原始资料存档于 `docs/inbox/tuyaopen-source.md`
- 站内:[Harness 概念与收录清单](index.md)、[生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md)、[AI 原生组织方法论](../06-enterprise/ontology-agent-adoption/ai-native-organization-methodology.md)
