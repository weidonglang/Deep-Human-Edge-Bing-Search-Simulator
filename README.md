# Deep-Human-Edge-Bing-Search-Simulator

**中文（Chinese）**：基于 **Selenium + Microsoft Edge** 的“类人”搜索脚本（PC 端与移动端各一份）。实现“真实检索对齐”“受控自动补全”“多源联想队列（相关搜索/PAA）”“跑题纠偏”“自然滚动与短暂停顿”等。
**English**: Human-like Bing search automation (PC & Mobile) built on **Selenium + Microsoft Edge**. It aligns logs with the **actual query**, uses **controlled autocomplete**, builds a **multi-hop related-terms queue (Related + PAA)**, performs **drift correction**, and simulates gentle scrolling/pauses.

---

## ✨ Features / 功能

* **Real query alignment / 真实检索对齐**
  从结果页读取搜索框 `value`（失败则回退解析 URL 的 `?q=`）作为“实际搜索词”，日志与去重使用该值，彻底消除“日志 A、实际搜 B”。参考：Selenium 获取输入值 `get_attribute("value")` 用法与示例。([Selenium][1])
* **Controlled autocomplete / 受控自动补全**
  仅当前缀 ≥3 且候选“以此前缀开头/包含此前缀”时才点击；否则直接回车。
* **Multi-hop related queue / 多跳联想队列**
  聚合“相关搜索”和 “People Also Ask（PAA）”，去重后入队，驱动下一轮检索。
* **Drift correction / 跑题纠偏**
  若实际词与计划词偏差过大，自动使用 `?q=<planned>` 强制纠偏，再继续交互。
* **PC & Mobile 两套脚本**

  * `PC.py`：桌面端选择器与节奏（点击主结果后自动返回继续抽取联想）。
  * `Mobilephone.py`：开启移动仿真（UA + deviceMetrics），触控点击与更平滑滚动。关于 Edge/Chromium 的设备模拟与 DevTools 设备模式可参见官方说明。([Microsoft Learn][2])

---

## 🧰 Prerequisites / 前置条件

* **Python 3.8+**（建议 3.10 以上）
* **Microsoft Edge 浏览器**
* **Edge WebDriver（msedgedriver）与浏览器版本匹配**
  Edge 官方要求 **主版本三段号**需与浏览器匹配（例如 `121.x.y.z` ↔ `121.x.y.z`），否则驱动会报错。检查浏览器版本：地址栏输入 `edge://settings/help`；再去 WebDriver 页面下载对应版本。([Microsoft Learn][3])
https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver?form=MA13LH
代码中驱动路径为：service = Service(r"E:\WebDriver\msedgedriver.exe") 
> 如果你不想手动管理驱动，也可以改用 `webdriver-manager` 自动下载（本仓库当前脚本使用**手动路径**方式）。

---

## 📦 Installation / 安装

```bash
# 1) 安装 Python 依赖
pip install -U selenium

# （可选）如果改成自动下载驱动：
pip install -U webdriver-manager
```
*也可以直接运行两个程序*
> Selenium 官方文档展示了用 `get_attribute("value")` 读取输入框值的方式，我们在脚本中据此实现“真实检索对齐”。([Selenium][1])

---

## ⚙️ Configure / 配置

打开脚本并根据你的环境修改以下常量（**必改路径**）：

* `PC.py`

  * `user_data_path = "E:\\MyEdgeProfile"` → 替换为你的 Edge 用户数据目录（用于持久化 Cookie/登录状态等）。
  * `Service(r"E:\WebDriver\msedgedriver.exe")` → 替换为你的 **msedgedriver** 绝对路径。
* `Mobilephone.py`

  * `user_data_path = "E:\\MyEdgeProfile_Mobile"` → 替换为移动脚本使用的独立 Profile 目录。
  * `Service(r"E:\WebDriver\msedgedriver.exe")` → 同上。

**可调开关（两份脚本一致）**：

* `STRICT_AUTOCOMPLETE = True`：只点击“与前缀相关”的下拉联想。
* `MIN_PREFIX_FOR_AUTOCOMPLETE = 3`：前缀不足 3 个字符不点联想。
* `ENFORCE_PLANNED_IF_DRIFT = True`：若跑题则强制回到计划词检索。
* `QUEUE_LIMIT = 120`：联想队列上限。

> Edge WebDriver 的 capability/EdgeOptions 配置项与启动方式见官方文档。([Microsoft Learn][4])
> DevTools 的移动设备模拟（UA、视口、节流等）介绍可参考官方说明。([Microsoft Learn][2])

---

## ▶️ Run / 运行

```bash
# PC/桌面端脚本
python PC.py

# Mobile/移动端脚本（Chromium 移动仿真 UA + deviceMetrics）
python Mobilephone.py
```

日志会打印“计划词 / 实际词”“是否点击联想”“是否触发纠偏”等关键信息。

---

## 🧠 How it works / 工作原理（简述）

1. **预热**：访问 1–2 个“噪音站点”。
2. **逐字输入计划词**（直接对输入框 `send_keys`，而非队列式 `ActionChains`），必要时点击**受控联想**，否则回车。
3. **结果页就绪**后读取**实际搜索词**：优先 `input#get_attribute("value")`，若失败解析当前 URL 的 `?q=`。([Selenium][1])
4. **跑题纠偏**：若与计划词偏差大，使用 `?q=<planned>` 重新发起搜索。
5. **抽取联想**：收集“相关搜索 + PAA”，去重后入队，驱动下一轮搜索。
6. **人类化交互**：轻度滚动/回拉、短暂停顿、偶尔点开主结果后返回。

---

## 🧪 Quick verify / 快速自检

* Edge 与 msedgedriver 版本是否匹配（前三段号需一致）？([Microsoft Learn][3])
* 你的 `user_data_path` 和驱动路径是否为**真实存在**的本地绝对路径？
* 首轮搜索后，日志中应能看到 **“实际搜索词”** 与 **“计划词”** 的对齐提示。

---

## 📦 Releases & Changelog / 版本与更新记录

* 发布版本建议使用 **注解标签**（annotated tag），并在 GitHub 的 **Releases** 页面启用**自动生成发布说明**（Generate release notes）。([GitHub Docs][5])
* 版本号使用 **Semantic Versioning（语义化版本）**。例如：

  * `MAJOR`（不兼容变更）、`MINOR`（兼容新增）、`PATCH`（兼容修复）。([Semantic Versioning][6])

---

## ⚖️ Ethics & Legal / 合规与提醒

* 请遵守所访问网站与搜索引擎的**服务条款**与**速率限制**，不要用于刷量或干扰性操作。
* 仅用于**学习与研究**；请对目标站点保持礼貌访问频率。
* WebDriver/Edge 的安装与使用以官方文档为准（确保驱动与浏览器版本匹配）。([Microsoft Learn][3])

---

## 🙋 FAQ

* **驱动报错/版本不一致怎么办？**
  进入 `edge://settings/help` 查看版本号，再到 Edge WebDriver 页面下载**相同主版本**的驱动即可。([Microsoft Learn][3])
* **为什么要用 `get_attribute("value")` 读实际搜索词？**
  这是 Selenium 常用、可靠的方式获取输入框当前内容；若 DOM 行为特殊，再回退解析 URL 的 `?q=`。([Selenium][1])
* **移动端脚本是“真手机”吗？**
  它使用 Chromium/Edge 的**设备模拟**（UA + 视口等），方便在桌面环境模拟移动页面渲染与选择器差异。([Chrome for Developers][7])

---

## 🤝 Contributing / 参与

欢迎 PR/Issue：

* Bug 修复：请附**最小复现**与运行环境。
* 选择器/兼容性：移动与桌面 SERP 若有结构变化，欢迎补充多套选择器兜底。
* 文档：欢迎补充中文/英文说明。

