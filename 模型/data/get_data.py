import re
import time
import random
import requests

# 内容根据自己的填
headers = {
    'referer': 'https://detail.tmall.com/item.htm?spm=a230r.1.14.57.5fba64f8bhH5rw&id=41828566996&ns=1&abbucket=1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50',
    'cookie': 'cna=zosiGv1e0FECAXGMC3ujzsCs; lid=tb70552302; enc=v1EQMsYSWcwfgRNxDl+0mJwO+Zod3SBg14RzyKrpxVWoI5gGVbFL/tjj57+a6zfrcMLGKNtJoz2zfIbZB3Xerg==; sm4=610100; xlly_s=1; csa=0_0_0.0; sgcookie=E100i0SBRSrsbeKEgN1GyWNS2CDc/Pl/27gCII7PGFBmcywWIKSEslSPGqlEeTYSnR1H8PZ1k7LYoxj7vAutw/JsUEmDNC6ZEU/qEIT1caLSqOs=; uc1=cookie14=UoexMnuATGtwAQ==; uc3=id2=UNcLXfS6qqEFhQ==&nk2=F5RCZV0GLhKm2Q==&vt3=F8dCvCh89ywgshlNWKg=&lg2=URm48syIIVrSKA==; t=fd3418411aa8720b2ecfe09098cabaf4; tracknick=tb70552302; uc4=nk4=0@FY4Ji3A2d6YoWVI5VkZwBYtTzARH&id4=0@UgDNjSFzivV8ZlC3tenoQ/I3XLSR; lgc=tb70552302; _tb_token_=e07e687b81857; cookie2=1a91f4fcc17ce6bfe6c979ddb2b7c839; _m_h5_tk=83d60fe738629494d31c174fe11f2e65_1650730830558; _m_h5_tk_enc=ab1400c759748c5a6d4bdc08278fe620; tfstk=cViOBuxWNBAGDfeKUVLn3wA42GMAZ5BTiONADmUwWyayrJIAiMoo2kLe5-Pz6pC..; l=eBIlqgPrgDlnvE5WKOfahurza77tcIRXjuPzaNbMiOCPOh1J5aJ1W6q8268vCnGVHsZpR3loI7VUBcTHXyKVokb4d_BkdloxndC..; isg=BE1NkxZ_E0h7DbTOj97m9tUSXGnHKoH8cULR_Y_S7uRXhmw4V3vHzJUQ8BrgbZm0'
}

# 模仿人获取网页源码，并转化为str类型的文本格式
url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=41828566996&spuId=848226244&sellerId=2176070676&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098#E1hvcpvnvP9vUpCkvvvvvjiWRLswAjrWRFch1jnEPmPv6jDCR2cvzjYPR2sygj1Un8QCvCUymbAmwchvUmgidAyDZT7xzw0vvpvWzPAQOMSNznswSUC439hvCvvhvvvgvpvhvvvvvvgCvvLMMQvvvvhvC9vhvvCvpv9CvhQvhuZvCsuxfJBlHdUfb5c61bm655Hv6WFy+2Kz8Z0vQRAn+byDCwLOTWeARFxjKOmxfXuKNB3r1j7Q+ul68NoxfwAKHkx/0jc6f4g7Kvhv8vvvvvCvpvvvvvmCsyCvm2wvvvWvphvW9pvvvQCvpvsvvvv2vhCv2WmIvpvUvvmvpC40hUVUvpvjmvmC9jHCQ8OCvvpvvUmmdvhvmpvhkOL1GpvZHF9Cvvpvvvvv&needFold=0&_ksTS=1650720771471_607&callback=jsonp608'
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
for i in range(500):
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=41828566996&spuId=848226244&sellerId=2176070676&order=3&currentPage={0}&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098#E1hvcpvnvP9vUpCkvvvvvjiWRLswAjrWRFch1jnEPmPv6jDCR2cvzjYPR2sygj1Un8QCvCUymbAmwchvUmgidAyDZT7xzw0vvpvWzPAQOMSNznswSUC439hvCvvhvvvgvpvhvvvvvvgCvvLMMQvvvvhvC9vhvvCvpv9CvhQvhuZvCsuxfJBlHdUfb5c61bm655Hv6WFy+2Kz8Z0vQRAn+byDCwLOTWeARFxjKOmxfXuKNB3r1j7Q+ul68NoxfwAKHkx/0jc6f4g7Kvhv8vvvvvCvpvvvvvmCsyCvm2wvvvWvphvW9pvvvQCvpvsvvvv2vhCv2WmIvpvUvvmvpC40hUVUvpvjmvmC9jHCQ8OCvvpvvUmmdvhvmpvhkOL1GpvZHF9Cvvpvvvvv&needFold=0&_ksTS=1650720771471_607&callback=jsonp608'.format(
        i + 1)
    # 增加随机延时,避免反爬
    time.sleep(random.randint(1, 3))
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


fb = open("tea.txt", 'w', encoding='utf-8')
for text in texts:
    text = filter_emoji(text) + "\n"
    fb.write(text)
print("评论保存完毕！")
fb.close()
