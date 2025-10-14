import json

with open("tf_outputs.json") as f:
    data = json.load(f)

env_lines = []
for key, value in data.items():
    env_key = key.upper()
    env_value = value["value"]
    env_lines.append(f"{env_key}={env_value}")

with open(".env", "w") as f:
    f.write("\n".join(env_lines))

print(".env file created from Terraform outputs!")
