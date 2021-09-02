from datetime import datetime


def timedate_magic(string1):
    ln = len(string1.split('/'))
    new = []
    for i in string1.split('/'):
        if len(i) == 1:
            new.append('0'+i)
        else:
            new.append(i)
    string1='/'.join(new)
    if ln == 4:
        return string1
    elif ln == 3:
        return string1+f'/{datetime.now().year}'
    elif ln == 2:
        return string1+f'/{"0" + str(datetime.now().month) if  datetime.now().month < 10 else datetime.now().month}/{datetime.now().year}'
    elif ln == 1:
        return string1+f'/{"0" + str(datetime.now().day) if  datetime.now().day < 10 else datetime.now().day}/{"0" + str(datetime.now().month) if  datetime.now().month < 10 else datetime.now().month}/{datetime.now().year}'

print(timedate_magic('2/30/1/2021'))