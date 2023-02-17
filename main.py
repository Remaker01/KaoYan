import kaoyan
from typing import Iterable
from multiprocessing.pool import ThreadPool
import os
def query():
    school = input("输入查询的学校 ")
    major = input("输入查询的学科类别代码(必填) ")
    while len(major) == 0:
        major = input("学科类别代码为必填项，请重新输入 ")
    majoring = input("输入查询的专业的名称 ")
    non_fullday = input("是否包含非全日制?按y表示包含,其他表示不包含 ")
    return school,major[0:4],majoring,non_fullday.lower() == 'y'
def showResult(lst:Iterable):
    print("本次查询结果为")
    for item in lst:
        for x in item:
            print(x,'\t',end='')
        print('')
def subcode():
    zy,dtype = input("输入专业名称 "),input("输入类型，学硕xs,专硕zx ").lower()
    while True:    
        try:
            return kaoyan.getSubjectCode(zy,dtype)
        except ValueError:
            dtype = input("类型错误，请重新输入 ").lower()
if __name__ == "__main__":
    try:
        fp_loc = open("loc.txt","r",encoding="utf-8")
        os.chdir(fp_loc.read(1024))
        fp_loc.close()
    except OSError:
        print("若要自定义结果保存路径,请在loc.txt中写入并放在与本程序同一目录下")
        fp_loc = open("loc.txt","w",encoding="utf-8")
        fp_loc.write(os.getcwd())
        fp_loc.close()
    _pool = ThreadPool(processes=5)
    print("欢迎使用考研信息查询系统")
    _fps = []
    while True:
        print("\n请输入下列操作之一\n1: 查询院校")
        print("2: 查询详细信息")
        print("3: 查询专业代码")
        print("其他任意键: 退出")
        choice = input()
        if choice != '1' and choice != '2' and choice != '3':
            break # issue1:特殊情况必须首先立即处理
        if choice == '3':
            showResult(subcode())
            continue
        school,major,majoring,non_full = query()
        schools = kaoyan.getSchoolList(subject=major,school=school,stype="" if non_full else "全日制",majoring=majoring)
        if len(schools) == 1:
            print("本次未查询到任何结果")
            continue
        if choice == '1':
            showResult(schools)
        elif choice == '2':
            if len(schools) > 2:
                if input("结果较多，按y把所有结果写入csv文件 ").lower() == 'y':
                    for item in schools[1:]:
                        fp = open(item[0] + ".csv","w",newline='\n')
                        _fps.append(fp)
                        _pool.apply_async(kaoyan.getSchoolMajorList,args=(item[4],True,fp))
            else:
                mresult = kaoyan.getSchoolMajorList(schools[1][4],get_subj=True)
                showResult(mresult)
                x = input("按y保存为csv ")
                if x.lower() == 'y':
                    fp = open(school + ".csv","w",newline='\n')
                    kaoyan.save(mresult,file=fp)
                    fp.close()
    _pool.close()
    _pool.join()
    for fp in _fps:fp.close()