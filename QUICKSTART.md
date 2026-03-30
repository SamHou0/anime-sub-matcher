# 快速开始指南

## 🚀 5分钟上手

### 第一步: 准备环境

确保已安装 Docker 和 Docker Compose:
```bash
docker --version
docker-compose --version
```

### 第二步: 修改配置

编辑 `docker-compose.yml`，将剧集目录路径改为你的实际路径:

```yaml
volumes:
  - /your/bangumi/path:/app/bangumi  # 修改这里
```

**示例路径:**
- Linux: `/mnt/nas/anime:/app/bangumi`
- Windows: `D:/Media/Bangumi:/app/bangumi`
- macOS: `/Users/yourname/Movies/Anime:/app/bangumi`

### 第三步: 启动应用

```bash
# 构建并启动
docker-compose up -d

# 查看日志（确认启动成功）
docker-compose logs -f
```

看到 `Running on http://0.0.0.0:5000` 表示启动成功！

### 第四步: 开始使用

1. 打开浏览器访问: **http://localhost:5000**
2. 拖拽字幕文件到上传区域
3. 选择目标剧集和季度
4. 点击"自动匹配字幕"按钮
5. 完成！✅

## 📋 目录结构示例

你的剧集目录应该是这样的:

```
/your/bangumi/path/
├── 进击的巨人/
│   ├── Season 01/
│   │   ├── [字幕组] 进击的巨人 S01E01.mkv
│   │   ├── [字幕组] 进击的巨人 S01E02.mkv
│   │   └── ...
│   └── Season 02/
│       └── ...
├── 鬼灭之刃/
│   └── Season 01/
│       └── ...
└── ...
```

## 🔧 常用命令

```bash
# 启动应用
docker-compose up -d

# 停止应用
docker-compose down

# 查看日志
docker-compose logs -f

# 重新构建（代码更新后）
docker-compose up -d --build

# 查看运行状态
docker-compose ps
```

## ⚠️ 注意事项

1. **必须修改挂载路径**: 将 docker-compose.yml 中的路径改为你的实际路径
2. **目录权限**: 确保Docker有权限读写你的剧集目录
3. **端口冲突**: 如果5000端口被占用，修改为其他端口（如8080:5000）
4. **文件名格式**: 字幕文件名需要包含集数信息（如[01], E01, S01E01等）

## 🆘 问题排查

### 应用无法访问?
```bash
# 检查容器是否运行
docker-compose ps

# 查看详细日志
docker-compose logs
```

### 看不到剧集列表?
- 检查挂载路径是否正确
- 确认目录结构符合要求（剧集名/Season XX/视频文件）
- 查看日志确认是否有权限问题

### 无法识别字幕集数?
- 确保文件名包含明确的集数信息
- 支持格式: `[01]`, `E01`, `EP01`, `S01E01` 等
- 使用原始字幕文件名，不要过度简化

## 📞 获取帮助

遇到问题？查看完整文档: [README.md](README.md)
