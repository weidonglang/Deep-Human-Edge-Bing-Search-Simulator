import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# [修复] 移除不再使用的 webdriver-manager
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
# 注意：我们不再需要 ActionChains，因为手机模拟使用更直接的 .click()

# 关键词列表（100个，与你提供的一致）
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

# --- 手机模拟核心设置 (保留) ---
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
# ------------------------------------

# --- (S1) 策略一: 使用持久化的浏览器 Profile [移植] ---
user_data_path = r"E:\MyEdgeProfile_Mobile" # 确保路径正确
options.add_argument(f"user-data-dir={user_data_path}")
# ----------------------------------------------------

# --- 核心反检测优化 [移植] ---
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


# [已移除] 不再在全局定义 driver 和 service，移至 main()

def simulate_human_scroll(driver):
    """(升级) 模拟人类的滚动行为，带“回拉”动作"""
    try:
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_times = random.randint(1, 4)
        current_position = 0

        for _ in range(scroll_times):
            # 手机上的“划动”距离比PC短
            scroll_distance = random.randint(100, 350)
            if random.random() < 0.3:  # 30% 概率向上“回拉”
                scroll_distance = -scroll_distance

            if 0 <= current_position + scroll_distance < page_height:
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                current_position += scroll_distance
            else:
                driver.execute_script("window.scrollTo(0, arguments[0]);",
                                      0 if current_position + scroll_distance < 0 else page_height)
                break
            time.sleep(random.uniform(0.5, 1.5))  # 滚动间的停顿
    except Exception as e:
        print(f"滚动时发生错误: {e}")


def simulate_interaction(driver):
    """(S5, S2) [修改] 模拟复杂的页面互动 (手机版)"""
    rand_val = random.random()

    try:
        # --- 25% 概率: (S5) 点击“相关搜索” ---
        if rand_val < 0.25:
            related_links = driver.find_elements(By.CSS_SELECTOR, ".b_rs a")
            if related_links:
                print("    -> (S5) 模拟点按“相关搜索”...")
                link_to_click = random.choice(related_links)
                next_query_text = link_to_click.text  # 获取联想词
                link_to_click.click()
                time.sleep(random.uniform(3, 7))
                return next_query_text  # (S-Chain) 返回联想词

        # --- 25% 概率: (S2) 点击一个主要结果并返回 ---
        elif rand_val < 0.50:  # (0.50 - 0.25 = 25%)
            links = driver.find_elements(By.CSS_SELECTOR, "h2 a")
            if not links:
                return None
            link_to_click = random.choice(links)
            href = link_to_click.get_attribute('href')
            if href and "go.microsoft.com" not in href and "bing.com" not in href:
                print(f"    -> (S2) 模拟点按: {href[:50]}...")
                link_to_click.click()
                time.sleep(random.uniform(4, 8))  # “阅读”
                print("    -> 模拟返回")
                driver.back()
                time.sleep(random.uniform(1, 3))
            else:
                print("    -> (S2) 找到链接但跳过 (广告或内部链接)")
                time.sleep(random.uniform(2, 6))
        # --- 50% 概率: 什么也不做，仅浏览 ---
        else:
            print("    -> 仅滚动和浏览")
            time.sleep(random.uniform(2, 6))

    except Exception as e:
        print(f"    -> 模拟互动时出错: {e}")
        try:
            driver.back()  # 尝试恢复
        except:
            pass
    return None  # 默认不返回联想词


def bing_search(query, driver):
    """(S6) [修改] 执行一次搜索"""
    try:
        driver.get("https://www.bing.com")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sb_form_q"))
        )
        search_box.click() # 模拟点按
        search_box.clear() # 使用 .clear()
        time.sleep(random.uniform(0.2, 0.5)) # 模拟键盘弹起

        # (S6) 模拟打字 (含错误) [移植]
        for char in query:
            if random.random() < 0.03:  # 3% 概率打错
                wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
                search_box.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                search_box.send_keys(Keys.BACKSPACE) # 修正
                time.sleep(random.uniform(0.05, 0.2))
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2)) # 模拟按键间隔

        search_box.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a"))
        )
        simulate_human_scroll(driver)
        # 执行互动，并将其返回值（可能是联想词）传递回去
        return simulate_interaction(driver)

    except Exception as e:
        print(f"搜索 {query} 时发生错误: {e}")
        return None  # S-Chain 逻辑：发生错误时，不返回联想词


def main():
    driver = None # [新增] 在 try 块之外初始化 driver
    try:
        # --- [修复] 切换回“手动” WebDriver 路径 ---
        # 确保 E:\WebDriver\msedgedriver.exe 是你刚下载的、版本匹配的文件
        try:
            print("正在启动 WebDriver (使用手动路径)...")
            # [修复] 改回你最初的 Service 定义，并加上 'r'
            service = Service(r"E:\WebDriver\msedgedriver.exe")
            driver = webdriver.Edge(service=service, options=options)
            print("WebDriver 启动成功。")
        except Exception as e:
            print(f"WebDriver 启动失败: {e}")
            print("请确保：1. E:\WebDriver\msedgedriver.exe 路径正确。 2. 驱动版本与你的Edge浏览器版本 *完全* 匹配。")
            return # 无法启动，退出 main
        # ---------------------------------

        # (S7) “预热”，访问 1-2 个噪音网站 [移植]
        noise_sites = [
            "https://www.baidu.com", "https://blog.csdn.net/",
            "https://www.jd.com/", "https://www.taobao.com/", "https://www.msn.cn/"
        ]
        print("(S7) 启动“预热”，访问 1-2 个噪音网站...")
        for _ in range(random.randint(1, 2)):
            try:
                site = random.choice(noise_sites)
                print(f"    ...噪音访问: {site}...")
                driver.get(site)
                time.sleep(random.uniform(4, 9))
            except Exception as e:
                print(f"    噪音访问 {site} 失败: {e}")

        # [修改] 设置为移动端的目标搜索次数
        total_searches = random.randint(23, 25)
        print(f"计划执行 {total_searches} 次 *移动端* 搜索...")

        # (S-Chain) "搜索联想链" 策略的起始变量 [移植]
        next_query = None

        for i in range(total_searches):
            # (S-Chain) 核心逻辑 [移植]
            if next_query:
                keyword = next_query
                print(f"    -> (S-Chain) 延续上一步搜索: {keyword}")
                next_query = None
            else:
                keyword = random.choice(keywords)

            print(f"执行第 {i + 1} / {total_searches} 次 *移动端* 搜索: {keyword}")
            # (S-Chain) 接收 bing_search 可能返回的“联想词” [移植]
            next_query = bing_search(keyword, driver)

            # (S4) “思考时间” 和 “长暂停” [移植]
            sleep_time = random.uniform(5, 15)
            print(f"    ...搜索完成，休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

            if random.random() < 0.05:  # 5% 概率
                # [修复] 按照你的偏好，改回 6-18 秒
                distraction_time = random.uniform(6, 18)
                print(f"    -> (S4) 模拟分心，长暂停 {distraction_time:.1f} 秒...")
                time.sleep(distraction_time)

        print(f"已完成 {total_searches} 次 *移动端* 搜索！")

        # (S7) “冷却”，在结束前再访问一个网站 [移植]
        try:
            site = random.choice(noise_sites)
            print(f"(S7) 搜索结束，“冷却”访问: {site}...")
            driver.get(site)
            time.sleep(random.uniform(3, 5))
        except Exception as e:
            print(f"    噪音访问 {site} 失败: {e}")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver: # [新增] 确保 driver 成功初始化后再退出
            print("关闭浏览器。")
            driver.quit()
        else:
            print("Driver 未能成功启动。")


if __name__ == "__main__":
    main()