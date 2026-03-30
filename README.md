# 动画字幕自动匹配工具

一个简单易用的 Web 应用程序，用于自动识别字幕文件的集数并匹配到对应的剧集视频文件。

## ✨ 特性

- 🎯 **自动识别集数**: 使用 anitopy 库智能解析各种动画字幕命名格式
- 🎨 **友好的界面**: 现代化的响应式 Web 界面，支持拖拽上传
- 🔄 **智能匹配**: 自动将字幕重命名为与视频文件相同的名称
- 🐳 **容器化部署**: 使用 Docker 一键部署，方便快捷
- 🔒 **安全可靠**: 文件类型验证、大小限制、路径安全检查

## 📋 系统要求

- Docker 和 Docker Compose
- 或者: Python 3.8+ (用于本地开发)

## 🚀 快速开始

### 方式一: 使用 Docker Compose (推荐)

1. **克隆或下载项目**

2. **修改配置**
   
   编辑 `docker-compose.yml` 文件，将 `/path/to/your/bangumi` 修改为你的实际剧集目录路径:
   
   ```yaml
   volumes:
     - /your/actual/bangumi/path:/app/bangumi  # 修改这里
   ```

3. **构建并启动**
   
   ```bash
   docker-compose up -d
   ```

4. **访问应用**
   
   打开浏览器访问: http://localhost:5000

5. **停止应用**
   
   ```bash
   docker-compose down
   ```

### 方式二: 本地运行

1. **安装依赖**
   
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **运行应用**
   
   ```bash
   python -m flask run --host=0.0.0.0 --port=5000
   ```

3. **访问应用**
   
   打开浏览器访问: http://localhost:5000

## 📁 目录结构要求

你的剧集目录应该遵循以下结构:

```
bangumi/
├── 剧集名称1/
│   ├── Season 01/
│   │   ├── 视频文件 S01E01.mkv
│   │   ├── 视频文件 S01E02.mkv
│   │   └── ...
│   └── Season 02/
│       └── ...
└── 剧集名称2/
    └── Season 01/
        └── ...
```

**示例**:
```
bangumi/
└── 搞姬日常/
    └── Season 01/
        ├── [VCB-Studio] 搞姬日常 S01E01.mkv
        ├── [VCB-Studio] 搞姬日常 S01E02.mkv
        └── [VCB-Studio] 搞姬日常 S01E03.mkv
```

## 🎯 使用方法

1. **上传字幕文件**
   - 拖拽字幕文件到上传区域，或点击选择文件
   - 支持格式: `.ass`, `.srt`, `.ssa`, `.vtt`, `.sub`
   - 系统会自动识别字幕文件名中的集数

2. **选择目标剧集**
   - 从下拉列表中选择剧集
   - 选择对应的季度

3. **自动匹配**
   - 点击"自动匹配字幕"按钮
   - 字幕将被重命名为与视频文件相同的名称（保留字幕扩展名）

## 📝 支持的字幕命名格式

使用 `anitopy` 库，支持各种常见的动画字幕命名格式:

- `[字幕组][剧名][01][编码信息].ass`
- `剧名 - 01.srt`
- `剧名.S01E01.ass`
- `剧名 EP01.srt`
- 以及更多其他格式...

## 🔧 配置说明

### Docker Compose 配置

编辑 `docker-compose.yml` 可以自定义:

- **端口映射**: 默认 5000，可修改为其他端口
  ```yaml
  ports:
    - "8080:5000"  # 使用 8080 端口访问
  ```

- **剧集目录**: 必须修改为你的实际路径
  ```yaml
  volumes:
    - /mnt/media/anime:/app/bangumi
  ```

- **上传目录**: 可选，用于持久化临时文件
  ```yaml
  volumes:
    - ./uploads:/app/uploads
  ```

## 🛠️ 技术栈

- **后端**: Python Flask
- **前端**: HTML5 + JavaScript + Bootstrap 5
- **字幕解析**: anitopy
- **容器化**: Docker + Docker Compose

## 🔒 安全特性

- 文件上传大小限制 (10MB)
- 严格的文件类型验证
- 路径遍历攻击防护
- 文件覆盖前检查

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## ❓ 常见问题

**Q: 为什么识别不到我的字幕集数?**  
A: 请确保字幕文件名包含明确的集数信息，如 `[01]`, `E01`, `EP01`, `S01E01` 等。

**Q: 如何修改端口?**  
A: 编辑 `docker-compose.yml` 中的 `ports` 配置。

**Q: 字幕文件会被移动还是复制?**  
A: 字幕文件会被复制到目标位置，上传的临时文件会在成功后删除。

**Q: 支持批量上传吗?**  
A: 当前版本不支持批量上传，需要逐个处理。

## 📞 支持

如有问题，请提交 GitHub Issue。
