import re
import time
import random
import requests
import pickle as pkl

# 内容根据自己的填
headers = {
    'referer': 'https://chaoshi.detail.tmall.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44',
    'cookie': 'cna=zosiGv1e0FECAXGMC3ujzsCs; lid=tb70552302; enc=v1EQMsYSWcwfgRNxDl+0mJwO+Zod3SBg14RzyKrpxVWoI5gGVbFL/tjj57+a6zfrcMLGKNtJoz2zfIbZB3Xerg==; sm4=610100; sgcookie=E100i0SBRSrsbeKEgN1GyWNS2CDc/Pl/27gCII7PGFBmcywWIKSEslSPGqlEeTYSnR1H8PZ1k7LYoxj7vAutw/JsUEmDNC6ZEU/qEIT1caLSqOs=; uc1=cookie14=UoexMnpTYVTu3g==; uc3=id2=UNcLXfS6qqEFhQ==&nk2=F5RCZV0GLhKm2Q==&vt3=F8dCvCh89ywgshlNWKg=&lg2=URm48syIIVrSKA==; t=b6c6761a5c6d64bc3fc9a6bbc1dd97a5; tracknick=tb70552302; uc4=nk4=0@FY4Ji3A2d6YoWVI5VkZwBYtTzARH&id4=0@UgDNjSFzivV8ZlC3tenoQ/I3XLSR; lgc=tb70552302; _tb_token_=5935ee36ad5bb; cookie2=1588aa81dee52765337b5fc9acdf10b7; _m_h5_tk=d528119eb0149047fb3b58e1505792a9_1650696195338; _m_h5_tk_enc=7b20bc08c62dc59005d5466ec66295c2; xlly_s=1; csa=0_0_0.0; tfstk=cw3lBuG_10r5bVEmfUaWRcyD233lZZtzF2uquQ0DFPvqMf3Vi1IVbBUBi8p6UM1..; l=eBIlqgPrgDlnv6FwKOfCnurza7797IRvmuPzaNbMiOCP9sfM5m9fW6qmIVTHCnGVhsCwR3loI7m7BeYBqnV0x6aZUR-DrUDmn; isg=BEREOSRx-lSixU21fomfHZRdFcI2XWjHUJ3IGV7lxI_RieRThm6jVkcvySFRpaAf'
}

# 模仿人获取网页源码，并转化为str类型的文本格式
url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=538402184082&spuId=699720530&sellerId=725677994&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&ua=098%23E1hvvvvEvb6vUpCkvvvvvjiWRLsOgjlWPszUgjEUPmPUgjtERsSysji2PF5UzjiPRgOCvvpv9hCvi9hvCvvvpZpRvpvhMMGvvvvCvvOv9hCvvvvUvpCWva2dT10yHd8rV369D76OdiwXaZRQD46fditApRm%2B%2Bu0fdeQEfJoK5d8rameOD46fd3ODNrBlHskTKo9vD70wdip7EcqpaXgXVB1d2u9Cvv9vvhjCZLg%2FbO9CvvwCvhnm1WvOKvhv8vvvphvvvvvvvvC2z9vvvJOvvhXVvvmCWvvvByOvvUhOvvCVB9vv9B9gvpvhvvCvpv%3D%3D&isg=BL29T-U2g78TiiR-n-52JqVCzBm3WvGsgZJhkn8C7ZRAtt3oR6mafbZkYOrwAglk&_ksTS=1650686132649_363&callback=jsonp364'
data = requests.get(url, headers=headers).text
# 正则表达式
# pat = re.compile('"内容"')
pat = re.compile('"rateContent":"(.*?)","fromMall"')
# 执行过滤操作
pat.findall(data)
# 此时的data输出便是列表格式的当前网页的所有评论

# 比如爬取前十页评论
texts = []
# 爬取前十页的商品评论
for i in range(5000):
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=538402184082&spuId=699720530&sellerId=725677994&order=3&currentPage={0}&append=0&content=1&tagId=&posi=&picture=&ua=098%23E1hvvvvEvb6vUpCkvvvvvjiWRLsOgjlWPszUgjEUPmPUgjtERsSysji2PF5UzjiPRgOCvvpv9hCvi9hvCvvvpZpRvpvhMMGvvvvCvvOv9hCvvvvUvpCWva2dT10yHd8rV369D76OdiwXaZRQD46fditApRm%2B%2Bu0fdeQEfJoK5d8rameOD46fd3ODNrBlHskTKo9vD70wdip7EcqpaXgXVB1d2u9Cvv9vvhjCZLg%2FbO9CvvwCvhnm1WvOKvhv8vvvphvvvvvvvvC2z9vvvJOvvhXVvvmCWvvvByOvvUhOvvCVB9vv9B9gvpvhvvCvpv%3D%3D&isg=BL29T-U2g78TiiR-n-52JqVCzBm3WvGsgZJhkn8C7ZRAtt3oR6mafbZkYOrwAglk&_ksTS=1650686132649_363&callback=jsonp364'.format(
        i + 1)
    # 增加随机延时,避免反爬
    time.sleep(random.randint(3, 6))
    try:
        data = requests.get(url, headers=headers).text
    except:
        break
    texts.extend(pat.findall(data))
    print("第{}页评论爬取完毕".format(i+1))


def filter_emoji(desstr, restr=''):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


fb = open("comments.txt", 'w', encoding='utf-8')
for text in texts:
    text = filter_emoji(text) + "\n"
    fb.write(text)
print("评论保存完毕！")
fb.close()
