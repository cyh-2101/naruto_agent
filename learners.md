# Naruto Agent Lab 学习记录

## 这个文档怎么用

每完成一个 Stage，Codex 都在这里追加一节，只记录项目负责人必须理解的内容。

把本文件连同对应代码交给 ChatGPT，并对它说：

> 请把我当作项目负责人，根据 learners.md 教我最新完成的 Stage。先解释整体数据流，再按“概念、代码入口、安全边界、验证方法”教学。不要假设未验证功能已经可用。每讲完一个小节问我一个检查理解的问题，最后让我独立解释一次系统流程。

学习时不要求背诵全部实现细节，但应该能够：

- 解释这个 Stage 解决了什么问题；
- 指出主要模块之间的数据流；
- 说明安全边界和失败时的行为；
- 运行安全验证命令并理解结果；
- 分清 mock 验证、真实环境验证和尚未实现的功能。

---

## Stage 0 — Foundation Runtime and Recording Spine

状态：已实现，并通过 mock 和安全自动化测试；真实模拟器采集与真实输入尚未验证。

### 必须理解的核心流程

```text
CaptureBackend
  -> FramePacket
  -> placeholder observation / future perception
  -> PolicyOutput
  -> ControlCommand
  -> ActionScheduler
  -> SafetyGate
  -> InputBackend

所有帧、输入事件和控制状态
  -> EpisodeRecorder
  -> manifest + JSONL indexes + bounded raw frames
```

策略不能直接发送按键。它只能生成 `ControlCommand`，再经过调度器和安全门。

### 必学概念

1. **接口与实现分离**
   - `Protocol` 定义模块边界。
   - mock、dry-run 和 Windows 实现可以替换，但上层接口保持稳定。

2. **单调时间戳**
   - 运行时使用 `perf_counter_ns()`，不能用会被系统校时改变的普通时间。
   - UTC 时间只用于人类阅读的 episode 元数据。

3. **dry-run 与 fail-safe**
   - 默认输入后端不会发送真实按键。
   - 焦点丢失、画面过期或冻结、紧急停止、安全检查失败、异常等情况都应阻止动作并释放按键。

4. **有界资源**
   - 捕获队列有最大长度，满时丢弃最旧帧。
   - raw-frame fallback 有最大帧数，避免磁盘和内存无限增长。

5. **配置验证**
   - 窗口标题、裁剪区域、UI 区域和键位来自配置，不能硬编码。
   - 本机配置放在 `configs/local/`，默认不进入 Git。
   - 三个角色的技能与时间参数仍是未验证状态，不能猜测或补造。

6. **可追溯录制**
   - episode 保存 manifest、帧索引、输入事件、控制区间、配置哈希和质量标记。
   - 原始录制不可覆盖；异常结束也要留下可检查的记录。

7. **mock 验证不等于真实验证**
   - mock 能证明模块契约、安全逻辑和录制流程可运行。
   - mock 不能证明真实 DXCam 性能、模拟器裁剪、`SendInput`、窗口焦点检查或物理紧急停止有效。

### 主要代码入口

- 核心数据契约：`src/naruto_agent/core/contracts.py`
- 模块接口：`src/naruto_agent/core/interfaces.py`
- 高精度时钟：`src/naruto_agent/runtime/clock.py`
- 窗口发现：`src/naruto_agent/runtime/window.py`
- 捕获后端：`src/naruto_agent/runtime/capture/`
- 输入后端：`src/naruto_agent/runtime/input/`
- 安全门和调度器：`src/naruto_agent/runtime/safety.py`
- 配置模型：`src/naruto_agent/config/models.py`
- episode 录制：`src/naruto_agent/data/recorder.py`
- mock 垂直链路：`src/naruto_agent/demo.py`
- 命令行工具：`scripts/doctor.py`、`scripts/runtime.py`、`scripts/episode.py`
- 安全测试：`tests/`

### 必须会运行的安全命令

```powershell
python scripts/doctor.py --project-root .
python -m pytest -ra
python -m ruff check .
python scripts/runtime.py mock-demo --frames 8
```

拿到 mock episode 路径后：

```powershell
python scripts/episode.py inspect "<episode-directory>"
python scripts/episode.py validate "<episode-directory>"
```

### 当前已验证的事实

- 40 个安全测试通过。
- Ruff 检查通过。
- mock 垂直链路能生成并验证 episode。
- 三个角色配置均保持 `declared` 和 `verified: false`。
- 默认测试不会构造真实 Windows 输入后端。

### 当前不能声称的事情

- 不能声称真实模拟器采集已经稳定。
- 不能声称真实按键或紧急停止已经实机验证。
- 不能声称已经识别血量、位置、动画或角色。
- 不能声称任何角色技能、连招或时间参数正确。
- 不能声称存在行为克隆、强化学习、自博弈或世界模型。

### 学完后应能回答

1. 为什么策略不能直接调用键盘后端？
2. 为什么运行时用单调时间戳，而 manifest 还需要 UTC 时间？
3. 捕获队列满了以后为什么丢最旧帧？
4. 哪些条件失败时必须释放全部按键？
5. mock episode 通过验证，能证明什么，不能证明什么？
6. 为什么角色机制必须放在配置里并保持未验证？

### 一个小练习

不看上面的流程图，用自己的话解释：一帧画面如何变成一个安全的控制意图，又如何被记录下来。重点说明安全门位于哪里，以及发生异常时系统应该做什么。

---

## Architecture Checkpoint V2 — 纯视觉策略契约

状态：契约已实现，64 个安全测试通过；没有实机感知、训练或真实输入。

### 这次解决了什么

- 用 `Estimate[T]` 区分“值为 0/false”和“根本不知道”；
- 用一个 `TemporalCombatState` 保存双方、相对位置、回合和场景实体的时序状态；
- 从同一个状态生成 IR、SQ 两种身份视图；IR 是主模式，SQ 是身份不可靠时的降级模式；
- 策略以后输出 `SemanticAction`，不再直接理解按键；
- 用 `ActionCapabilities` 判断角色此刻能不能做某动作，再经过 scheduler 和 SafetyGate；
- Episode V2 会明确记录某条数据流是 valid、unknown、stale 还是 not implemented。

### 必须理解的数据流

```text
画面 -> 被动感知 -> TemporalCombatState -> IR（主）/SQ（降级）
-> 共享时序骨干 -> 角色适配 -> SemanticAction
-> ActionCapabilities -> 角色动作适配
-> ActionScheduler -> SafetyGate -> InputBackend
```

其中从“被动感知”到“共享时序骨干”目前只有契约，没有可用游戏模型。

### 两种视图

- IR：对手身份置信度和新鲜度足够时，使用双方身份，追求最高信息利用率；
- SQ：对手身份未知、过期、低置信度或冲突时，只知道我方配置身份。

SQ 隐藏对手身份时，序列化结果里连对手身份字段都不存在，不是写成 `null`。未来训练可
随机隐藏对手身份，让共享大脑不能只靠角色名字，但最终运行在身份可靠时仍优先 IR。

### 能力和安全为什么分开

`ActionCapabilities` 判断动作是否合法或是否已校准；`SafetyGate` 判断现在是否允许发送任何
输入。动作即使合法，也仍然可能因为 dry-run、失焦、旧画面或急停而被 SafetyGate 拒绝。

### 主要代码入口

- `src/naruto_agent/core/estimates.py`
- `src/naruto_agent/core/combat_state.py`
- `src/naruto_agent/core/observations.py`
- `src/naruto_agent/core/actions.py`
- `src/naruto_agent/runtime/semantic.py`
- `src/naruto_agent/data/models.py`
- `docs/ARCHITECTURE.md`
- `docs/CODEX_WORK_ORDER_002.md`

### 当前不能声称

- 不能说系统已经能从游戏画面识别血量、技能或角色；
- 不能说任何角色机制、动作时间或连招已校准；
- 不能说共享骨干或策略模型已经实现或训练；
- 不能说测试证明了真实模拟器、DXCam、SendInput 或游戏水平；
- 不能开始 BC、PPO、RL、自博弈、HELT/PFSP 或 world model。

### 学完后应能回答

1. `Estimate(False)` 与 unavailable 有什么区别？
2. 为什么 IR/SQ 必须来自同一个状态？
3. 什么时候用 IR，什么时候降级到 SQ？
4. `SemanticAction` 怎样到达输入后端？
5. `ActionCapabilities` 与 `SafetyGate` 各负责什么？
6. 64 个测试证明了什么，又没有证明什么？

### 小练习

让 ChatGPT 给你一个“技能动作合法，但画面已过期”的例子，然后由你解释系统应该在哪两
个阶段分别做出什么决定。

---

## 后续 Stage 追加模板

### Stage N — 名称

状态：已实现 / mock 验证 / 实机验证 / 部分阻塞。

#### 这个 Stage 解决了什么

- 

#### 必学概念

- 

#### 数据流

```text

```

#### 主要代码入口

- 

#### 安全边界

- 

#### 验证命令与证据

- 

#### 尚未实现或尚未验证

- 

#### 学完后应能回答

1. 
2. 
3. 

#### 一个小练习

- 
