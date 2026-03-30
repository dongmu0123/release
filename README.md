# 微信每日天气推送

每天自动推送天气预报 + 自定义文字到你的微信，无需电脑一直开着。

## 使用方法

### 第1步：获取 PushPlus Token

1. 微信搜索公众号 **「pushplus推送加」** 并关注
2. 进入公众号，点击菜单获取你的 **Token**（一串字符串）

### 第2步：创建 GitHub 仓库

1. 在 GitHub 上创建一个新仓库
2. 把本项目的文件全部推送上去：

```bash
cd tianqi
git init
git add .
git commit -m "初始化天气推送项目"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 第3步：配置 GitHub Secrets 和 Variables

进入你的 GitHub 仓库页面：

**Settings → Secrets and variables → Actions**

添加以下 **Secret**（加密，用于敏感信息）：

| Secret 名称 | 值 | 说明 |
|---|---|---|
| `PUSHPLUS_TOKEN` | 你的PushPlus Token | 必填 |

添加以下 **Variables**（明文，用于配置）：

| Variable 名称 | 值 | 说明 |
|---|---|---|
| `CITY` | 你的城市名，如 `上海` | 可选，默认北京 |
| `CUSTOM_TEXT` | 你想每天看到的话 | 可选，默认"今天也要加油鸭！" |

### 第4步：测试

1. 进入仓库的 **Actions** 页面
2. 左侧选择 **「每日天气推送」**
3. 点击 **「Run workflow」** 手动触发一次
4. 检查微信是否收到推送

### 推送时间

默认每天 **北京时间早上 7:30** 推送。

如需修改时间，编辑 `.github/workflows/daily_weather.yml` 中的 cron 表达式：
```yaml
# 格式：分 时(UTC) 日 月 星期
- cron: '30 23 * * *'   # UTC 23:30 = 北京时间 07:30
```

## 效果预览

推送内容包括：
- 当前温度 / 体感温度
- 今日最高最低温度
- 天气状况 / 湿度 / 风速
- 日出日落时间
- 你的自定义文字
