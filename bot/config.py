import yaml
import dotenv
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# Load yaml config
with open(config_dir / "config.yml", 'r', encoding='utf-8') as f:
    config_yaml = yaml.safe_load(f)

# Load .env config
config_env = dotenv.dotenv_values(config_dir / "config.env")

# Config parameters
telegram_token = config_yaml["telegram_token"]
openai_api_key = config_yaml["openai_api_key"]
use_chatgpt_api = config_yaml.get("use_chatgpt_api", True)
allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
new_dialog_timeout = config_yaml["new_dialog_timeout"]
enable_message_streaming = config_yaml.get("enable_message_streaming", True)
return_n_generated_images = config_yaml.get("return_n_generated_images", 1)
n_chat_modes_per_page = config_yaml.get("n_chat_modes_per_page", 5)
mssql_connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config_env['MSSQL_HOST']};DATABASE={config_env['MSSQL_DATABASE']};UID={config_env['MSSQL_USER']};PWD={config_env['MSSQL_PASSWORD']}"

# Chat_modes
with open(config_dir / "chat_modes.yml", 'r', encoding='utf-8') as f:
    chat_modes = yaml.safe_load(f)

# Models
with open(config_dir / "models.yml", 'r', encoding='utf-8') as f:
    models = yaml.safe_load(f)

# Files
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"
