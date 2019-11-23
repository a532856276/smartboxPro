#注意:代码模板中的代码将会被复制到任何新创建的文件中，编辑代码模板中的代码，让他;帮你自动增加固定代码吧
#aaa = input("bbb:");
#print(aaa);

#import urllib2 
import urllib

def getNetContent():
    url = 'http://www.baidu.com'
#创建request对象
    request = urllib.Request(url)
#发送请求，获取结果
    #try:
    response = urllib.urlopen(request)
    #except BaseException, err:
        #print err
        #exit()
    #else:
        #print("ok")
#获取状态码，如果是200表示获取成功
    code = response.getcode()
    print(code)
#读取内容
    if 200 == code:
        content = response.read() 
        print(content)
if __name__== "__main__":
    print("hello")
    getNetContent()
