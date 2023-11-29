from translator import translator
from machine import machine
import unittest


class MachineTest(unittest.TestCase):
    """ 处理器测试 """

    def setUp(self) -> None:
        print("Test beginning:")

    def tearDown(self) -> None:
        print("Test finished.")

    def test_hello(self):
        print("Testing hello")
        translator.translate("./asm/hello.asm", "./asm/target")
        result = machine.start("./asm/target", '')
        self.assertEqual(result, "Hello,world")

    def test_cat(self):
        print("Testing cat")
        translator.translate('./asm/cat.asm', './asm/target')
        result = machine.start('./asm/target', './asm/cat_test.txt')
        text = ''
        with open('asm/cat_test.txt') as f:
            text = f.read()
        self.assertEqual(result, text)

    def test_prob2(self):
        print("Testing prob2")
        translator.translate("./asm/prob2.asm", "./asm/target")
        result = machine.start("./asm/target", '')
        print("问题2答案：" + result)
        self.assertEqual(int(result), 4613732)


if __name__ == '__main__':
    unittest.main()
