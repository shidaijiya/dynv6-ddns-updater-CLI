# dynv6-ddns-updater-CLI

一个基于 Python 和 Windows 的命令行动态 DNS（DDNS）更新工具，用于自动将本机公网 IPv4/IPv6 地址同步到 [dynv6.com](https://dynv6.com)。支持加密配置、定时运行、日志记录、单实例运行以及无终端启动的打包版本。

---

## ✨ 功能特点

- 自动获取本机活动网络接口的公网 IPv4/IPv6 地址
- 查询当前 DNS 记录，仅在变更时发起更新请求
- 使用 `win32crypt` 加密配置文件，保护 API Token 安全
- 锁文件机制防止多实例并发运行
- 命令行模式或定时轮询均支持
- 支持打包为无终端 `.exe`，开袋即食

---

## 📁 项目结构

```

dynv6-ddns-updater-CLI/
├── run.py                   # 主程序入口
├── requirements.txt         # 依赖列表
├── ddns-secrets.bin         # 加密后的配置文件（运行后生成）
├── lib/
│   ├── log\_utils.py         # 日志记录模块
│   ├── network\_info.py      # 网络接口与公网 IP 获取
│   ├── process\_locker.py    # 进程锁（Windows专用）
│   ├── security.py          # 配置加密/解密
│   └── **init**.py
└── log/
└── ddns.log             # 日志文件（运行后生成）

````

---

## 💻 安装与运行

### 系统要求

- 操作系统：**Windows 10/11**
- Python：**3.6+**
- 必须具备公网访问权限和 dynv6 帐号

### 安装依赖

```bash
pip install -r requirements.txt
````

依赖包含：

* `requests`：发送 HTTP 请求
* `dnspython`：进行 DNS 查询
* `psutil`：枚举网卡接口
* `pywin32`：Windows 配置加密
* `portalocker`：锁文件实现

---

## 🚀 快速启动

### 单次运行（调试用途）

```bash
python run.py --token <your_token> --domain <yourdomain.dynv6.net> --update_type ipv6 --once
```

### 周期更新（推荐）

首次配置时运行：

```bash
python run.py --token <your_token> --domain <yourdomain.dynv6.net> --update_type both --update_interval 600
```

之后运行时将自动读取本地加密配置文件，无需重复输入参数。

---

## ⚙️ 命令行参数说明

| 参数                  | 类型       | 必需 | 说明                                      |
| ------------------- | -------- | -- | --------------------------------------- |
| `--token`           | `string` | ✅  | dynv6 API Token                         |
| `--domain`          | `string` | ✅  | 需要更新的 dynv6 主机名（如 `yourname.dynv6.net`） |
| `--update_type`     | `string` | ✅  | 更新类型：`ipv4` / `ipv6` / `both`           |
| `--update_interval` | `int`    | ❌  | 更新间隔（秒），默认：3600                         |
| `--conf_name`       | `string` | ❌  | 配置名称，默认："default"，用于识别多个配置              |
| `--once`            | `flag`   | ❌  | 单次运行模式，执行一次后立即退出                        |

---

## 🔒 配置加密说明

* 使用 Windows 原生 `win32crypt` 对配置信息进行加密保存（`ddns-secrets.bin`）
* 加密配置自动在首次运行后生成，内容包括 token、域名、类型、更新频率等
* 后续运行将自动加载该配置，无需重复输入

---

## 📦 打包版 EXE（开袋即食）

我们在 [Releases](https://github.com/shidaijiya/dynv6-ddns-updater-CLI/releases) 页面提供了 **无终端版 `.exe` 可执行文件**：

* 文件名：`dynv6-ddns-updater-CLI.exe`
* 无窗口弹出，适合长期后台运行
* 首次运行需带参数完成配置

### 示例（首次运行）

```bash
dynv6-ddns-updater-CLI.exe --domain yourdomain.dynv6.net --token your_token --update_type both --update_interval 3600
```

### 设置自动启动

1. 将 `dynv6-ddns-updater-CLI.exe` 放入以下目录：

   ```
   C:\Users\<你的用户名>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
   ```

2. 每次系统启动时将自动运行，并使用上次的配置进行定时更新

---

## 📄 日志与调试

* 所有日志记录写入：`./log/ddns.log`
* 包含：IP 检测、DNS 查询、更新结果、异常信息
* 日志等级支持 INFO、WARNING、ERROR

---

## ⚠️ 注意事项

* 本工具仅支持 Windows 系统
* 若需修改已保存配置，重新携带完整参数运行即可覆盖原配置
* 程序会自动创建并管理锁文件，确保每次只有一个实例运行

---


## 🙋‍♂️ 支持与反馈

如遇到问题或建议功能，请通过 GitHub Issues 提交，或发起 Pull Request 与我们共同完善项目。

## 🙏 鸣谢

特别感谢优秀开源项目 [[ddns-go](https://github.com/jeessy2/ddns-go)](https://github.com/jeessy2/ddns-go) 及其同类项目带来的启发！

