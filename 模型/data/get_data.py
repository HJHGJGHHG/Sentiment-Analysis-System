import re
import time
import random
import requests
import pickle as pkl

# 内容根据自己的填
headers = {
    'referer': 'https://detail.tmall.com/item.htm?spm=a230r.1.14.1.204e7d3cAuYLmc&id=564725598700&ns=1&abbucket=12',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39',
    'cookie': 'cna=zosiGv1e0FECAXGMC3ujzsCs; lid=tb70552302; enc=v1EQMsYSWcwfgRNxDl+0mJwO+Zod3SBg14RzyKrpxVWoI5gGVbFL/tjj57+a6zfrcMLGKNtJoz2zfIbZB3Xerg==; t=321fff142170756080b33079426883ff; tracknick=tb70552302; _tb_token_=f9be6eb653e97; cookie2=16932c2897cb90db17afcec4613d2fc1; dnk=tb70552302; _l_g_=Ug==; unb=3738973260; lgc=tb70552302; cookie1=BxJMYGCm+VJgBONxHGU++g5/bNmgDcEFlN7K9IiQqBA=; login=true; cookie17=UNcLXfS6qqEFhQ==; _nk_=tb70552302; cancelledSubSites=empty; sg=20d; xlly_s=1; uc1=cookie15=UtASsssmOIJ0bQ==&existShop=false&cookie14=UoexMn5vYlkf6w==&cookie16=Vq8l+KCLySLZMFWHxqs8fwqnEw==&pas=0&cookie21=V32FPkk/gihF/S5nr3O5; uc3=id2=UNcLXfS6qqEFhQ==&nk2=F5RCZV0GLhKm2Q==&vt3=F8dCvCh89ywgshlNWKg=&lg2=URm48syIIVrSKA==; uc4=nk4=0@FY4Ji3A2d6YoWVI5VkZwBYtTzARH&id4=0@UgDNjSFzivV8ZlC3tenoQ/I3XLSR; sgcookie=E100i0SBRSrsbeKEgN1GyWNS2CDc/Pl/27gCII7PGFBmcywWIKSEslSPGqlEeTYSnR1H8PZ1k7LYoxj7vAutw/JsUEmDNC6ZEU/qEIT1caLSqOs=; csg=76e24b0d; _m_h5_tk=3470a716cd71ec2c5d420aa128fed500_1650258173376; _m_h5_tk_enc=ab29e09bb377d6115295e0e8ba97374b; tfstk=c4bdB34bhR23osAOgMEGalZ7OV6dZFGpEX9-yaC4K8Eqt3gRim7ckFEaAQJ2p5C..; l=eBIlqgPrgDlnvpeUBOfanurza77OYIRvmuPzaNbMiOCPOn1wK38AW62dOkLeCnGVh6W2R38b3NEuBeYBqhVgx6aNa6Fy_CDmn; isg=BImJ7MKRD2SGm_AC6_JqQgkGmLXj1n0Ia2k2yCv-WnD8cqmEcyWo2IKstNZEHhVA'
}

# 模仿人获取网页源码，并转化为str类型的文本格式
url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=564725598700&spuId=1597206294&sellerId=2452619605&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098#E1hvUpv8vWIvUvCkvvvvvjiWRLsUljrEP2s9sjivPmPOsj1PPFFvgjDUP25hgj3ndvhvmpmCVCWtvvmn3IOCvvpv9hCv29hvCvvvMMGvvpvVvUCvpvvvmvhvLUjv9gWa+boJe11tLq2XrqpAhjCbFO7t+3mOJhbEDLuTRLa9C7zhdigqrADn9Wv7+u0fjomxfBkKHdUfbjc6+u0fderEkbmAdBkKNo4UvpvjvpC2p+LvV89Cvv9vvhjCThqfvb9Cvm9vvhCvvvvvvvvvpMWvvvjevvCVB9vv9LvvvhXVvvmCVvvvByOvvUhORvhvCvvvphmevpvhvvCCBv==&needFold=0&_ksTS=1650250209074_727&callback=jsonp728'
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
for i in range(200):
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=564725598700&spuId=1597206294&sellerId=2452619605&order=3&currentPage={0}&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098#E1hvUpv8vWIvUvCkvvvvvjiWRLsUljrEP2s9sjivPmPOsj1PPFFvgjDUP25hgj3ndvhvmpmCVCWtvvmn3IOCvvpv9hCv29hvCvvvMMGvvpvVvUCvpvvvmvhvLUjv9gWa+boJe11tLq2XrqpAhjCbFO7t+3mOJhbEDLuTRLa9C7zhdigqrADn9Wv7+u0fjomxfBkKHdUfbjc6+u0fderEkbmAdBkKNo4UvpvjvpC2p+LvV89Cvv9vvhjCThqfvb9Cvm9vvhCvvvvvvvvvpMWvvvjevvCVB9vv9LvvvhXVvvmCVvvvByOvvUhORvhvCvvvphmevpvhvvCCBv==&needFold=0&_ksTS=1650250209074_727&callback=jsonp728'.format(
        i + 1)
    # 增加随机延时,避免反爬
    time.sleep(random.randint(3, 6))
    data = requests.get(url, headers=headers).text
    texts.extend(pat.findall(data))
    print("第{}页评论爬取完毕".format(i))


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
