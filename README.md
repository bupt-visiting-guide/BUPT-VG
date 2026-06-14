# BUPT 访学指南 — 维护手册

基于 [VitePress](https://vitepress.dev) 的静态文档网站，汇聚北邮历届交流访学同学的问卷经验。内容由 CSV 问卷数据 + LLM 提炼自动生成，通过 Netlify 持续部署。

**内容更新只需三步**：换 CSV → 跑脚本 → 推代码。

---

## 目录

1. [技术栈速览](#1-技术栈速览)
2. [项目结构](#2-项目结构)
3. [环境准备（一次性）](#3-环境准备一次性)
4. [本地开发](#4-本地开发)
5. [内容更新三步流](#5-内容更新三步流)
6. [手动编辑页面](#6-手动编辑页面)
7. [数据流与架构](#7-数据流与架构)
8. [验证 Netlify 部署](#8-验证-netlify-部署)
9. [常见问题排查](#9-常见问题排查)
10. [进阶：修改 LLM 提示词](#10-进阶修改-llm-提示词)
11. [进阶：增加新的分类页面](#11-进阶增加新的分类页面)

---

## 1. 技术栈速览

| 层级 | 技术 | 用途 |
| --- | --- | --- |
| 文档框架 | VitePress 1.6 + Vue 3.5 | 静态站点生成、主题、搜索 |
| 词云可视化 | ECharts 5.5 + echarts-wordcloud 2.1 | `/insights/keyword-overview` 页面的交互式词云 |
| ETL 脚本 | Python 3 + pandas | 读取 CSV、脱敏、调用 LLM、写入 Markdown |
| LLM | DeepSeek（默认）/ Kimi / OpenAI | 提炼问卷摘要、发现关键词 |
| 部署 | Netlify | 自动构建，push 即部署 |

---

## 2. 项目结构

```
bupt-visiting-guide/
├── .env.example                  # API Key 配置模板
├── .env                          # 本地 API Key（gitignore）
├── .gitignore
├── package.json                  # Node 依赖（VitePress, ECharts…）
├── netlify.toml                  # Netlify 构建与缓存规则
│
├── data/
│   └── raw/                      # 问卷 CSV（gitignore，不上传仓库）
│       └── .gitkeep
│
├── docs/                         # 网站内容根目录
│   ├── index.md                  # 首页（Hero + Feature 卡片）
│   ├── public/data/keywords.json # 词云数据（ETL 自动生成）
│   ├── pre-departure/
│   │   ├── index.md              # 手写概览
│   │   ├── generated-insights.md # LLM 提炼摘要（自动覆盖）
│   │   ├── visa-and-documents.md
│   │   └── packing-checklist.md
│   ├── academics/
│   │   ├── index.md
│   │   ├── generated-insights.md
│   │   ├── course-selection.md
│   │   └── lab-and-research.md
│   ├── life-and-mindset/
│   │   ├── index.md
│   │   ├── generated-insights.md
│   │   ├── daily-life.md
│   │   └── mental-health.md
│   └── insights/
│       └── keyword-overview.md   # 手写骨架 + KeywordBubble 组件
│
├── scripts/etl/                  # Python ETL 管道
│   ├── run.py                    # 入口脚本
│   ├── config.py                 # 路径、LLM provider、种子关键词
│   ├── extract.py                # CSV 读取 + PII 脱敏
│   ├── transform.py              # LLM 调用 + 关键词计数
│   ├── load.py                   # 写入 Markdown + JSON Schema 校验
│   ├── requirements.txt
│   └── prompts/
│       ├── insight_extraction.txt  # 摘要提炼提示词
│       └── keyword_extraction.txt  # 关键词发现提示词
│
└── .vitepress/
    ├── config.mts                # 导航、侧边栏、搜索配置
    └── theme/
        ├── index.ts              # 注册 KeywordBubble 组件
        └── components/
            └── KeywordBubble.vue # ECharts 词云组件
```

### 文件生成关系

```
data/raw/*.csv
    │
    ▼  extract.py（读取 + 脱敏）
    │
    ▼  transform.py（LLM 提炼 + 关键词统计）
    │
    ├──▶ docs/{category}/generated-insights.md   （各分类摘要页）
    └──▶ docs/public/data/keywords.json           （词云数据）
              │
              ▼  KeywordBubble.vue（前端渲染）
```

---

## 3. 环境准备（一次性）

### 3.1 安装 Node.js（≥ 20）

从 [nodejs.org](https://nodejs.org) 下载 LTS 版本并安装。推荐使用 22.x。

### 3.2 安装前端依赖

```bash
npm install
```

### 3.3 安装 Python 依赖

```bash
pip install -r scripts/etl/requirements.txt
```

### 3.4 配置 LLM API Key

项目已包含 `.env.example` 作为模板。如果还没有 `.env` 文件，复制一份：

- **Windows（PowerShell）**：`Copy-Item .env.example .env`
- **Windows（CMD）**：`copy .env.example .env`
- **Mac / Linux**：`cp .env.example .env`

然后用文本编辑器打开 `.env`，在等号右侧填入你的 API Key。例如：

```ini
# .env 文件内容示例
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-你的真实key填在这里
KIMI_API_KEY=
OPENAI_API_KEY=
```

你要填的就是 `DEEPSEEK_API_KEY=` 等号右边那一串，把 `sk-你的真实key填在这里` 替换为你的真实 Key。其他两行用不上可以留空。

- **DeepSeek**（默认）：在 [platform.deepseek.com](https://platform.deepseek.com) 注册获取
- **Kimi**：在 [platform.moonshot.cn](https://platform.moonshot.cn) 注册获取
- **OpenAI**：在 [platform.openai.com](https://platform.openai.com) 获取

如要切换 LLM provider，修改 `.env` 中 `LLM_PROVIDER` 的值（`deepseek` / `kimi` / `openai`）。

---

## 4. 本地开发

### 4.1 启动开发服务器

```bash
npm run docs:dev
```

浏览器访问 `http://localhost:5173`，支持热更新。

### 4.2 构建生产版本

```bash
npm run docs:build
```

产物输出到 `docs/.vitepress/dist/`。

### 4.3 本地预览构建产物

```bash
npm run docs:preview
```

此命令与 Netlify 部署的内容一致，可在推送前做最后验证。

---

## 5. 内容更新三步流

### 步骤一：替换 CSV 文件

将新问卷导出的 CSV 放入 `data/raw/` 目录（旧文件可删除或保留）。

CSV 必须包含以下列（列名可为中文或英文）：

| 列名 | 说明 |
| --- | --- |
| `回答内容` 或 `response` | 必填，学生的回答文本 |
| `分类` 或 `category` | 可选，值为 `pre-departure` / `academics` / `life-and-mindset` |

> 如 CSV 导出时的列名与上述不同，在 `scripts/etl/extract.py` 的 `COLUMN_ALIASES` 字典中添加映射即可。

### 步骤二：运行 ETL 脚本

```bash
python scripts/etl/run.py
```

脚本会自动完成以下操作：

1. **Extract** — 读取所有 CSV，脱敏个人信息（学号、手机号、邮箱），汇总为结构化列表
2. **Transform** — 按分类分组，调用 LLM 提炼摘要建议；统计全量文本中的关键词频次
3. **Load** — 写入 `docs/{category}/generated-insights.md` 和 `docs/public/data/keywords.json`（写入前经过 JSON Schema 校验）

### 步骤三：本地预览 & 推送

```bash
# 1. 本地预览确认
npm run docs:dev

# 2. 确认无误后提交
git add docs/
git commit -m "chore: update content from questionnaire $(date +%Y-%m-%d)"
git push
```

推送后，Netlify 会在 2–3 分钟内自动重新部署网站。

---

## 6. 手动编辑页面

| 文件 | 编辑方式 | 说明 |
| --- | --- | --- |
| `docs/{category}/index.md` | 手动编辑 | 手写概览页，脚本**不会**覆盖 |
| `docs/{category}/generated-insights.md` | 通过脚本生成 | 每次跑 ETL 会覆盖 |
| `docs/{category}/*.md`（其他子页面） | 手动编辑 | 如 `visa-and-documents.md`、`daily-life.md` 等 |
| `docs/insights/keyword-overview.md` | 手动编辑 | 手写说明文字，词云图由 `<KeywordBubble />` 组件渲染 |
| `docs/public/data/keywords.json` | 通过脚本生成 | 前端词云的数据源 |
| `docs/index.md` | 手动编辑 | 首页 Hero + Feature 布局 |

---

## 7. 数据流与架构

### ETL 管道

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ Extract  │ ──▶ │  Transform   │ ──▶ │    Load      │
│          │     │              │     │              │
│ CSV→rows │     │ LLM→summary  │     │ .md + .json  │
│ PII 脱敏 │     │ seed+LLM→kw  │     │ schema 校验   │
└──────────┘     └──────────────┘     └──────────────┘
```

### 前端词云渲染

```
keywords.json ──▶ fetch() in onMounted ──▶ buildOption() ──▶ <VChart>
                                                              │
                                                    echarts-wordcloud
```

`KeywordBubble.vue` 使用 `vue-echarts` 封装，通过 `defineAsyncComponent` 延迟加载以避免 SSR 构建时的 `document is not defined` 错误。

### PII 隐私保护

Extract 阶段通过正则脱敏学号、手机号、邮箱。LLM prompt 层额外要求模型不还原任何个人信息，形成双重防护。

---

## 8. 验证 Netlify 部署

1. 推送到 GitHub 后，打开 [Netlify 控制台](https://app.netlify.com)
2. 进入项目 → **Deploys** 标签
3. 确认最新 deploy 状态为 **Published**（绿色）
4. 访问网站 URL，检查以下页面是否正常：
   - 首页和各分类页内容是否最新
   - `/insights/keyword-overview` 词云是否正常加载
   - 各分类的 `generated-insights` 是否显示了新数据

---

## 9. 常见问题排查

| 症状 | 原因 | 解决方法 |
| --- | --- | --- |
| `No CSV files found` | `data/raw/` 为空 | 将 CSV 文件放入该目录 |
| `API key not set` | `.env` 未配置 | 检查 `.env` 中对应 key；确认 key 指向的 provider 与 `LLM_PROVIDER` 一致 |
| LLM 返回乱码或空内容 | API 余额不足或超时 | 检查 LLM 平台余额；脚本内置指数退避重试，短时波动会自动恢复 |
| 词云显示"无法加载关键词数据" | `keywords.json` 不存在或路径错误 | 确认文件在 `docs/public/data/keywords.json`；若文件存在但内容为空，重新跑脚本 |
| `keywords.json failed schema validation` | LLM 返回格式异常 | 重新运行脚本；若持续失败，检查 LLM provider 余额或切换 provider |
| Netlify build 失败 | Node 版本不匹配 | 检查 `netlify.toml` 中 `NODE_VERSION` 是否为 `"22"` |
| 新页面不出现在导航/侧边栏 | `config.mts` 未更新 | 在 `.vitepress/config.mts` 的 `nav` 和 `sidebar` 中添加条目 |
| 开发服务器词云不显示 | SSR 兼容问题 | 确认 `KeywordBubble` 通过 `defineAsyncComponent` 加载；刷新页面即可 |

---

## 10. 进阶：修改 LLM 提示词

编辑以下文件，然后重新运行 `python scripts/etl/run.py`：

- `scripts/etl/prompts/insight_extraction.txt` — 控制各分类摘要的输出格式（核心建议、常见困难、综合总结）
- `scripts/etl/prompts/keyword_extraction.txt` — 控制 LLM 关键词的提取数量、长度和输出格式

修改提示词后建议先在单个分类上验证效果，再全量运行。

---

## 11. 进阶：增加新的分类页面

1. 在 `docs/` 下新建目录，例如 `docs/career/`，并创建 `index.md`
2. 在 `scripts/etl/config.py` 的 `CATEGORIES` 字典中添加：
   ```python
   "career": DOCS_DIR / "career",
   ```
3. 在 `.vitepress/config.mts` 的 `nav` 和 `sidebar` 中添加对应条目
4. 重新运行 ETL 脚本并验证

---

## 附录：上线前检查清单

部署前逐项确认：

- [ ] `.env` 中的 API Key 已在对应平台充值/激活
- [ ] GitHub 仓库 URL 已替换 `.vitepress/config.mts` 中的 `YOUR_ORG` 占位符
- [ ] `data/raw/` 中有至少一个 CSV 文件
- [ ] `python scripts/etl/run.py` 成功完成
- [ ] `npm run docs:dev` 本地预览无异常
- [ ] 词云页面 `/insights/keyword-overview` 正常渲染
- [ ] Netlify 已关联 GitHub 仓库

---

*技术问题请联系上一届维护者，或提交 Issue 到 GitHub 仓库。*
