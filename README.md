# 告警统计与 AI 摘要练习原型

这是一个用于学习和面试展示的**独立练习**。它只读取仓库内的虚构告警数据，**尚未接入 WiCare 的设备、线上服务或真实用户数据**。这里的模型调用是普通 API 请求，暂不包含 Agent、RAG 或工作流框架。

## 它做什么

`sample_events.json` → Python 按时间范围统计告警 → 本地摘要，或将统计事实交给 DeepSeek API 生成文字摘要。**告警次数由代码计算，不由模型猜测。**

样本里的 `days_ago` 表示相对天数：`0` 是今天，`1` 是昨天。它不对应任何真实日期。

中文练习页会直接展示原始 JSON。点击“统计告警”后，表格会标出每条记录是否被 Python 纳入统计，并展示 `main.py` 中读取、筛选和计数的代码。近 7 天会纳入第 1～4 条，排除 8 天前与 12 天前的两条。

### 第 3 步的 Prompt 是怎么来的

Prompt 是发给模型的任务说明。`main.py` 里的 `PROMPT_TEMPLATE` 先写好“用两句话概括、不能编造次数和原因”等要求，并用 `{range_days}`、`{total}`、`{by_type}` 留出数据位置。Python 先算出统计事实，再由 `prompt_for(facts)` 把这些空位填好。例如选近 7 天，会得到“近 7 天、共 4 次、跌倒 2 次、设备离线 2 次”。页面会并排展示原始模板和填好的内容。

如果配置了密钥并点击“生成 AI 摘要”，程序会把 `SYSTEM_PROMPT` 和填好的 Prompt 作为两条消息发送到模型接口，再读取模型返回的文字。模型只负责表述，次数以 Python 的统计为准，返回后仍需核对。**预览 Prompt 不等于实际调用模型。**

2026-10-28 已使用本地环境中的真实 API 密钥，验证近 7 天模拟数据的完整模型调用：返回摘要中的告警总数为 4 次，跌倒 2 次、设备离线 2 次，与 Python 统计一致。这次检查只覆盖该组模拟数据；不代表所有回答都会正确。密钥未纳入仓库。

## 在 Windows 上运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8766
```

打开 <http://127.0.0.1:8766/>，按中文页面的顺序操作：先看模拟告警，再选天数并统计，最后可选尝试 AI 摘要。初学时不用看接口文档。

如果你想检查接口，可以再打开 <http://127.0.0.1:8766/docs>：

1. `GET /health`：确认服务启动。
2. `GET /api/events`：查看六条虚构事件。
3. `POST /api/summary`：请求体填 `{"range_days": 7}`，应得到 4 次告警，其中 `fall` 2 次、`offline` 2 次。这个接口不需要密钥。
4. `POST /api/ai-summary`：可选。需要自己配置 DeepSeek API 密钥后才会真实调用模型；请求体同上。

运行统计检查：

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

## 可选：使用自己的模型 API 密钥

复制 `.env.example` 为本地 `.env`，把 `replace_with_your_key` 换成自己的密钥，然后重启服务。程序启动时会把它读入环境变量。`.env` 已加入 `.gitignore`，不会被正常 Git 提交；**提交前仍要运行 `git status` 自己确认**。不要把密钥粘贴到聊天、截图或 README 中。调用模型 API 可能产生费用。

没有密钥时，前三个接口和本地统计仍可运行；调用 `/api/ai-summary` 会明确返回 503，不会假装模型已接通。

## 面试时可以怎么说

“我做了一个与现有项目场景相关的独立练习：用模拟事件验证时间范围筛选和分类统计，再把**已经算好的事实**交给大模型写摘要。当前只在本地使用虚构数据验证，下一步才是接 WiCare 的历史事件接口并补权限、异常处理和实际数据测试。”

可以继续尝试：把 `range_days` 改成 1 或 30，观察统计；修改一条虚构事件，再运行检查；对比简短与详细 Prompt 的回复是否都与统计事实一致。
