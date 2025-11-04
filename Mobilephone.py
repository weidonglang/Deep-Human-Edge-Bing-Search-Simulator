# Mobilephone.py
import time
import random
import re
from collections import deque
from urllib.parse import urlparse, parse_qs, quote_plus

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service

# ========================= 可调开关 =========================
STRICT_AUTOCOMPLETE = True              # 只点与前缀相关的下拉联想（避免“趋势词”误点）
MIN_PREFIX_FOR_AUTOCOMPLETE = 3         # 前缀不足3个字符不点联想
ENFORCE_PLANNED_IF_DRIFT = True         # 若实际词明显偏离计划词，强制纠偏到计划词
QUEUE_LIMIT = 120                       # 联想队列上限
# ==========================================================

# 关键词列表
keywords = [
    # Retail & Seasonal
    "11.11 deals 2025","618 shopping festival deals","Prime Day 2025 deals",
    "back to school laptop deals","student discounts electronics",
    "refurbished laptops warranty","price tracking tools",
    "compare SSD vs HDD 2025","USB-C power bank 100W","noise cancelling earbuds under $100",
    "sustainable fashion brands","men’s capsule wardrobe 2025","winter jackets waterproof ratings",
    "skincare routine for oily skin","sneaker resale market trends","international size guide",

    # Home & Appliances
    "energy efficient washing machines 2025","robot vacuum comparison","air purifier HEPA vs H13",
    "smart lighting starter kit","induction cooktop buying guide","espresso machine under $500",
    "dishwasher decibel levels","home projector short throw",

    # Travel Planning
    "visa-free countries for Chinese passport 2025","Schengen visa appointment tips",
    "best time to visit Japan","JR Pass alternatives","travel SIM vs eSIM 2025",
    "airport lounge access cards","travel packing checklist","travel scams to avoid",
    "city pass comparison Europe","rainy season travel tips Southeast Asia",

    # Outdoor & Camping
    "ultralight backpacking gear list","waterproof rating explained","best tent for 4 people",
    "hiking GPS vs offline maps","portable solar panel camping","bear canister requirements",

    # News & Geopolitics
    "central bank rate decisions 2025","semiconductor supply chain news","climate tech investments 2025",
    "conflict analysis explained","fact-check tools list","energy storage policy updates","AI governance framework 2025",

    # Education & Career
    "SOP writing tips grad school","machine learning roadmap 2025","coding interview prep roadmap",
    "IELTS vs TOEFL comparison 2025","scholarship statement sample","research paper reading strategies",
    "LaTeX thesis template","citation managers comparison","Coursera vs edX vs Udemy 2025","study abroad budget planning",

    # Health & Fitness
    "high protein meal prep","intermittent fasting schedule","HIIT workouts at home",
    "posture correction exercises","creatine monohydrate guide","smartwatch fitness accuracy",
    "running cadence tips","sleep hygiene checklist",

    # Entertainment & Media
    "indie games hidden gems 2025","4K streaming bitrate comparison","Dolby Atmos setup guide",
    "anime season chart 2025","film festival submissions","board games for beginners",
    "podcast microphone under $200","game pass vs buy to own",

    # Tech & Gadgets
    "Wi-Fi 7 routers 2025","USB4 v2 explained","Bluetooth LE Audio earbuds","Matter smart home standard",
    "foldable phones durability","LLM tools for students","RISC-V dev boards 2025","microLED vs OLED",
    "NAS setup home 2.5GbE","cloud storage encryption",

    # Cybersecurity & Privacy
    "password manager comparison","2FA authenticator apps","phishing email examples",
    "VPN split tunneling explained","data breach checker","privacy friendly browsers",

    # Local & Everyday
    "best cafes near me laptop-friendly","weekend markets schedule","public transport cards guide",
    "recycling rules city","pet adoption process","home cleaning services","emergency clinics near me","phone repair same day",

    # Finance & Jobs
    "ETF dollar-cost averaging 2025","high-yield savings accounts","credit score improvement tips",
    "salary negotiation email","resume ATS keywords CS","freelance contract template","tax residency rules expats",
    "index funds vs active funds",

    # Automotive & EV
    "EV charging networks map","LFP vs NMC battery","used car inspection checklist",
    "third-party vs comprehensive insurance","tire size calculator","heat pump efficiency EV",

    # Photography & Imaging
    "mirrorless cameras 2025","prime vs zoom lenses","color grading LUTs free",
    "astrophotography settings","drone regulations 2025","RAW vs HEIF vs JPEG",

    # Food & Kitchen
    "air fryer recipes healthy","meal kit delivery comparison","specialty coffee beans guide",
    "sous vide beginner guide","knife sharpening angles",

    # Productivity & PKM
    "second brain note taking","time blocking template","PKM tools comparison 2025",
    "markdown editors list","read it later apps","Zettelkasten workflow",

    # ---------------- 中文 ----------------
    "2025年双十一购物优惠","618年中大促优惠","2025年Prime会员日优惠","开学季笔记本优惠",
    "学生电子产品优惠","官翻笔记本保修政策","价格跟踪工具","2025年SSD与HDD对比",
    "100W USB-C 移动电源","百美元内降噪耳机","可持续时尚品牌","2025男士胶囊衣橱",
    "冬季外套防水等级","油皮护肤步骤","球鞋转售市场趋势","国际尺码对照表",

    "2025节能洗衣机","扫地机器人对比","空气净化器HEPA与H13","智能照明入门套装",
    "电磁炉选购指南","500美元以下咖啡机","洗碗机噪音分贝对比","家用短焦投影仪",

    "2025中国护照免签国家","申根签证预约技巧","日本最佳旅行季节","日本通票替代方案",
    "2025旅游实体卡与eSIM对比","机场贵宾厅信用卡攻略","旅行打包清单","旅行常见骗局",
    "欧洲城市通票对比","东南亚雨季出行建议",

    "超轻徒步装备清单","防水等级IPX说明","四人帐篷推荐","徒步GPS与离线地图对比","露营便携太阳能板","防熊罐使用要求",

    "2025央行利率决议","半导体供应链新闻","2025气候科技投资","国际冲突解析",
    "事实核查工具清单","储能政策动态","2025人工智能治理框架",

    "研究生申请SOP写作要点","2025机器学习学习路线","编程面试准备路线图","2025雅思与托福对比","奖学金申请陈述范文",
    "论文精读方法","LaTeX论文模板","文献管理工具对比","2025在线课程平台对比","留学预算规划",

    "高蛋白备餐","间歇性断食时间表","家庭HIIT训练","体态矫正训练","肌酸一水补剂指南",
    "智能手表运动数据准确性","跑步步频技巧","睡眠卫生清单",

    "2025独立游戏冷门佳作","4K流媒体码率对比","杜比全景声设置指南","2025动画新番导览",
    "电影节投稿指南","桌游入门推荐","200美元内播客麦克风","订阅制与买断制对比",

    "2025年Wi-Fi 7路由器","USB4 v2 技术解析","低功耗蓝牙音频耳机","Matter智能家居标准","折叠屏手机耐用性",
    "学生用大语言模型工具","2025年RISC-V开发板","MicroLED与OLED对比","家用NAS与2.5G网卡配置","云存储加密方案",

    "密码管理器对比","双重验证应用推荐","钓鱼邮件示例","VPN分流原理解析","数据泄露查询工具","注重隐私的浏览器",

    "附近适合办公的咖啡馆","周末市集时间表","公共交通卡使用指南","城市垃圾分类规则","宠物领养流程","家政保洁服务",
    "附近急诊诊所","当日手机维修",

    "2025ETF定投","高收益储蓄账户","信用分提升技巧","薪资谈判邮件模板","计算机专业简历ATS关键词",
    "自由职业合同模板","海外税务居民规则","指数基金与主动基金对比",

    "电动车充电网络地图","LFP与NMC电池对比","二手车检查清单","交强险与商业全险对比","轮胎尺寸计算器","电车热泵效率",

    "2025无反相机推荐","定焦与变焦镜头对比","免费调色LUT资源","星野摄影参数设置","2025无人机法规","RAW/HEIF/JPEG对比",

    "空气炸锅健康食谱","生鲜配餐对比","精品咖啡豆选购指南","低温慢煮入门指南","厨刀开刃角度",

    "第二大脑笔记法","时间块模板","2025知识管理工具对比","Markdown编辑器清单","稍后读应用","卡片盒笔记工作流",
]


# --- 手机模拟核心设置 ---
options = webdriver.EdgeOptions()
mobile_user_agent = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 6 Build/AP2A.240605.024) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36 Edge/121.0.2277.138"
)
options.add_argument(f"user-agent={mobile_user_agent}")
options.add_experimental_option("mobileEmulation", {
    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    "userAgent": mobile_user_agent
})

# (S1) 使用持久化 Profile
user_data_path = r"E:\MyEdgeProfile_Mobile"  # 替换为你的真实路径
options.add_argument(f"user-data-dir={user_data_path}")

# 反检测优化
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ============================ 工具函数 ============================
def simulate_human_scroll(driver):
    """模拟手机端滚动（含回拉）"""
    try:
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_times = random.randint(1, 4)
        current_position = 0
        for _ in range(scroll_times):
            dist = random.randint(100, 350)
            if random.random() < 0.3:
                dist = -dist
            if 0 <= current_position + dist < page_height:
                driver.execute_script(f"window.scrollBy(0, {dist});")
                current_position += dist
            else:
                driver.execute_script(
                    "window.scrollTo(0, arguments[0]);",
                    0 if current_position + dist < 0 else page_height
                )
                break
            time.sleep(random.uniform(0.5, 1.5))
    except Exception as e:
        print(f"滚动时发生错误: {e}")

def _type_slowly(search_box, text):
    """逐字输入到搜索框（手机端，直接 send_keys）"""
    typed = ""
    for ch in text:
        if random.random() < 0.03:  # 3% 概率输错并退格
            wrong = random.choice("abcdefghijklmnopqrstuvwxyz")
            search_box.send_keys(wrong)
            time.sleep(random.uniform(0.08, 0.2))
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.05, 0.15))
        search_box.send_keys(ch)
        typed += ch
        time.sleep(random.uniform(0.05, 0.18))
    return typed

def pick_autocomplete_if_any(driver, prefix, prefer_ratio=0.45,
                             min_prefix=MIN_PREFIX_FOR_AUTOCOMPLETE,
                             strict=STRICT_AUTOCOMPLETE):
    """
    若有下拉联想，按概率点击其中一个并触发搜索；返回被点击文本，否则 None。
    仅在 prefix 足够长时启用；strict=True 时只点“以 prefix 开头/包含 prefix”的项。
    """
    try:
        if len(prefix.strip()) < min_prefix or random.random() > prefer_ratio:
            return None

        # 等待联想渲染（手机端略慢）
        time.sleep(random.uniform(0.25, 0.6))

        # 多套选择器以适配 Bing 移动版
        selectors = [
            "#sa_ul li",             # 常见
            "li.sa_sg",              # 变体
            ".sa_as li",             # 旧版
            '[role=\"listbox\"] [role=\"option\"]',  # 无障碍语义
        ]
        items = []
        for sel in selectors:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                items = els
                break
        if not items:
            return None

        prefix_l = prefix.strip().lower()
        cands = []
        for el in items:
            t = (el.text or "").strip()
            if not t:
                continue
            t_l = t.lower()
            if not strict or t_l.startswith(prefix_l) or (prefix_l in t_l):
                cands.append((el, t))

        if not cands:
            return None

        el, text = random.choice(cands)
        el.click()  # 手机端直接 tap
        time.sleep(random.uniform(2, 4))
        print(f"    -> (AC) 点击下拉联想：{text}")
        return text
    except Exception as e:
        print(f"Autocomplete 选择失败: {e}")
        return None

def collect_related_terms_on_page(driver):
    """
    汇集联想词：相关搜索 / 相关问题(PAA) / 拼写纠错 等
    """
    related = set()
    try:
        # 相关搜索（多容器兜底）
        for sel in [".b_rs a", ".b_rsList a", "#b_context .b_rs a", ".b_vList a"]:
            for a in driver.find_elements(By.CSS_SELECTOR, sel):
                t = a.text.strip()
                if t:
                    related.add(t)

        # People also ask / 相关问题（手机端标题文案可能不同）
        paa_heads = driver.find_elements(
            By.XPATH,
            "//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'people also ask') "
            " or contains(., '相关问题') or contains(., '其他人还会问') or contains(., '人们也会问')]"
        )
        for head in paa_heads:
            for el in head.find_elements(By.XPATH, "following::li[.//a or .//button][position()<=8]"):
                t = el.text.strip()
                if t and len(t) <= 80:
                    related.add(t)

        # 拼写纠错（Did you mean / 你是否要找）
        for el in driver.find_elements(
            By.XPATH,
            "//*[contains(., 'Did you mean') or contains(., '你是否要找') or contains(., '你是不是要找')]//a"
        ):
            t = el.text.strip()
            if t:
                related.add(t)

    except Exception as e:
        print(f"收集联想词失败: {e}")

    return list(related)

def simulate_interaction(driver):
    """
    页面互动（手机版）：
      - 35%：从页面联想池挑一个（若可点击则阅读，否则返回词）
      - 20%：点一个主要结果并返回
      - 其余：只滚动浏览
    返回:
        - string: 选中的“联想词”（给下一轮）
        - None: 不切换 query
    """
    rand_val = random.random()
    try:
        if rand_val < 0.35:
            pool = collect_related_terms_on_page(driver)
            if pool:
                term = random.choice(pool)
                print(f"    -> (Relate) 选择联想词: {term}")
                # 尝试点击同文本链接
                links = driver.find_elements(By.LINK_TEXT, term)
                if links:
                    links[0].click()
                    time.sleep(random.uniform(3, 6))
                    return None
                return term

        elif rand_val < 0.55:
            links = driver.find_elements(By.CSS_SELECTOR, "h2 a")
            if links:
                link = random.choice(links)
                href = link.get_attribute('href') or ''
                if href and "bing.com" not in href and "go.microsoft.com" not in href:
                    print(f"    -> (Click) 打开结果：{href[:60]}...")
                    link.click()
                    time.sleep(random.uniform(4, 8))
                    print("    -> 返回结果页")
                    driver.back()
                    time.sleep(random.uniform(1, 3))
        else:
            time.sleep(random.uniform(2, 6))

    except Exception as e:
        print(f"    -> 模拟互动时出错: {e}")
        try:
            driver.back()
        except:
            pass

    return None

def _read_actual_query(driver):
    """优先从输入框 value 读实际搜索词；失败则从 URL 的 ?q= 读取。"""
    # input 的当前值用 get_attribute('value') 读取；URL 的 q 是查询参数
    try:
        box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "sb_form_q")))
        val = (box.get_attribute("value") or "").strip()
        if val:
            return val
    except Exception:
        pass
    try:
        parsed = urlparse(driver.current_url)
        q = (parse_qs(parsed.query).get("q", [""])[0] or "").strip()
        if q:
            return q
    except Exception:
        pass
    return ""

def _is_drift(planned: str, actual: str) -> bool:
    """判断实际词是否明显偏离计划词（中英混合的简单启发式）"""
    if not actual:
        return False
    p = planned.strip().lower()
    a = actual.strip().lower()
    if p == a:
        return False
    # 前缀/包含
    if len(p) >= 3 and (p[:3] in a or a[:3] in p):
        return False
    if p in a or a in p:
        return False
    # 英文 token 相似度
    p_tokens = [t for t in re.findall(r"\w+", p) if len(t) >= 3]
    a_tokens = [t for t in re.findall(r"\w+", a) if len(t) >= 3]
    if p_tokens and a_tokens:
        inter = len(set(p_tokens) & set(a_tokens))
        base = min(len(set(p_tokens)), len(set(a_tokens)))
        if base and (inter / base) >= 0.34:
            return False
    return True

# ============================ 搜索主流程 ============================
def bing_search(query, driver):
    """
    1) 打开 Bing -> 清空 -> 逐字输入
    2) 仅当前缀>=MIN_PREFIX_FOR_AUTOCOMPLETE 时，才尝试“与前缀相关”的自动补全；否则直接回车
    3) 结果页就绪 -> 读取“实际搜索词”；若跑题且允许纠偏，则强制以计划词搜索
    4) 滚动 + 页面互动
    返回: (next_term, actual_query)
    """
    actual_query = ""
    try:
        driver.get("https://www.bing.com")
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sb_form_q")))
        search_box.click()
        # 清空
        search_box.clear()
        time.sleep(random.uniform(0.2, 0.5))

        # 逐字输入
        prefix = _type_slowly(search_box, query)

        # 确认输入框已持有我们刚打的前缀（轻微防抖）
        try:
            WebDriverWait(driver, 2).until(
                lambda d: d.find_element(By.ID, "sb_form_q").get_attribute("value") and
                          d.find_element(By.ID, "sb_form_q").get_attribute("value").strip()[:len(prefix)] == prefix[:len(prefix)]
            )
        except Exception:
            pass  # 不阻断

        # 尝试点“与前缀相关”的下拉联想；未点击则直接回车
        picked = pick_autocomplete_if_any(driver, prefix=prefix)
        if not picked:
            search_box.send_keys(Keys.RETURN)

        # 等结果页元素出现
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a")))

        # 读取“实际搜索词”
        actual_query = _read_actual_query(driver)

        # 纠偏：若明显偏离计划词，强制以计划词检索
        if ENFORCE_PLANNED_IF_DRIFT and _is_drift(query, actual_query):
            print(f"    -> (Correct) 实际词偏离计划词，纠偏到计划词：{query}")
            driver.get("https://www.bing.com/search?q=" + quote_plus(query))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a")))
            actual_query = _read_actual_query(driver)

        # 浏览与互动
        simulate_human_scroll(driver)
        next_term = simulate_interaction(driver)

        return next_term, actual_query

    except Exception as e:
        print(f"搜索 {query} 时发生错误: {e}")
        return None, actual_query

def main():
    driver = None
    try:
        # 启动 WebDriver（手动路径）
        print("正在启动 WebDriver (使用手动路径)...")
        service = Service(r"E:\WebDriver\msedgedriver.exe")  # 替换为你的驱动路径
        driver = webdriver.Edge(service=service, options=options)
        print("WebDriver 启动成功。")

        # 预热（1-2个噪音站）
        noise_sites = [
            "https://www.baidu.com", "https://blog.csdn.net/",
            "https://www.jd.com/", "https://www.taobao.com/", "https://www.msn.cn/"
        ]
        print("(S7) 启动预热，访问 1-2 个噪音网站...")
        for _ in range(random.randint(1, 2)):
            try:
                site = random.choice(noise_sites)
                print(f"    ...噪音访问: {site}...")
                driver.get(site)
                time.sleep(random.uniform(4, 9))
            except Exception as e:
                print(f"    噪音访问 {site} 失败: {e}")

        total_searches = random.randint(23, 25)
        print(f"计划执行 {total_searches} 次 *移动端* 搜索...")

        visited = set()
        queue = deque()

        next_query = None
        for i in range(total_searches):
            if next_query:
                planned = next_query
                print(f"    -> (S-Chain) 延续上一步联想: {planned}")
                next_query = None
            elif queue:
                planned = queue.popleft()
                print(f"    -> (Queue) 使用队列联想: {planned}")
            else:
                planned = random.choice(keywords)

            print(f"执行第 {i + 1} / {total_searches} 次 *移动端* 搜索: {planned}")
            next_term, actual_query = bing_search(planned, driver)

            if actual_query and actual_query != planned:
                print(f"    -> 实际搜索词: {actual_query}")

            used_for_dedup = actual_query or planned
            visited.add(used_for_dedup)

            # 页面联想批量入队
            try:
                pool = collect_related_terms_on_page(driver)
                random.shuffle(pool)
                for t in pool[:random.randint(2, 5)]:
                    if t not in visited and t not in queue:
                        queue.append(t)
                while len(queue) > QUEUE_LIMIT:
                    queue.pop()
            except Exception as e:
                print(f"收集并入队失败: {e}")

            # 明确联想词优先
            if next_term and next_term not in visited and next_term not in queue:
                queue.appendleft(next_term)

            # 休息 / 分心
            sleep_time = random.uniform(5, 15)
            print(f"    ...搜索完成，休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)
            if random.random() < 0.05:
                distraction_time = random.uniform(6, 18)
                print(f"    -> (S4) 模拟分心，长暂停 {distraction_time:.1f} 秒...")
                time.sleep(distraction_time)

        print(f"已完成 {total_searches} 次 *移动端* 搜索！")

        # 冷却
        try:
            site = random.choice(noise_sites)
            print(f"(S7) 搜索结束，冷却访问: {site}...")
            driver.get(site)
            time.sleep(random.uniform(3, 5))
        except Exception as e:
            print(f"    噪音访问 {site} 失败: {e}")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver:
            print("关闭浏览器。")
            driver.quit()
        else:
            print("Driver 未能成功启动。")

if __name__ == "__main__":
    main()