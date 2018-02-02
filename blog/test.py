
def inpu(view_func):
    mystr = input('请输入一个字符串:')
    def wrap():
        view_func(mystr)
    return wrap

@inpu
def prin(mystr):
    print(mystr)

# prin = inpu(prin)
prin()