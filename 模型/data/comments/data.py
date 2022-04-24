texts = []
with open("car.txt", "r", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.replace(" ", "")
        if "." in line:
            print(line.strip())
            continue
        line = line.strip().replace(":", "：").replace("'", "’").replace("!", "！").replace("?", "？").replace(";","；").replace("(", "（").replace(")", "）").replace(".", "")
        texts.append(line.strip())
    f.close()


with open("car.txt", "w", encoding="utf-8") as f:
    for text in texts:
        text = text + '\n'
        f.write(text)
    f.close()
