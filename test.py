'''测试模块'''
import kaoyan
from unittest import TestCase,TestProgram
import os.path
class TestKaoyan(TestCase):
    def __init__(self, methodName: str) -> None:
        self._result_seu_0839 = kaoyan.getSchoolList(subject="0839",school="东南大学",majoring="网络空间安全")
        super().__init__(methodName)
    def test_getSchoolList(self):
        # 1. 包含地区名、学校名(与地区对应)、学科代码、专业名
        result_seu_0839 = kaoyan.getSchoolList(subject="0839",location="江苏省",school="东南大学",majoring="网络空间安全")
        self.assertEqual(result_seu_0839[1],self._result_seu_0839[1])
        # 2.与上述相同,但学校名与地区不对应
        result_seu_0839_wrong = kaoyan.getSchoolList(subject="0839",location="江西省",school="东北大学",majoring="网络空间安全")
        self.assertEqual(len(result_seu_0839_wrong), 1)
        # 3. 学习方式为"1"
        result_0775 = kaoyan.getSchoolList(subject="0775",stype="1")
        self.assertEqual(len(result_0775), 26)
        # 4. 学习方式为"2"
        result_0854_nonfull = kaoyan.getSchoolList(subject="0854",stype="2",majoring="计算机技术",location="北京市")
        self.assertEqual(len(result_0854_nonfull), 7)
        # 5. 学习方式为"全日制"
        result_0775_2 = kaoyan.getSchoolList(subject="0775",stype="全日制")
        self.assertListEqual(result_0775[1],result_0775_2[1])
        # 6.学习方式为1
        result_0775_2 = kaoyan.getSchoolList(subject="0775",stype=1)
        self.assertListEqual(result_0775[1],result_0775_2[1])
        # 7. 省份名称不完整
        result_shanghai_0839 = kaoyan.getSchoolList(subject="0839",location="上海",majoring="网络空间安全")
        self.assertEqual(len(result_shanghai_0839),3)
        # 8. 错误
        with self.assertRaises(NotImplementedError):
            kaoyan.getSchoolList(subject="软件工程",stype="1")
    def test_getMajorList(self):
        # 1. False,None
        result = kaoyan.getSchoolMajorList(url=self._result_seu_0839[1][4])
        self.assertMultiLineEqual(result[0][5],"考试科目URL")
        # 2. False,"out.csv"
        OUTPUT = "out.csv"
        with open(OUTPUT,"w",newline='\n') as fp:
            kaoyan.getSchoolMajorList(url=self._result_seu_0839[1][4],output_fp=fp)
        self.assertTrue(os.path.exists(OUTPUT))
        # 3. True,None
        result = kaoyan.getSchoolMajorList(url=self._result_seu_0839[1][4],get_subj=True)
        self.assertMultiLineEqual(result[0][5],"考试科目")
        # 4. 非法URL
        with self.assertRaises(ValueError):
            kaoyan.getSchoolMajorList(url=self._result_seu_0839[1][3])
    def test_getExamSubjects(self):
        # 1. 常规科目
        result_seu_0839 = kaoyan.getSchoolMajorList(self._result_seu_0839[1][4],get_subj=True)
        subjects = result_seu_0839[1][5]
        self.assertMultiLineEqual(subjects[0],"英语（一）")
        self.assertIn("数学（一）",subjects[1])
        # 2. 管理类联考科目
        result_sdu_1253 = kaoyan.getSchoolList("1253",school="上海财经大学",stype="全日制")
        result_sdu_1253_ = kaoyan.getSchoolMajorList(result_sdu_1253[1][4],get_subj=True)
        subjects = result_sdu_1253_[1][5]
        self.assertEqual(len(subjects),2)
        self.assertIn("199",subjects[0])
        # 3. 非法科目
        with self.assertRaises(ValueError):
            kaoyan.getExamSubjects(url=kaoyan.HOST)
    def test_save(self):
        result_seu_0839 = kaoyan.getSchoolMajorList(self._result_seu_0839[1][4])
        # 1. 直接打印
        kaoyan.save(result_seu_0839)
        # 2.输出到文件(上面已测试过)
TestProgram(__name__)