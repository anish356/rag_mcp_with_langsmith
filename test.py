from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

for key, value in os.environ.items():
    print(f"{key} = {value}")