import requests
import openai
import pyautogui
import json
import base64
import time

# API 設定
SERVER_URL = "http://0.0.0.0:8008/parse/"  # OmniParser API
GPT4O_API_KEY = ""  # GPT-4o API Key

def parse_document(image_path):
    """ 使用 OmniParser API 解析圖片 """
    with open(image_path, "rb") as img_file:
        img_file_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    payload = {"base64_image": img_file_base64}
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(SERVER_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # 回傳 JSON 結果
    else:
        print("解析失敗:", response.text)
        return None

def save_image_from_base64(base64_str, output_path="output.jpg"):
    """ 解析 Base64 字串並存成圖片 """
    img_data = base64.b64decode(base64_str)
    with open(output_path, "wb") as img_file:
        img_file.write(img_data)
    print(f"✅ 解析後的圖片已儲存為 {output_path}")

def decide_click_target(btn_desc,parsed_result):
    """ 使用 GPT-4o 判斷要點擊的按鈕 """
    client = openai.OpenAI(api_key=GPT4O_API_KEY)

    prompt = f"""
    以下是 OCR 解析的內容：
    {json.dumps(parsed_result, indent=2)}

    你的任務是找出最可能需要點擊的按鈕，並回傳 JSON 格式：
    - 如果有座標 (x, y)，請回傳：`{{"id": "[id] icon", "button": "按鈕名稱", "coordinates": [x, y]}}`
    - 如果沒有座標，請回傳：`{{"button": "按鈕名稱"}}`
    - 如果找不到按鈕，請回傳：`{{"button": null}}`
    
    點擊描述: {btn_desc}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一個 UI 操作助手，專門分析 OCR 結果並找出需要點擊的按鈕。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def click_target(click_data):
    """ 解析 GPT-4o 回傳的 JSON，並執行點擊動作 """
    try:
        data = json.loads(click_data)  # 解析 JSON 格式
        if data.get("coordinates"):
            x, y = data["coordinates"]
            print(f"移動滑鼠到 ({x}, {y}) 並點擊")
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
        else:
            print(f"找不到座標，無法點擊 [{data.get('button', '未知按鈕')}]")
    except Exception as e:
        print("點擊失敗:", e)

def main():
    image_path = "12BA299E-BB28-46C5-AE12-BDE3DE98A7C8.jpg"
    print("📤 正在解析圖片...")
    response_data = parse_document(image_path)

    if response_data:
        # 儲存圖片
        if "som_image_base64" in response_data:
            save_image_from_base64(response_data["som_image_base64"])
        
        # 指定解析結果
        parsed_result = response_data.get("parsed_content_list", [])
        print("✅ 解析完成，傳送至 GPT-4o 判斷點擊按鈕")

        # 顯示 latency
        print(f"⏳ 解析延遲: {response_data.get('latency')} ms")

        # 處理按鈕點擊
        click_target_data = decide_click_target("點擊深入研究",parsed_result)
        print("📌 GPT-4o 判斷結果:", click_target_data)
        print("🖱️ 嘗試點擊按鈕...")
        click_target(click_target_data)
    else:
        print("❌ 解析失敗，請檢查 API")

if __name__ == "__main__":
    main()