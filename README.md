# 小红书发布模块 (Xiaohongshu Publisher)

自动化发布内容到小红书的 Python 模块，支持视频和图文笔记的上传、定时发布、标签管理等功能。

## 功能特性

- 🚀 自动化发布视频和图文笔记到小红书
- 🖼️ 支持多图发布（1-9张图片）
- 🎬 支持视频发布
- 📅 支持定时发布
- 🏷️ 标签管理
- 🌐 HTTP API 接口
- 🔐 Cookie 登录管理
- 📦 媒体文件下载与上传（视频/图片）

## 目录结构

```
xiaohongshu_publisher/
├── xhs/                    # 核心模块
│   ├── __init__.py        # 模块导出
│   ├── publish.py         # 发布核心功能
│   ├── api_server.py      # FastAPI HTTP 服务
│   ├── liulanqi.py        # Chrome 浏览器驱动配置
│   ├── fetch_cookies.py   # Cookie 获取工具
│   └── utils.py           # 工具函数
├── cookies/               # Cookie 存储目录
├── output/                # 输出文件目录
├── requirements.txt       # 依赖列表
└── README.md             # 本文档
```

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Chrome 浏览器

确保系统已安装 Chrome 浏览器和对应的 ChromeDriver。

## 使用方法

### 方式一：直接调用 Python 函数

#### 1. 获取小红书登录 Cookie

```bash
cd xiaohongshu_publisher
python -m xhs.fetch_cookies
```

按提示在浏览器中登录小红书，完成后按回车，Cookie 将保存到 `cookies/xiaohongshu.json`。

#### 2. 发布内容

**发布视频笔记：**

```python
from xhs.publish import publish_xhs_content

# 准备内容数据
scripts_data = {
    "name": "测试视频",
    "tags": ["测试", "小红书"],
    "content": {
        "title": "这是标题",
        "script": "这是正文内容"
    }
}

# 发布视频笔记
success = publish_xhs_content(
    scripts_data=scripts_data,
    publish_time="2025-01-12 16:00",  # 定时发布时间
    media_paths=["output/video.mp4"], # 视频文件路径
    content_type="video"              # 内容类型：视频
)
```

**发布图文笔记：**

```python
from xhs.publish import publish_xhs_content

# 准备内容数据
scripts_data = {
    "name": "测试图文",
    "tags": ["旅行", "美食"],
    "content": {
        "title": "美好的一天",
        "script": "今天天气真好，分享一些美图"
    }
}

# 发布图文笔记（1-9张图片）
success = publish_xhs_content(
    scripts_data=scripts_data,
    publish_time="2025-01-12 16:00",    # 定时发布时间
    media_paths=[                        # 图片文件路径列表
        "output/image1.jpg",
        "output/image2.jpg",
        "output/image3.jpg"
    ],
    content_type="image"                 # 内容类型：图文
)
```

#### 3. 命令行发布

```bash
cd xiaohongshu_publisher
python -m xhs.publish "2025-01-12 16:00"
```

需要提前准备好 `output/script.json` 文件，格式如下：

```json
{
    "name": "测试视频",
    "tags": ["测试", "小红书"],
    "content": {
        "title": "这是标题",
        "script": "这是正文内容"
    }
}
```

### 方式二：HTTP API 服务

#### 1. 启动 API 服务

```bash
cd xiaohongshu_publisher
source venv/bin/activate
python -m xhs.api_server
```

服务将在 `http://localhost:8000` 启动。

#### 2. 公网访问（可选）

如果需要从外部网络（如飞书、其他服务器）调用 API，可以使用 Cloudflare Tunnel 暴露到公网：

```bash
# 安装 cloudflared（仅首次）
brew install cloudflared

# 启动 tunnel（新终端窗口）
cloudflared tunnel --url http://localhost:8000
```

启动后会显示公网地址，如：`https://xxx-xxx-xxx.trycloudflare.com`

在外部服务中使用：`https://xxx-xxx-xxx.trycloudflare.com/publish`

> **注意**：每次启动 tunnel 会生成新的公网地址，需要更新调用方的 URL。

#### 3. 发送发布请求

**发布视频笔记：**

```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "video",
    "name": "测试视频",
    "tags": ["测试", "小红书"],
    "content": {
      "title": "这是标题",
      "script": "这是正文内容"
    },
    "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
    "publish_time": "2025-01-12 16:00"
  }'
```

**发布图文笔记：**

```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "image",
    "name": "测试图文",
    "tags": ["旅行", "美食"],
    "content": {
      "title": "美好的一天",
      "script": "今天天气真好，分享一些美图"
    },
    "image_urls": [
      "https://picsum.photos/800/600",
      "https://picsum.photos/800/601",
      "https://picsum.photos/800/602"
    ],
    "publish_time": "2025-01-12 16:00"
  }'
```

#### 4. 查看 API 文档

访问 `http://localhost:8000/docs` 查看完整的 API 文档。

## API 接口说明

### POST /publish

发布内容到小红书（支持视频和图文笔记）。

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content_type` | string | ✅ | `"image"` 图文 / `"video"` 视频 |
| `name` | string | ✅ | 任务备注名（仅用于日志，不显示在笔记中）|
| `tags` | array/string | ✅ | 标签，如 `["标签1", "标签2"]` 或 `"标签1,标签2"` |
| `content.title` | string | ✅ | 笔记标题（**最多20字**）|
| `content.script` | string | ✅ | 笔记正文 |
| `image_urls` | array | 图文必填 | 图片URL列表（**1-9张**，必须是 http/https）|
| `video_url` | string | 视频可选 | 视频URL |
| `publish_time` | string | 可选 | 定时发布，格式: `"YYYY-MM-DD HH:MM"`，不填则默认5分钟后 |

**请求示例：**

```json
{
  "content_type": "image",
  "name": "任务备注",
  "tags": ["标签1", "标签2"],
  "content": {
    "title": "笔记标题",
    "script": "笔记正文内容"
  },
  "image_urls": [
    "https://picsum.photos/800/600",
    "https://picsum.photos/800/601"
  ],
  "publish_time": "2025-12-08 10:00"
}
```

**图片要求：**
- 数量：1-9 张
- 格式：JPEG/JPG/PNG/WebP
- 大小：每张 < 10MB
- 尺寸：建议 ≥ 600x600

**响应示例：**

```json
{
  "success": true,
  "message": "Content queued for publishing (Task ID: abc123)",
  "task_id": "abc123",
  "video_downloaded": true,
  "scheduled_time": "2025-01-12 16:00",
  "queue_position": 1
}
```

### GET /health

健康检查接口，返回服务状态和队列信息。

### GET /queue/status

查看当前发布队列状态。

## 工作原理

1. **登录管理**：使用 Cookie 方式登录小红书创作者平台
2. **浏览器自动化**：通过 Selenium 控制 Chrome 浏览器
3. **笔记类型切换**：自动点击"上传图文"或"上传视频" Tab
4. **内容填充**：自动填写标题、正文、标签等信息
5. **媒体上传**：
   - 视频：上传单个视频文件
   - 图文：批量上传1-9张图片
6. **定时发布**：设置发布时间并提交

## 注意事项

- 首次使用需要手动登录获取 Cookie
- Cookie 可能会过期，需要定期更新
- 发布任务按队列顺序执行，确保不会并发操作浏览器
- 标题最多 20 个字符
- 建议使用定时发布避免频繁操作
- **视频笔记**：视频文件建议使用 MP4 格式
- **图文笔记**：
  - 支持 1-9 张图片
  - 支持格式：JPEG/JPG/PNG/WebP
  - 每张图片 < 10MB
  - 建议尺寸 ≥ 600x600

## 依赖项

- `selenium` - 浏览器自动化
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `httpx` - HTTP 客户端（用于下载媒体文件）
- `pydantic` - 数据验证
- `Pillow` - 图片验证和处理

## 故障排查

### 1. Cookie 过期

重新运行 `python -m xhs.fetch_cookies` 获取新的 Cookie。

### 2. ChromeDriver 版本不匹配

确保 ChromeDriver 版本与 Chrome 浏览器版本匹配。

### 3. 元素定位失败

小红书页面可能更新，需要检查 `publish.py` 中的元素定位器是否仍然有效。

### 4. 登录失败（代理问题）

如果使用代理时登录小红书失败，浏览器驱动已配置 `--no-proxy-server` 参数，会绕过系统代理直接连接。

### 5. Cloudflare Tunnel 连接失败

如果 tunnel 无法连接，可能是网络代理干扰，尝试关闭代理软件后重试。

## 快速启动

```bash
# 终端1：启动 API 服务
cd /Users/xpw/ws/wxp_claude_code/xiaohongshu_publisher
source venv/bin/activate
python -m xhs.api_server

# 终端2：启动公网穿透（可选）
cloudflared tunnel --url http://localhost:8000
```

## 许可证

本模块提取自原项目，仅供学习和研究使用。
