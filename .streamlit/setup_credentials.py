import bcrypt

password1 = bcrypt.hashpw('demo123'.encode(), bcrypt.gensalt()).decode()
password2 = bcrypt.hashpw('bilaspur123'.encode(), bcrypt.gensalt()).decode()

content = (
    "credentials:\n"
    "  usernames:\n"
    "    vyaparscore_demo:\n"
    "      email: demo@vyaparscore.com\n"
    "      name: Demo Bank\n"
    f'      password: "{password1}"\n'
    "    coop_bank_bilaspur:\n"
    "      email: bilaspur@vyaparscore.com\n"
    "      name: Cooperative Bank Bilaspur\n"
    f'      password: "{password2}"\n'
    "\n"
    "cookie:\n"
    "  expiry_days: 1\n"
    "  key: vyaparscore_secret_key_2024\n"
    "  name: vyaparscore_cookie\n"
)

with open('credentials.yaml', 'w', encoding='utf-8') as f:
    f.write(content)

print('credentials.yaml created successfully!')