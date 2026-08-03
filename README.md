# headline_new

A "Toutiao"-style news app — a FastAPI + Vue 3 practice project.

一个类似「今日头条」的新闻 App,用来练习 FastAPI 的全栈练习项目。

**[English](#english) · [中文](#中文)**

> **Tutorial source / 教程来源**: the project follows a HeiMa Programmer video tutorial —
> <https://www.bilibili.com/video/BV1zV2QBtE39/>
>
> The frontend comes from that tutorial; the backend was built by following along, with some
> deliberate changes (see [Differences from the tutorial](#differences-from-the-tutorial)).
>
> 前端代码来自该教程,后端由本人跟着流程逐步实现,并做了一些改动,详见[与教程的差异](#与教程的差异)。

---

# English

## Tech stack

| Layer | Choice |
| --- | --- |
| Backend | FastAPI 0.115 · SQLAlchemy 2.0 (async) · Alembic · Pydantic v2 |
| Database | PostgreSQL (hosted on [Neon](https://neon.tech/)), `asyncpg` driver |
| Auth | UUID token + `passlib`/`bcrypt` password hashing |
| AI | Gemini, proxied through the backend (OpenAI-compatible API + SSE streaming) |
| Frontend | Vue 3.5 · Vite 7 · Vant 4 · Pinia · Vue Router · vue-i18n |

## Project layout

```
headline_new/
├── Backend/
│   ├── config/                     database connection, Gemini settings
│   ├── models/                     SQLAlchemy models (tables)
│   ├── schemas/                    Pydantic models (validation / serialization)
│   ├── crud/                       database operations
│   ├── routers/                    endpoint definitions
│   ├── utils/                      auth dependency, hashing, response envelope, seed scripts
│   ├── alembic/                    migration history
│   ├── main.py                     application entry point
│   └── requirements.txt
└── front-end-part-of-news-project/  frontend (from the tutorial)
    └── src/
        ├── views/                  pages
        ├── components/             components
        ├── store/                  Pinia stores
        ├── i18n/                   English / Chinese locale files
        └── config/api.js           backend base URL
```

## Getting started

### 1. Backend

```bash
# create the environment and install dependencies
conda create -n headline-backend python=3.11 -y
conda activate headline-backend
cd Backend
pip install -r requirements.txt

# configure environment variables
cp .env.example .env      # then fill in your database URL and Gemini API key

# create the tables
alembic upgrade head

# seed test data (optional)
python -m utils.seed_categories    # 8 news categories
python -m utils.seed_news          # 2 test articles per category

# run
uvicorn main:app --reload
```

Once running:

- API at <http://127.0.0.1:8000>
- Auto-generated docs at <http://127.0.0.1:8000/docs>

### 2. Frontend

```bash
cd front-end-part-of-news-project
npm install
npm run dev
```

Open <http://localhost:5173>. The frontend targets `http://127.0.0.1:8000` by default — change it in
`src/config/api.js`.

## Environment variables

Everything lives in `Backend/.env`, which is gitignored — **never commit it**. See `.env.example`:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL URL in `postgresql+asyncpg://...` form (not plain `postgresql://`) |
| `GEMINI_API_KEY` | Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Model name, defaults to `gemini-flash-latest` |
| `GEMINI_BASE_URL` | Optional; defaults to Google's OpenAI-compatible endpoint |

> **Note for Neon users**: the URL from the console ends with `?sslmode=require`, which `asyncpg`
> does not accept — drop it. SSL is configured via `connect_args` in `config/db_conf.py`. Prefer the
> pooled (`-pooler`) host.

## API reference

Every endpoint answers with the same `{"code", "message", "data"}` envelope, on both success and
failure.

### News `/api/news`

| Method | Path | Description | Auth |
| --- | --- | --- | :---: |
| GET | `/categories` | List categories | |
| GET | `/list?categoryId&page&pageSize` | Paginated articles by category | |
| GET | `/detail?id` | Article detail (increments views, includes related articles) | |

### User `/api/user`

| Method | Path | Description | Auth |
| --- | --- | --- | :---: |
| POST | `/register` | Register, returns a token | |
| POST | `/login` | Log in, returns a token | |
| GET | `/info` | Current user profile | ✓ |
| PUT | `/update` | Update nickname / avatar / gender / bio | ✓ |
| PUT | `/password` | Change password (signs out other devices) | ✓ |

### Favorites `/api/favorite`

| Method | Path | Description | Auth |
| --- | --- | --- | :---: |
| GET | `/check?newsId` | Whether an article is favorited | ✓ |
| POST | `/add` | Add a favorite | ✓ |
| DELETE | `/remove?newsId` | Remove a favorite | ✓ |
| GET | `/list?page&pageSize` | List favorites | ✓ |
| DELETE | `/clear` | Clear all favorites | ✓ |

### History `/api/history`

| Method | Path | Description | Auth |
| --- | --- | --- | :---: |
| POST | `/add` | Record a view (one row per article; the latest visit wins) | ✓ |
| GET | `/list?page&pageSize` | List history | ✓ |
| DELETE | `/delete/{history_id}` | Delete one entry | ✓ |
| DELETE | `/clear` | Clear all history | ✓ |

### AI chat `/api/ai`

| Method | Path | Description | Auth |
| --- | --- | --- | :---: |
| POST | `/chat` | Streaming conversation (SSE) | ✓ |
| GET | `/history` | Conversation log | ✓ |
| DELETE | `/history` | Clear the conversation log | ✓ |

**Authentication**: send `Authorization: <token>`. The `Bearer <token>` form works too.

## Database

Seven tables: `users`, `user_token`, `news`, `news_category`, `favorite`, `history`, `ai_chat`.

Schema changes go through Alembic. After editing a model:

```bash
alembic revision --autogenerate -m "message"   # generate the migration
# open the generated file and read it — autogenerate is not always right,
# especially when renaming a column
alembic upgrade head                           # apply it
```

## Differences from the tutorial

- **PostgreSQL (Neon) instead of MySQL**, with `asyncpg` as the driver.
- **Gemini instead of the tutorial's provider, proxied through the backend.** The tutorial keeps the
  API key in a frontend config file, which ships it to every visitor's browser and is easy to commit
  by accident. Here the frontend calls its own `/api/ai/chat` and the key stays in `Backend/.env`.
- **No `related_news` join table.** Related articles are simply other articles in the same category.
- **English UI by default.** Pages that never went through i18n (login, register, favorites,
  history, profile…) were wired up, and Vant's own built-in strings are switched along with them.
- **Shared timestamps on the `Base` class**, so every table has `create_at` / `update_at`.

## Known issues

- The AI endpoint only checks that you are logged in — there is no rate limiting. Add per-user
  throttling before deploying anywhere real.
- The backend URL in `config/api.js` is hardcoded to `127.0.0.1:8000`; make it environment-aware
  before deploying.

## Notes

This project exists for learning FastAPI and is not commercial. The frontend code belongs to the
original tutorial author.

---

# 中文

## 技术栈

| 层 | 选型 |
| --- | --- |
| 后端 | FastAPI 0.115 · SQLAlchemy 2.0(异步)· Alembic · Pydantic v2 |
| 数据库 | PostgreSQL(托管在 [Neon](https://neon.tech/)),驱动 `asyncpg` |
| 认证 | UUID Token + `passlib`/`bcrypt` 密码哈希 |
| AI | Gemini(经后端代理,OpenAI 兼容接口 + SSE 流式输出) |
| 前端 | Vue 3.5 · Vite 7 · Vant 4 · Pinia · Vue Router · vue-i18n |

## 目录结构

```
headline_new/
├── Backend/                        后端
│   ├── config/                     配置:数据库连接、Gemini 配置
│   ├── models/                     SQLAlchemy 模型(表结构)
│   ├── schemas/                    Pydantic 模型(请求校验 / 响应序列化)
│   ├── crud/                       数据库操作
│   ├── routers/                    路由(接口定义)
│   ├── utils/                      认证依赖、密码哈希、统一响应、种子脚本
│   ├── alembic/                    数据库迁移历史
│   ├── main.py                     应用入口
│   └── requirements.txt
└── front-end-part-of-news-project/  前端(来自教程)
    └── src/
        ├── views/                  页面
        ├── components/             组件
        ├── store/                  Pinia 状态管理
        ├── i18n/                   中英文语言包
        └── config/api.js           后端地址配置
```

## 快速开始

### 1. 后端

```bash
# 创建环境并安装依赖
conda create -n headline-backend python=3.11 -y
conda activate headline-backend
cd Backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env      # 然后填入自己的数据库连接串和 Gemini API Key

# 建表(应用迁移)
alembic upgrade head

# 灌入测试数据(可选)
python -m utils.seed_categories    # 8 个新闻分类
python -m utils.seed_news          # 每个分类 2 条测试新闻

# 启动
uvicorn main:app --reload
```

启动后:

- 接口地址 <http://127.0.0.1:8000>
- 自动生成的接口文档 <http://127.0.0.1:8000/docs>

### 2. 前端

```bash
cd front-end-part-of-news-project
npm install
npm run dev
```

访问 <http://localhost:5173>。前端默认请求 `http://127.0.0.1:8000`,如需修改见 `src/config/api.js`。

## 环境变量

全部配置在 `Backend/.env`(该文件已被 `.gitignore` 排除,**不要提交**),模板见 `.env.example`:

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | PostgreSQL 连接串,格式 `postgresql+asyncpg://...`(注意不是 `postgresql://`) |
| `GEMINI_API_KEY` | Gemini API Key,在 [Google AI Studio](https://aistudio.google.com/apikey) 获取 |
| `GEMINI_MODEL` | 模型名,默认 `gemini-flash-latest` |
| `GEMINI_BASE_URL` | 可选,默认为 Google 的 OpenAI 兼容端点 |

> **Neon 用户注意**:控制台给出的连接串结尾带 `?sslmode=require`,`asyncpg` 不认这个参数,需要去掉
> ——SSL 已在 `config/db_conf.py` 里通过 `connect_args` 配置。建议使用带 `-pooler` 的连接池地址。

## 接口一览

统一响应格式为 `{"code", "message", "data"}`,成功和失败都是这个结构。

### 新闻 `/api/news`

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | :---: |
| GET | `/categories` | 分类列表 | |
| GET | `/list?categoryId&page&pageSize` | 按分类分页取新闻 | |
| GET | `/detail?id` | 新闻详情(浏览量 +1,含相关推荐) | |

### 用户 `/api/user`

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | :---: |
| POST | `/register` | 注册,返回 token | |
| POST | `/login` | 登录,返回 token | |
| GET | `/info` | 当前用户信息 | ✓ |
| PUT | `/update` | 修改昵称 / 头像 / 性别 / 简介 | ✓ |
| PUT | `/password` | 修改密码(同时踢下线其他设备) | ✓ |

### 收藏 `/api/favorite`

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | :---: |
| GET | `/check?newsId` | 是否已收藏 | ✓ |
| POST | `/add` | 添加收藏 | ✓ |
| DELETE | `/remove?newsId` | 取消收藏 | ✓ |
| GET | `/list?page&pageSize` | 收藏列表 | ✓ |
| DELETE | `/clear` | 清空收藏 | ✓ |

### 浏览历史 `/api/history`

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | :---: |
| POST | `/add` | 记录浏览(同一篇文章只保留一条,以最后一次访问为准) | ✓ |
| GET | `/list?page&pageSize` | 历史列表 | ✓ |
| DELETE | `/delete/{history_id}` | 删除单条 | ✓ |
| DELETE | `/clear` | 清空历史 | ✓ |

### AI 问答 `/api/ai`

| 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | :---: |
| POST | `/chat` | 流式对话(SSE) | ✓ |
| GET | `/history` | 对话记录 | ✓ |
| DELETE | `/history` | 清空对话记录 | ✓ |

**认证方式**:请求头 `Authorization: <token>`,`Bearer <token>` 格式也支持。

## 数据库

共 7 张业务表:`users`、`user_token`、`news`、`news_category`、`favorite`、`history`、`ai_chat`。

表结构变更通过 Alembic 管理,改完模型后:

```bash
alembic revision --autogenerate -m "说明"   # 生成迁移脚本
# 打开生成的文件检查一遍(autogenerate 不总是正确,改字段名时尤其要注意)
alembic upgrade head                        # 应用到数据库
```

## 与教程的差异

- **数据库用 PostgreSQL(Neon)而非 MySQL**,驱动相应换成 `asyncpg`
- **AI 换成 Gemini,并改为后端代理**:教程里 API Key 放在前端配置文件中,会随打包产物进入浏览器、
  也容易误提交到仓库;这里改成前端调用自己的后端 `/api/ai/chat`,Key 只保存在 `Backend/.env`
- **相关推荐不建关联表**:直接查同分类下的其他文章,省掉一张 `related_news` 表
- **界面默认英文**:补全了原本没接入 i18n 的页面(登录、注册、收藏、历史、个人信息等),
  并把 Vant 组件库自身的内置文案也一并切换
- **时间戳统一在 `Base` 基类**:所有表共用 `create_at` / `update_at`

## 已知问题

- AI 接口目前只有登录校验,没有频率限制;若要真正部署,建议加上按用户的调用限流
- 项目尚未部署,`config/api.js` 里的后端地址是写死的 `127.0.0.1:8000`,上线前需要改成按环境区分

## 说明

本项目仅用于学习 FastAPI,非商业用途。前端代码版权归原教程作者所有。
