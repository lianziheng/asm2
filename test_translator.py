from translator import translator
import unittest
import filecmp


class TranslatorTest(unittest.TestCase):
    """ 翻译测试 """

    def setUp(self) -> None:
        print("Test of translator beginning:")

    def tearDown(self) -> None:
        print("Test of translator finished.")

    def test_hello(self):
        print("Testing hello")
        translator.translate("./asm/hello.asm", "./tmp/result.tmp")
        status = filecmp.cmp('./tmp/result.tmp', './target/hello')
        self.assertEqual(status, True)

    def test_cat(self):
        print("Testing cat")
        translator.translate("./asm/cat.asm", "./tmp/result.tmp")
        status = filecmp.cmp('./tmp/result.tmp', './target/cat')
        self.assertEqual(status, True)

    def test_prob2(self):
        print("Testing prob2")
        translator.translate("./asm/prob2.asm", "./tmp/result.tmp")
        status = filecmp.cmp('./tmp/result.tmp', './target/prob2')
        self.assertEqual(status, True)
