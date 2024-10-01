str = []
str.append("hello:bye")
str.append("what:how")
print(str[0], str[1])
str[0] = str[0].split(":")
print(str[0][0], str[0][1])