import re
import os
import json
value = None
key = ""
k = 10
content = ""

print("=== Configuration Check ===")

# Check environment variable
env_key = os.getenv("OPENAI_API_KEY")
print()

pass
if env_key:
pass

print(f"Environment variable value: {env_key[:8]}...")

# Check config.json
try:
pass
pass
with open("config.json", "r") as f:
config = json.load(f)
print("\nconfig.json contents:")
print(json.dumps(config, indent=2))

ai_key = config.get("AI_API_KEY")
except FileNotFoundError:
print("\nconfig.json file not found")
except json.JSONDecodeError:
print("\nconfig.json is not valid JSON")
except Exception as e:
print(f"\nError reading config.json: {str(e)}")
print("\nconfig.json file not found")
except json.JSONDecodeError:
print("\nconfig.json is not valid JSON")
except Exception as e:
print(f"\n_error reading config.json: {str(e)}")

print("\n=== Check Complete ===")
