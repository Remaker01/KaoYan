'''
从研招网爬取研究生招生信息\n
使用示例\n
import kaoyan\n
all = kaoyan.getSchoolList(subject="0839",stype="全日制")\n
details = kaoyan.getSchoolMajorInfo(all[1][4])\n
details_with_subjs = kaoyan.getSchoolMajorInfo(all[2][4],get_subj=True)\n
    # 获取学校列表后进行并发请求。建议使用并发时指定输出，直接使用getSchoolMajorInfo的返回值可导致详细信息和学校不对应\n
pool = ThreadPool()\n
for each in all:\n
    with open(each[0]) as fp:\n
        pool.apply_async(kaoyan.getSchoolMajorInfo(each[4],output_fp=fp))
'''
from urllib3.poolmanager import PoolManager
import json,re,sys
from lxml import etree
HOST = "https://yz.chsi.com.cn"
head = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/91.0",
    "Accept":"gzip, deflate",
    "Referer":HOST + "/zsml/zyfx_search.jsp",
    "Connection":"keep-alive"
}
_http = PoolManager(num_pools=3,headers=head)
_province_table = []
def _get_location_index(loc:str):
    '''将地区名称映射为数字'''
    global _province_table
    if len(_province_table) == 0:
        respo = _http.request_encode_body("POST",url=HOST + "/zsml/pages/getSs.jsp")
        _province_table = json.loads(respo.data)
    for item in _province_table:
        if item["mc"] == loc:
            return item["dm"]
    return ""
def _remove_redundant(str_with_index:str):
    '''传入带编号的数字，去除冗余部分(括号+内部的数字)'''
    RE = re.compile("\([0-9]+\)")
    _find = RE.findall(str_with_index)
    return str_with_index.replace(_find[0],"")
def _get_number_from_script(script:str):
    '''从js的字符串中截取招生人数'''
    NUM = re.compile("[0-9]+")
    _find = NUM.findall(script)
    return _find[0]
def getSchoolList(subject,location="",school="",stype=""):
    '''
    获取学校列表

    Parameters:
    ---------------
    subject:学科类别(代码)，必填项\n
    location:地域,默认为空。如果给定错误省份将在全国范围内搜索\n
    school:学校,默认为空\n
    stype:学习方式,全日制("1")非全日制("2"),默认为空

    Returns:
    ---------------
    list[list]  包含搜索到的各学校信息的列表\n
    每个学校信息是包括学校名、省份、是否有研究生院、是否为自划线以及详细信息URL的列表
    '''
    TABLE_HEAD = ["招生单位","所在地","研究生院","自划线院校","URL"]
    if stype == "全日制":
        xxfs = "1"
    elif stype == "非全日制":
        xxfs = "2"
    elif stype != "1" and stype != "2":
        raise ValueError("非法的学习方式")
    loc = _get_location_index(location)
    schools = []
    data = {
        "ssdm":loc, # 省份
        "dwmc":school, # 学校
        "mldm":"", # 大类
        "mlmc":"",
        "yjxkdm":subject, # 学科类别
        "xxfs":xxfs # 学习方式
    }
    # print("已封装请求数据",data)
    respo = _http.request_encode_url("POST",url=HOST+"/zsml/queryAction.do",fields=data) # 注意data是标在url上，所以要指明encode_url
    tree = etree.HTML(respo.data.decode("utf-8"))
    trs = tree.xpath("//body//div//table[@class=\"ch-table\"]/tbody/tr")
    # print(trs)
    for tr in trs:
        name = tr.xpath("./td[1]//a/text()")
        if len(name) == 0:
            return [TABLE_HEAD]
        name = name[0]
        sub_url = HOST + tr.xpath("./td[1]//a/@href")[0] #结构td/frame/a
        loc = tr.xpath("./td[2]/text()")[0]
        td3 = tr.xpath("./td[3]/i")
        td4 = tr.xpath("./td[4]/i")
        gdu_instit = (len(td3) != 0) # gradute_institude
        zi_huaxian = (len(td4) != 0)
        info = [name,_remove_redundant(loc),str(gdu_instit),str(zi_huaxian),sub_url]
        schools.append(info)
    return [TABLE_HEAD] + schools
def getSchoolMajorList(url,get_subj = False,output_fp = None):
    '''
    根据url获取学校信息

    Parameters
    ----------
    url:包含考试科目的url\n
    get_subj:bool  是否包含考试科目\n
    output_fp:输出文件，默认为None

    Raises
    ------
    当URL不符合给定格式时，引发ValueError

    Returns
    -------
    list[list]  get_subj==False时 包含每个专业信息的列表。每个专业信息包括学院、专业名、研究方向、学习方式、招生人数和考试科目的URL。\n
    get_subj==True时，最后一列包含考试科目(外国语,业务课1,业务课2)
    '''
    # TODO:进行一些并发操作
    table_head = ["学院","专业","研究方向","学习方式","招生人数","考试科目URL"]
    if get_subj:
        table_head[5] = "考试科目"
    # if isinstance(url,list):
    #     url = url[4]
    if not url.startswith(HOST+"/zsml/querySchAction.do"):
        raise ValueError("非法的URL地址")
    respo = _http.request("GET",url=url)
    tree = etree.HTML(respo.data.decode("utf-8"))
    trs = tree.xpath("//body/div//table[@class=\"ch-table more-content\"]/tbody/tr")
    majors = []
    for tr in trs:
        faculty = tr.xpath("./td[2]/text()")[0] 
        major = tr.xpath("./td[3]/text()")[0]
        rsch_dr = tr.xpath("./td[4]/text()")[0] # research_direction
        stype = tr.xpath("./td[5]/text()")[0] # study_type
        script = tr.xpath("./td[7]/script/text()")[0]
        popu = _get_number_from_script(script) #population
        exam_url = HOST + tr.xpath("./td[8]/a/@href")[0]
        if not get_subj:
            majors.append([faculty,major,rsch_dr,stype,popu,exam_url])
        else:
            subjects = getExamSubjects(url=exam_url)
            majors.append([faculty,major,rsch_dr,stype,popu,subjects])
    
    if output_fp is not None:
        save([table_head] + majors,output_fp)
    return [table_head] + majors
def getExamSubjects(url):
    '''
    根据包含考试科目的url获取考试科目

    Parameters
    ----------
    url:str 包含考试科目的url

    Raises
    ------
    当URL不是包含考试科目的URL时，引发ValueError

    Returns
    -------
    包含下列元素的tuple:\n
    lang:外国语科目
    major1:专业课1科目
    major2:专业课2科目

    '''
    if not url.startswith(HOST+"/zsml/kskm.jsp"):
        raise ValueError("非法的URL地址")
    respo = _http.request("GET",url=url)
    tree = etree.HTML(respo.data.decode("utf-8"))
    tr = tree.xpath("//body//div[@class=\"zsml-result\"]/table/tbody/tr")[0]
    lang = tr.xpath("./td[2]/text()")[0].strip()
    major1 = tr.xpath("./td[3]/text()")[0].strip()
    major2 = tr.xpath("./td[4]/text()")[0].strip()
    return _remove_redundant(lang),major1,major2 # 英语一般不用代号
def save(mresult,file=sys.stdout):
    '''将getSchoolMajorList查询到的结果mresult保存为文件。'''
    for result in mresult:
        result.extend(result[5])
        result.__delitem__(5)
        file.write(','.join(result) + '\n')
# if __name__ == "__main__":
#     from multiprocessing.pool import ThreadPool
#     sbj = input("输入专业代码 ")
#     sch = input("输入学校 ")
#     results = getSchoolList(subject=sbj,location="",school=sch,stype="全日制")
#     _pool = ThreadPool(processes=5)
#     for item in results[1:]:
#         fp = open(item[0] + ".csv","w",newline='\n')
#         _pool.apply_async(getSchoolMajorList,args=(item[4],True,fp))
#     _pool.close()
#     _pool.join()