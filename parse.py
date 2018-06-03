import re
import sys
import base64
import quopri


def parse(msg):
    try:
        from_email_list = re.findall(r'From: (.)*<(.+)*>', msg)[0]
        from_email = from_email_list[1]
    except:
        sys.exit("Не могу распарсить имя")
    try:
        to_email = re.findall(r'To: [\S]* <([\S]+)*>', msg)[0]
    except:
        sys.exit("Не могу распарсить имя")
    try:
        boundary = re.findall(r'boundary="(.+)"', msg)[0]
    except IndexError:
        boundary = ''
    reg = re.compile(r"Subject: =\?UTF-8\?([BQ])\?(\S+)\?=", re.IGNORECASE)
    res = reg.findall(msg)
    if res != []:
        if res[0][0] == 'B':
            subject = base64.b64decode(res[0][1]).decode()
        else:
            subject = quopri.decodestring(res[0][1]).decode()
    else:
        subject = "No theme"
    if boundary:
        part = msg.split(r'Content-Type: text/plain;')[1]
        text = part.split('\n')[3]
    else:
        mes_parts = msg.split('\r\n\r\n')
        text = mes_parts[1][:-5]
    files = dict()
    names = re.findall(r"filename=[\S]+", msg)
    if boundary:
        if names != []:
            for element in names:
                if element.split('?')[2] == 'B':
                    files[element.split('?')[3]] = base64.b64decode(element.split('?')[3]).decode()
                else:
                    files[element.split('?')[3]] = quopri.decodestring(element.split('?')[3]).decode()
    if files:
        mes_parts = msg.split(boundary)
        for part in mes_parts:
            name = re.findall(r'attachment; filename="(.*)"', part)
            if name:
                letter = name[0].split('?')[2]
                parts = part.split('\r\n')
                file = ''
                for i in range(5, len(parts)):
                    if parts[i] != '--':
                        file = file + parts[i]
                with open(files[name[0].split('?')[3]], "wb") as f:
                    if letter == 'B':
                        f.write(base64.decodestring(file.encode()))
                    else:
                        f.write(quopri.encodestring(file.encode()))
    print("From: %s" % str(from_email))
    print("To: %s" % str(to_email))
    print("Тема письма: %s" % str(subject))
    if text != '':
        if res[0][0] == 'B':
            print("Текст письма:\n" + base64.b64decode(text).decode())
        else:
            try:
                print("Текст письма:\n" + quopri.decodestring(text).decode())
            except ValueError:
                print("Текст письма:\n" + text)
    else:
        print("Текст отсутствует")
