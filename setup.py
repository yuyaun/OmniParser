import os
from huggingface_hub import hf_hub_download

# 設定要下載的儲存庫ID
repo_id = "microsoft/OmniParser"

# 定義每個子資料夾要下載的檔案列表
files_to_download = {
    "icon_detect": ["model.safetensors", "model.yaml"],
    "icon_caption_florence": ["config.json", "generation_config.json", "model.safetensors"],
    "icon_caption_blip2": ["config.json", "generation_config.json", "pytorch_model-00001-of-00002.bin", "pytorch_model-00002-of-00002.bin", "pytorch_model.bin.index.json"],
    "icon_detect_v1_5": ["model.yam", "model_v1_5.pt", "train_args.yaml"],
}

# 逐一下載並存放到指定資料夾下
for folder, file_list in files_to_download.items():
    # 建立對應的本機資料夾
    local_dir = os.path.join("weights", folder)
    os.makedirs(local_dir, exist_ok=True)
    
    for file_name in file_list:
        # 假設儲存庫內的檔案結構為 folder/file_name
        repo_filepath = f"{folder}/{file_name}"
        try:
            local_filepath = hf_hub_download(
                repo_id=repo_id,
                filename=repo_filepath,
                local_dir=local_dir
            )
            print(f"下載成功：{repo_filepath} -> {local_filepath}")
        except Exception as e:
            print(f"下載 {repo_filepath} 時發生錯誤：{e}")