from collections import UserString

from bidict import bidict
from typing_extensions import LiteralString

from LyricTimeTab import LyricTimeTab
from typing import Optional, Final

from DataTypeInterface import var_type_guard, str_len_eq_1_guard

"""
每个字符的类，继承自字符串类，
包含时间和字符
"""


class LyricCharacter(UserString):
    """
    每个歌词字符的类，继承自字符串类。

    Each lyric character class, inherited from the string class.

    :param character: the character
    :param time_tab: the time tab
    """
    # 在原有的列表后面追加新的元组
    CHINESE_OR_CHU_NOM_RANGES: Final[bidict[str: tuple[int, int]]] = bidict(
        dict(
            # CJKV 汉字字符集Unicode编码范围
            # 汉字和喃字的 Unicode 区间
            CJK_RADICAL_COMPLEMENT=(0x2E80, 0x2EFF),  # CJK 部首补充
            KANGXI_RADICALS=(0x2F00, 0x2FDF),  # 康熙部首

            CJK_UNIFIED_IDEOGRAPHS=(0x4E00, 0x9FFF),  # CJK 统一表意符号
            CJK_COMPATIBILITY_IDEOGRAPHS=(0xF900, 0xFAFF),  # CJK 兼容表意符号
            CJK_COMPATIBILITY_IDEOGRAPHS_SUPPLEMENT=(0x2F800, 0x2FA1F),  # CJK 兼容表意符号补充

            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_A=(0x3400, 0x4DBF),  # CJK 统一表意符号扩展 A
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_B=(0x20000, 0x2A6DF),  # CJK 统一表意符号扩展 B
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_C=(0x2A700, 0x2B73F),  # CJK 统一表意符号扩展 C
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_D=(0x2B740, 0x2B81F),  # CJK 统一表意符号扩展 D
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_E=(0x2B820, 0x2CEAF),  # CJK 统一表意符号扩展 E
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_F=(0x2CEB0, 0x2EBEF),  # CJK 统一表意符号扩展 F
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_G=(0x30000, 0x3134F),  # CJK 统一表意符号扩展 G
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_H=(0x31350, 0x323AF),  # CJK 统一表意符号扩展 H
            CJK_UNIFIED_IDEOGRAPHS_EXTENSION_I=(0x2EBF0, 0x2EE5F),  # CJK 统一表意符号扩展 I

            NUSHU=(0xAA60, 0xAA7F),  # 喃字补充

            IDEOGRAPHIC_NUMBER_ZERO=(0x3007, 0x3007),  # 〇
            IDEOGRAPHIC_ITERATION_MARK=(0x3005, 0x3005),  # 汉字叠字符号々
            IDEOGRAPHIC_ITERATION_MARKS=(0x303B, 0x303B),  # 汉字叠字符号〻
            IDEOGRAPHIC_SYMBOL_FOR_CORAL=(0x20120, 0x20120),  # 多字叠字符号𠄠
            TANGUT_COMPONENTS=(0x16FE3, 0x16FE3),  # 多字叠字符号𖿣
            KANGXI_RADICALS_SUPPLEMENT=(0x2E80, 0x2E80)  # ⺀
        )
    )

    """
    重写init，添加时间属性
    """

    def __init__(self,
                 character: str,
                 time_tab: Optional[LyricTimeTab] = None):
        # ================== Type Guard 🛡️ ==================
        # 如果不是字符串，抛出异常
        var_type_guard(character, (str,))
        # 如果不是单个字符，抛出异常
        str_len_eq_1_guard(character)

        # ================== Time 🕒 ==================
        self.initial_data: str = character

        super().__init__(character)

        # 时间
        # 调用Time_tab类
        self.time_tab: Optional[LyricTimeTab] = time_tab

        # 如果有
        # 括号更新为 <>，这是单个字符的时间标签
        if self.time_tab is not None:
            self.time_tab.brackets = ('<', '>')


    @staticmethod
    def is_in_unicode_range(input_string: str, unicode_range: tuple[int, int]) -> bool:
        """
        Loop the input string and check if all characters are in the Unicode range.

        遍历输入字符串并检查所有字符是否在 Unicode 范围内。

        :param input_string: the input string
        :param unicode_range: the Unicode range
        :return: True if all characters are in the Unicode range, False otherwise
        """
        for each_character in input_string:
            # 获取字符的 Unicode 编码
            char_code: int = ord(each_character)
            start, end = unicode_range

            # if not in the range, return False
            if not (start <= char_code <= end):
                # goto False
                break
        # if not break, means every character is in the range
        else:
            return True

        # label False
        return False

    @classmethod
    def is_cjkv_classmethod(cls, single_character: str) -> bool:
        """
        Check if the input character is a CJKV character.

        检查输入字符是否为 CJKV 字符。

        :param single_character: the input character
        :return: True if the input character is a CJKV character, False otherwise
        """
        # 遍历 CJKV 字符集
        for each_unicode_range in cls.CHINESE_OR_CHU_NOM_RANGES.values():
            # 如果字符在范围内，中断，退出循环，返回 True
            # 否则 继续下一个范围检测，返回 False
            if not cls.is_in_unicode_range(single_character, each_unicode_range):
                pass
            else:
                # goto False
                break
        # 如果没有退出循环，说明字符不在所有范围内，所有检测都失败了
        else:
            return False

        # 返回 False
        # label False
        return True

    def is_cjkv(self) -> bool:
        """
        Check if the character is a CJKV character.

        检查字符是否为 CJKV 字符。

        :return: True if the character is a CJKV character, False otherwise
        """
        return self.is_cjkv_classmethod(self.data)

    def is_empty(self) -> bool:
        """
        Check if the character is empty.

        检查字符是否为空。

        :return: True if the character is empty, False otherwise
        """
        return self.data == ''

    def get_timed_character(self,
                            min_len_of_minutes = 2,
                            min_len_of_seconds = 2,
                            min_len_of_millisecond = 2,
                            cut_off_millisecond = False,
                            brackets = ('<', '>'),
                            seperator = (':', '.')
                            ) -> str:
        """
        Get the timed character.

        获取带时间的字符。

        :return: the timed character
        """
        if self.time_tab is None:
            return self.data
        else:
            return self.time_tab.convert_to_time_tab(min_len_of_minutes=min_len_of_minutes,
                                                     min_len_of_seconds=min_len_of_seconds,
                                                     min_len_of_millisecond=min_len_of_millisecond,
                                                     cut_off_millisecond=cut_off_millisecond,
                                                     brackets=brackets,
                                                     seperator=seperator
                                                     ) + self.data

# 测试
if __name__ == '__main__':
    a_time_tab = LyricTimeTab("<00:00.50>", ("strict", None))

    a = LyricCharacter('覗', a_time_tab)
    print(a)
    print(a.time_tab)
    print(a)
    print(a.is_in_unicode_range('他', LyricCharacter.CHINESE_OR_CHU_NOM_RANGES['CJK_UNIFIED_IDEOGRAPHS']))
    print(LyricCharacter.is_cjkv_classmethod('々'))
