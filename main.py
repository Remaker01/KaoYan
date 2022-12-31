import kaoyan
from typing import Iterable
from multiprocessing.pool import ThreadPool
def query():
    school = input("输入查询的学校 ")
    major = input("输入查询的专业代码 ")
    return school,major[0:4]
def showResult(lst:Iterable):
    print("本次查询结果为")
    for item in lst:
        for x in item:
            print(x,'\t',end='')
        print('')
if __name__ == "__main__":
    _pool = ThreadPool(processes=5)
    print("欢迎使用考研信息查询系统")
    while True:
        school,major = query()
        print("请输入下列操作之一\n1: 查询专业")
        print("2: 查询详细信息")
        print("其他任意键: 退出")
        choice = input()
        schools = kaoyan.getSchoolList(subject=major,school=school,stype="全日制")
        if len(schools) == 1:
            print("本次未查询到任何结果")
            continue
        if choice == '1':
            showResult(schools)
        elif choice == '2':
            if len(schools) > 2:
                print("结果较多，将把所有结果写入csv文件")
                for item in schools[1:]:
                    with open(item[0] + ".csv","w",newline='\n') as fp:
                        _pool.apply_async(kaoyan.getSchoolMajorList,args=(item[4],True,fp))
            else:
                mresult = kaoyan.getSchoolMajorList(schools[1][4],get_subj=True)
                showResult(mresult)
                x = input("按y保存为result.csv ")
                if x.lower() == 'y':
                    with open("result.csv","w",newline='\n') as fp:
                        kaoyan.save(mresult,file=fp)
        else:
            break
    _pool.close()
    _pool.join()