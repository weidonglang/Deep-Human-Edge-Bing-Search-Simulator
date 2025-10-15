import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains

# 关键词列表（保持不变）
keywords = [
    # ... (100个关键词列表，与你提供的一致)
    "Best laptops 2025", "Smartphone deals", "Fashion trends women", "Online shopping discounts",
    "Gaming console prices", "Home appliance reviews", "Sneaker brands", "Luxury watches",
    "Budget headphones", "Furniture sales", "Electronics deals", "Black Friday 2025",
    "Amazon best sellers", "Tech gadgets 2025", "Winter clothing trends", "Jewelry gift ideas",
    "Top travel destinations", "Cheap flights 2025", "Hotel booking tips", "Beach vacation ideas",
    "City break Europe", "Adventure travel packages", "Cruise deals 2025", "Travel insurance comparison",
    "Camping gear reviews", "Best hiking trails", "Family vacation spots", "Solo travel tips",
    "Backpacking destinations", "Luxury resorts Asia", "Travel safety tips", "Road trip ideas",
    "Breaking news today", "World news updates", "US election 2025", "Global economy trends",
    "Climate change solutions", "Political debates 2025", "International conflicts", "Tech industry updates",
    "Stock market predictions", "Health policy news", "Space mission updates", "Energy crisis 2025",
    "Online courses free", "Best coding bootcamps", "Study abroad programs", "Scholarship opportunities",
    "Academic research tools", "Math learning apps", "History documentaries", "Science podcasts",
    "University rankings 2025", "Career training programs", "Language learning tips", "STEM resources",
    "Weight loss diets", "Home workout routines", "Mental health tips", "Meditation apps",
    "Healthy meal plans", "Fitness equipment reviews", "Yoga for beginners", "Nutrition supplements",
    "Running shoes reviews", "Stress management techniques", "Sleep improvement tips", "Vegan recipes easy",
    "New movie releases", "TV show reviews 2025", "Music festivals 2025", "Book recommendations",
    "Streaming service deals", "Celebrity news today", "Top video games 2025", "Art exhibitions",
    "Theater shows 2025", "Pop music charts", "Comedy specials Netflix", "Cultural events near me",
    "Smart home devices 2025", "Wearable tech reviews", "Electric car prices", "AI innovations",
    "5G network updates", "Virtual reality headsets", "Drone technology", "Cybersecurity tips",
    "Tech startups 2025", "Cloud storage comparison", "Programming tutorials", "Data privacy laws",
    "Local weather forecast", "Event planning ideas", "DIY craft projects", "Pet adoption near me",
    "Gardening for beginners", "Car maintenance tips", "Home renovation ideas", "Wedding planning guide",
    "Photography gear reviews", "Best coffee machines", "Restaurant reviews near me", "Online grocery delivery",
    "Real estate trends 2025", "Job search websites", "Personal finance apps", "Charity organizations"
]

# 准备一组真实的 Edge User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.0.0"
]

# 设置 Edge 浏览器选项
options = webdriver.EdgeOptions()

# --- (S1) 策略一: 使用持久化的浏览器 Profile ---
# ！！重要！！: 请将下面的路径替换为你电脑上的一个真实文件夹路径！
# 例如: "C:\\Users\\你的用户名\\MyEdgeProfile" (注意双反斜杠)
user_data_path = "E:\\MyEdgeProfile"
options.add_argument(f"user-data-dir={user_data_path}")
# ----------------------------------------------------

# --- 核心反检测优化 ---
options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 你的驱动路径
service = Service(r"E:\WebDriver\msedgedriver.exe")
driver = webdriver.Edge(service=service, options=options)

# --- (S-JS) 进阶策略: 深化JS指纹隐藏 ---
# 在浏览器实例创建后，立即执行JS来修改多个检测点
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        // 1. 隐藏 webdriver 标志 (你已有的)
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        });

        // 2. 伪装 Chrome 运行时
        window.chrome = window.chrome || {};
        window.chrome.app = { "isInstalled": false };
        window.chrome.runtime = { "id": "abcdefghijklmno" };

        // 3. 伪装权限状态
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: 'prompt' }) : // 假装总是 'prompt'
                originalQuery(parameters)
        );

        // 4. 伪装插件长度 (自动化环境下通常为 0)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3], // 伪造一个非0数组
        });
    """
})

# 5. 随机化浏览器窗口大小 (保留)
width = random.randint(1280, 1920)
height = random.randint(720, 1080)
driver.set_window_size(width, height)


def simulate_human_scroll(driver):
    """模拟人类的滚动行为（传入 driver）"""
    try:
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_times = random.randint(1, 4)
        current_position = 0

        for _ in range(scroll_times):
            scroll_distance = random.randint(100, 500)
            if random.random() < 0.3:  # 30% 概率向上滚动
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
    """
    (S5, S2, S-Highlight)
    模拟复杂的页面互动，并返回一个“联想词”（如果有的话）

    返回:
        - string: 如果点击了“相关搜索”，返回该词条
        - None: 如果执行了其他操作
    """
    # 决定执行哪种操作
    rand_val = random.random()

    try:
        # --- 20% 概率: (S5) 点击“相关搜索” ---
        if rand_val < 0.20:
            related_links = driver.find_elements(By.CSS_SELECTOR, ".b_rs a")
            if related_links:
                print("    -> (S5) 模拟点击“相关搜索”...")
                link_to_click = random.choice(related_links)
                next_query_text = link_to_click.text  # 获取联想词

                actions = ActionChains(driver)
                actions.move_to_element(link_to_click).pause(random.uniform(0.5, 1.2)).click().perform()

                time.sleep(random.uniform(3, 7))
                return next_query_text  # (S-Chain) 返回联想词

        # --- 15% 概率: (S-Highlight) 模拟高亮“阅读” ---
        elif rand_val < 0.35:  # (0.35 - 0.20 = 15%)
            # 尝试在搜索结果的描述文字上高亮
            targets = driver.find_elements(By.CSS_SELECTOR, ".b_caption p, .b_algoDesc")
            if targets:
                target_text = random.choice(targets)
                if target_text.is_displayed():
                    print("    -> (S-Highlight) 模拟高亮文本...")
                    actions = ActionChains(driver)
                    actions.move_to_element(target_text).pause(0.5) \
                        .click_and_hold().move_by_offset(random.randint(50, 150), 0) \
                        .release().perform()
                    time.sleep(random.uniform(1, 3))

        # --- 15% 概率: (S2) 点击一个主要结果并返回 ---
        elif rand_val < 0.50:  # (0.50 - 0.35 = 15%)
            links = driver.find_elements(By.CSS_SELECTOR, "h2 a")
            if not links:
                return None

            link_to_click = random.choice(links)
            href = link_to_click.get_attribute('href')

            if href and "go.microsoft.com" not in href and "bing.com" not in href:
                print(f"    -> (S2) 模拟点击: {href[:50]}...")

                actions = ActionChains(driver)
                actions.move_to_element(link_to_click).pause(random.uniform(0.5, 1.5)).click().perform()

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
    """
    (S2, S6)
    执行一次搜索，包含模拟打字、错误修正，并返回互动结果
    """
    try:
        driver.get("https://www.bing.com")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sb_form_q"))
        )

        # (S2) 模拟清空
        actions = ActionChains(driver)
        actions.move_to_element(search_box).click().pause(0.3).key_down(Keys.CONTROL).send_keys('a').key_up(
            Keys.CONTROL).send_keys(Keys.DELETE).perform()

        # (S6) 模拟打字 (含错误)
        actions = ActionChains(driver).move_to_element(search_box)
        for char in query:
            if random.random() < 0.03:  # 3% 概率打错
                wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
                actions.send_keys(wrong_char).pause(random.uniform(0.1, 0.3))
                actions.send_keys(Keys.BACKSPACE).pause(random.uniform(0.05, 0.2))  # 修正

            actions.send_keys(char).pause(random.uniform(0.05, 0.2))

        actions.send_keys(Keys.RETURN).perform()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a"))
        )

        simulate_human_scroll(driver)

        # 执行互动，并将其返回值（可能是联想词）传递回去
        return simulate_interaction(driver)

    except Exception as e:
        print(f"搜索 {query} 时发生错误: {e}")
        return None  # 发生错误时，不返回联想词


def main():
    try:
        # (S7) “预热”，访问 1-2 个噪音网站
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

        total_searches = random.randint(34, 36)  # 按你要求，保留原范围
        print(f"计划执行 {total_searches} 次电脑端搜索...")

        # (S-Chain) "搜索联想链" 策略的起始变量
        next_query = None

        for i in range(total_searches):

            # (S-Chain) 核心逻辑: 检查是否有“联想词”
            if next_query:
                keyword = next_query
                print(f"    -> (S-Chain) 延续上一步搜索: {keyword}")
                next_query = None  # 用过一次后就清空
            else:
                keyword = random.choice(keywords)  # 否则从列表随机选

            print(f"执行第 {i + 1} / {total_searches} 次搜索: {keyword}")

            # (S-Chain) 接收 bing_search 可能返回的“联想词”
            next_query = bing_search(keyword, driver)

            # (S4) “思考时间” 和 “长暂停”
            sleep_time = random.uniform(5, 15)
            print(f"    ...搜索完成，休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

            if random.random() < 0.05:  # 5% 概率
                distraction_time = random.uniform(6, 18)  # 摸鱼一会儿
                print(f"    -> (S4) 模拟分心，长暂停 {distraction_time:.1f} 秒...")
                time.sleep(distraction_time)

        print(f"已完成 {total_searches} 次电脑端搜索！")

        # (S7) “冷却”，在结束前再访问一个网站
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
        print("关闭浏览器。")
        driver.quit()


if __name__ == "__main__":
    main()