import re
import time
import random
import requests
import pickle as pkl

# 内容根据自己的填
headers = {
    'referer': 'https://item.taobao.com/item.htm?spm=a230r.1.14.1.f20133a3fCshyC&id=599269056085&ns=1&abbucket=12',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44',
    'cookie': 'cna=zosiGv1e0FECAXGMC3ujzsCs; tracknick=tb70552302; enc=v1EQMsYSWcwfgRNxDl+0mJwO+Zod3SBg14RzyKrpxVWoI5gGVbFL/tjj57+a6zfrcMLGKNtJoz2zfIbZB3Xerg==; miid=4867062431434503621; thw=cn; _m_h5_tk=2ccd78f1020ff2f72e27736afe48be36_1650256681872; _m_h5_tk_enc=77e8bc801b3ffd04504202b4ebb7c78e; t=321fff142170756080b33079426883ff; lgc=tb70552302; sgcookie=E100i0SBRSrsbeKEgN1GyWNS2CDc/Pl/27gCII7PGFBmcywWIKSEslSPGqlEeTYSnR1H8PZ1k7LYoxj7vAutw/JsUEmDNC6ZEU/qEIT1caLSqOs=; uc3=id2=UNcLXfS6qqEFhQ==&nk2=F5RCZV0GLhKm2Q==&vt3=F8dCvCh89ywgshlNWKg=&lg2=URm48syIIVrSKA==; uc4=nk4=0@FY4Ji3A2d6YoWVI5VkZwBYtTzARH&id4=0@UgDNjSFzivV8ZlC3tenoQ/I3XLSR; _cc_=UtASsssmfA==; mt=ci=53_1; xlly_s=1; _samesite_flag_=true; cookie2=1467ebc717f12e76bd28492ae57a7bf2; _tb_token_=533a3ae7334dd; tfstk=cL3RBOT6CKvucVNx_0KmTr7E-9hRZS18K_wdJ2Ufw0PfD7_diNuiWrK2VWyaeIC..; l=eBQHrNtHgDl29PHwBOfZlurza77thIRXjuPzaNbMiOCPOT5J-nTcW62ez68vCnGVnsUvR3loI7m7BWTUByUBlEGfIqlBs2JZndLh.; isg=BKeng8WdieBtMw78GdI68Ng-NttxLHsOrxzLkHkUpTZJaMYqgf25Xlsuimh2q1OG'
}

# 模仿人获取网页源码，并转化为str类型的文本格式
url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=599269056085&userNumId=132691477&currentPageNum=1&pageSize=20&rateType=&orderType=sort_weight&attribute=&sku=&hasSku=false&folded=0&ua=098%23E1hvtQvUvbZvUvCkvvvvvjiWRLsWzjrRRFMv0j3mPmP9tjtRPLSw1jrnn2Lh6jDUi9hvCvvv9UUgvpvhvvvvvvvCvvOvCvvvphvUvpCW2EYVvvaMFa11gLWXjVonzjj3%2BX%2BwXUzhwJV1VVERD7zhaXgBOyTxfwCl533%2BCNLhQRpXe7Q4S47B9CkaU6bnDO2hVB6AxYjxAfyp%2Bd9Cvm9vvvvvphvvvvvvvLrvpv9zvvv2vhCv2UhvvvWvphvWQvvvvQCvpvsvkvhvCQ9v9OC1pwmIvpvUvvmvpvjCbJwRvpvhvv2MMQ%3D%3D&_ksTS=1650370563260_2705&callback=jsonp_tbcrate_reviews_list'
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
for i in range(10):
    url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=599269056085&userNumId=132691477&currentPageNum=1&pageSize=20&rateType=&orderType=sort_weight&attribute=&sku=&hasSku=false&folded=0&ua=098%23E1hvtQvUvbZvUvCkvvvvvjiWRLsWzjrRRFMv0j3mPmP9tjtRPLSw1jrnn2Lh6jDUi9hvCvvv9UUgvpvhvvvvvvvCvvOvCvvvphvUvpCW2EYVvvaMFa11gLWXjVonzjj3%2BX%2BwXUzhwJV1VVERD7zhaXgBOyTxfwCl533%2BCNLhQRpXe7Q4S47B9CkaU6bnDO2hVB6AxYjxAfyp%2Bd9Cvm9vvvvvphvvvvvvvLrvpv9zvvv2vhCv2UhvvvWvphvWQvvvvQCvpvsvkvhvCQ9v9OC1pwmIvpvUvvmvpvjCbJwRvpvhvv2MMQ%3D%3D&_ksTS=1650370563260_2705&callback=jsonp_tbcrate_reviews_list'.format(
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
