import kaoyan
from typing import Iterable
from multiprocessing.pool import ThreadPool
def query():
    school = input("输入查询的学校 ")
    major = input("输入查询的学科类别代码(必填) ")
    majoring = input("输入查询的专业的名称 ")
    non_fullday = input("是否包含非全日制?按y表示包含,其他表示不包含 ")
    return school,major[0:4],majoring,non_fullday.lower() == 'y'
def showResult(lst:Iterable):
    print("本次查询结果为")
    for item in lst:
        for x in item:
            print(x,'\t',end='')
        print('')
if __name__ == "__main__":
    _pool = ThreadPool(processes=5)
    print("欢迎使用考研信息查询系统")
    _fps = []
    while True:
        print("\n请输入下列操作之一\n1: 查询专业")
        print("2: 查询详细信息")
        print("其他任意键: 退出")
        choice = input()
        if choice != '1' and choice != '2':
            break # issue1:特殊情况必须首先立即处理
        school,major,majoring,non_full = query()
        schools = kaoyan.getSchoolList(subject=major,school=school,stype="" if non_full else "全日制",majoring=majoring)
        if len(schools) == 1:
            print("本次未查询到任何结果")
            continue
        if choice == '1':
            showResult(schools)
        elif choice == '2':
            if len(schools) > 2:
                print("结果较多，将把所有结果写入csv文件")
                for item in schools[1:]:
                    fp = open(item[0] + ".csv","w",newline='\n')
                    _fps.append(fp)
                    _pool.apply_async(kaoyan.getSchoolMajorList,args=(item[4],True,fp))
            else:
                mresult = kaoyan.getSchoolMajorList(schools[1][4],get_subj=True)
                showResult(mresult)
                x = input("按y保存 ")
                if x.lower() == 'y':
                    fp = open(school + ".csv","w",newline='\n')
                    kaoyan.save(mresult,file=fp)
                    fp.close()
    _pool.close()
    _pool.join()
    for fp in _fps:
        fp.close()