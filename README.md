# Deep-Human-Edge-Bing-Search-Simulator

基于 **Python + Selenium + Microsoft Edge WebDriver** 的 Bing 搜索页面自动化示例项目。

本项目包含桌面端和移动端两个脚本，用于学习 Selenium 浏览器控制、搜索框输入、结果页等待、页面滚动、链接点击、相关搜索词采集等自动化流程。请仅在个人学习、受控测试和低频辅助场景中使用，并遵守目标网站服务条款、robots/访问策略和当地法律法规。

> 重要说明：本项目不应用于刷量、排名操纵、账号风控规避、批量采集、广告/奖励任务、绕过平台限制或任何可能干扰第三方服务的行为。

## 项目文件

| 文件 | 说明 |
| --- | --- |
| `PC.py` | 桌面端 Edge 自动化脚本，使用桌面浏览器窗口和桌面端选择器节奏。 |
| `Mobilephone.py` | 移动端 Edge 自动化脚本，使用 Chromium 移动设备仿真配置。 |
| `README.md` | 项目说明、配置方式和使用边界。 |
| `CHANGELOG.md` | 简要变更记录。 |

## 功能概览

- 打开 Bing 并定位搜索框。
- 按字符输入搜索词，模拟普通输入节奏。
- 可选地从自动补全候选中选择与当前输入前缀相关的候选项。
- 等待搜索结果页加载。
- 从搜索框或 URL 参数读取实际搜索词，用于日志和去重。
- 在明显偏离计划搜索词时，重新以计划词发起搜索。
- 在结果页执行轻量滚动、短暂停留和有限点击。
- 从“相关搜索”“People Also Ask”等区域提取后续候选词。
- 维护一个去重队列，驱动后续搜索流程。

## 适用场景

推荐用途：

- 学习 Selenium 和 Edge WebDriver 的基本用法。
- 研究搜索结果页的 DOM 定位、等待条件和异常处理。
- 在自己的测试环境中验证浏览器自动化流程。
- 低频、人工监督下的页面交互练习。

不适用用途：

- 批量自动搜索或刷搜索次数。
- 操纵搜索排名、广告收益、奖励积分或平台任务。
- 绕过验证码、风控、反自动化检测或访问限制。
- 未经授权采集、复制或再分发第三方内容。
- 对第三方服务造成异常流量、干扰或负载压力。

## 环境要求

- Python 3.8+，建议 Python 3.10 或更高版本。
- Microsoft Edge 浏览器。
- 与 Edge 浏览器主版本匹配的 `msedgedriver.exe`。
- Python 依赖：`selenium`。

安装依赖：

```bash
pip install -U selenium
```

Edge WebDriver 下载地址：

```text
https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver
```

请确保 Edge 浏览器和 `msedgedriver.exe` 的主版本一致，否则 WebDriver 可能无法启动。

## 配置说明

运行前需要根据自己的机器修改脚本中的路径。

`PC.py`：

```python
user_data_path = "E:\\MyEdgeProfile"
service = Service(r"E:\WebDriver\msedgedriver.exe")
```

`Mobilephone.py`：

```python
user_data_path = r"E:\MyEdgeProfile_Mobile"
service = Service(r"E:\WebDriver\msedgedriver.exe")
```

建议桌面端和移动端使用不同的 Edge Profile 目录，避免同时运行时互相占用浏览器用户数据。

## 主要开关

两个脚本顶部都有以下配置项：

```python
STRICT_AUTOCOMPLETE = True
MIN_PREFIX_FOR_AUTOCOMPLETE = 3
ENFORCE_PLANNED_IF_DRIFT = True
QUEUE_LIMIT = 120
```

含义：

- `STRICT_AUTOCOMPLETE`：只选择与当前输入前缀相关的自动补全项。
- `MIN_PREFIX_FOR_AUTOCOMPLETE`：输入长度达到该值后才尝试自动补全。
- `ENFORCE_PLANNED_IF_DRIFT`：实际搜索词明显偏离计划词时，重新搜索计划词。
- `QUEUE_LIMIT`：相关搜索词队列最大长度。

## 运行方式

桌面端：

```bash
python PC.py
```

移动端：

```bash
python Mobilephone.py
```

脚本会启动 Edge 浏览器并执行多轮搜索页面交互。请在运行期间保持人工监督，发现验证码、登录验证、访问受限或异常页面时应立即停止脚本。

## 工作流程

1. 启动 Edge WebDriver。
2. 使用指定的 Edge 用户数据目录。
3. 访问少量普通页面作为启动前检查。
4. 从内置关键词列表或相关词队列中选择计划搜索词。
5. 打开 Bing 首页。
6. 清空搜索框并逐字输入计划搜索词。
7. 根据配置尝试选择相关自动补全项；否则直接回车搜索。
8. 等待结果页主要链接出现。
9. 读取实际搜索词并进行必要的偏离校正。
10. 执行轻量页面交互。
11. 收集相关搜索词并加入去重队列。
12. 按配置间隔进入下一轮。

## 桌面端与移动端差异

| 项目 | `PC.py` | `Mobilephone.py` |
| --- | --- | --- |
| 浏览器形态 | 桌面窗口 | 移动设备仿真 |
| User-Agent | 桌面 Edge UA 池 | 固定 Android/Edge UA |
| 点击方式 | `ActionChains` | 元素直接点击 |
| 窗口设置 | 随机桌面窗口尺寸 | `mobileEmulation` 设备参数 |
| 搜索间隔 | 较长 | 较短 |

## 已知限制

- Bing 页面结构可能变化，选择器需要随页面更新而维护。
- 地区、语言、登录状态、验证码和个性化结果会影响页面结构。
- 当前关键词列表中部分中文内容可能存在编码损坏，需要人工清理后再使用。
- 脚本异常处理比较宽泛，适合作为学习示例，不适合作为生产级自动化系统。
- 路径配置目前写在源码中，换机器运行前需要手动修改。

## 合规与安全建议

- 只在你有权访问和测试的环境中运行。
- 控制频率，避免持续、批量、无人值守运行。
- 不要尝试绕过验证码、登录验证、风控或访问限制。
- 不要将该脚本用于商业刷量、广告、奖励、排名或流量任务。
- 不要采集、存储或传播第三方个人信息、敏感信息或受版权保护内容。
- 如目标网站提示停止、限制或验证访问，应停止脚本并人工处理。

## 维护建议

后续如果继续维护，建议优先处理：

- 清理中文乱码关键词和注释。
- 将公共逻辑从 `PC.py` 与 `Mobilephone.py` 抽到共享模块。
- 将 WebDriver 路径、Profile 路径、搜索次数和间隔改为配置文件或命令行参数。
- 增加更明确的异常日志，方便定位页面结构变化和 WebDriver 启动问题。

