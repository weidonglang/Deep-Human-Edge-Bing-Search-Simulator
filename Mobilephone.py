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

# 关键词列表（保持你的原始100项）
keywords = [
    "Python programming", "AI technology", "Machine learning", "Data science", "Web development",
    "Cloud computing", "Cybersecurity", "Blockchain", "Quantum computing", "Big data",
    "Artificial intelligence", "Deep learning", "Software engineering", "DevOps", "Mobile apps",
    "Game development", "Network security", "Database management", "API integration", "Microservices",
    "Computer vision", "Natural language processing", "Robotics", "IoT devices", "5G technology",
    "Augmented reality", "Virtual reality", "Edge computing", "Serverless architecture", "Fintech",
    "Cryptocurrency", "Digital transformation", "Agile methodology", "Selenium automation", "Bing rewards",
    "Cloud security", "Web3", "Data analytics", "Neural networks", "Kubernetes", "Docker containers",
    "Cybersecurity trends", "Generative AI", "Low-code platforms", "Quantum cryptography",
    "Latest movies 2025", "Music streaming services", "Top Netflix shows", "Hollywood news",
    "Video game releases", "Pop culture trends", "Celebrity interviews", "Anime recommendations",
    "Streaming platforms comparison", "Oscar predictions 2025", "K-pop trends", "Virtual concerts",
    "Football highlights", "Basketball NBA news", "Olympics 2024 updates", "Tennis rankings",
    "Soccer World Cup", "Sports betting trends", "Fitness training tips", "Marathon training",
    "Healthy recipes", "Sustainable living", "Minimalist lifestyle", "Travel destinations 2025",
    "Home decor ideas", "Personal finance tips", "Mental health awareness", "Yoga benefits",
    "Vegan diet plans", "DIY home projects", "Eco-friendly products", "Budget travel tips",
    "Global news today", "Climate change updates", "Economic trends 2025", "International politics",
    "Tech industry news", "Stock market analysis", "World health organization updates",
    "Renewable energy trends", "Geopolitical events", "Space exploration news",
    "Online learning platforms", "Free coding tutorials", "Language learning apps",
    "STEM education trends", "Virtual classrooms", "Best universities 2025",
    "Weather forecast", "Local events near me", "Photography tips", "Pet care advice",
    "Gardening tips", "Electric vehicles 2025", "Smart home devices", "Fashion trends 2025",
    "Food delivery apps", "Virtual reality gaming", "Productivity tools", "Remote work tips",
    "Cryptocurrency prices", "Artificial intelligence ethics", "Space tourism", "Fitness trackers"
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
