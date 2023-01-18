## 考研信息查询脚本
自动抓取研招网上的招生信息
使用的第三方库:urllib3,lxml
kaoyan.py使用示例
```
import kaoyan
from multiprocessing.pool import ThreadPool
all = kaoyan.getSchoolList(subject="0839",stype="全日制")
details = kaoyan.getSchoolMajorList(all[1][4])
details_with_subjs = kaoyan.getSchoolMajorList(all[2][4],get_subj=True)
# 获取学校列表后进行并发请求。建议并发时指定输出，直接使用getSchoolMajorList的返回值可导致详细信息和学校不对应
pool = ThreadPool()
fps = []
for each in all:
    fp = open(each[0],"w")
    pool.apply_async(kaoyan.getSchoolMajorList(each[4],False,fp))
    fps.append(fp)
for fp in fps:
    fp.close()
```

使用main.py:直接运行脚本，或使用py_compile,pyinstaller编译后运行

**欢迎提出意见与建议**