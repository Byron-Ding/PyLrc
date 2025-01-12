import copy
import datetime
import math
import re
import warnings
from typing import Callable, Union, Any, Optional
from typing import Final
from typing import Match, Pattern
from typing import Self

from collections import UserString

from functools import wraps

from DataTypeInterface import Comparable, Calculable, C
from DataTypeInterface import var_type_guard, int_leq_0_guard



class LyricTimeTab(Comparable, Calculable):
    """
    中文注释： \n
    LRC 歌词格式的 时间标签类

    拥有严格，普通，宽松，非常宽松四种模式
    strict: 严格模式，只接受[00:00.00]、<00:00.00>格式
    normal: 普通模式，接受[00:00[:.]{2-3}]、<00:00[:.]{2-3}>格式
    loose: 宽松模式，在normal基础上 允许 分钟秒钟毫秒任意位数，但是不允许括号缺失， 毫秒数可缺失 [ \\d* : \\d* [:.] \\d* ]
    very_loose: 非常宽松模式，允许括号缺失 [? \\d* : \\d* [:.] \\d* ]?

    self_defined: 自定义模式，自定义正则表达式
    但是必须包含
    <left_bracket>
    <minutes> <minutes_seconds_seperator>
    <seconds> <seconds_milliseconds_seperator>
    <milliseconds>
    <right_bracket>

    English Comments: \n
    LRC Lyrics Format Time Tab Class
    """
    # 时间标签转换常量
    CONVERSION_TIME_60: int = 60
    CONVERSION_TIME_1000: int = 1000
    CONVERSION_TIME_100: int = 100

    # 尖括号正则表达式
    ANGLE_BRACKETS_REGREX: str = r'\<|\>'
    # 方括号正则表达式
    SQUARE_BRACKETS_REGREX: str = r'\[|\]'

    '''
    判断时间标签是否合法
    拥有严格，普通，宽松，非常宽松四种模式
    strict: 严格模式，只接受[00:00.00]、<00:00.00>格式
    normal: 普通模式，接受[00:00[:.]{2-3}]、<00:00[:.]{2-3}>格式
    loose: 宽松模式，在normal基础上 允许 分钟秒钟毫秒任意位数，但是不允许括号缺失， 毫秒数可缺失 [ \\d* : \\d* [:.] \\d* ]
    very_loose: 非常宽松模式，允许括号缺失 [? \\d* : \\d* [:.] \\d* ]?
    
    self_defined: 自定义模式，自定义正则表达式
    但是必须包含
    <left_bracket>
    <minutes> <minutes_seconds_seperator>
    <seconds> <seconds_milliseconds_seperator>
    <milliseconds>
    <right_bracket>
    
    # 规范里面说了，分钟位和秒钟位必须有数字
    '''
    MODE_TYPE: Final[tuple[str, ...]] = ('strict', 'normal', 'loose', 'very_loose', 'self_defined')

    # REGREX group name
    # 自定义必须包含的组名
    SELF_DEFINED_GROUP_NAME: Final[set[str]] = {'left_bracket', 'minutes', 'minutes_seconds_seperator',
                                                'seconds', 'seconds_milliseconds_seperator', 'milliseconds',
                                                'right_bracket'}


    # 歌词每个字的时间标签的正则表达式 <>
    # 严格模式时间标签的正则表达式
    TIME_TAB_STRICT_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                                       r'(?P<minutes>\d{2})'
                                                                       r'(?P<minutes_seconds_seperator>:)'
                                                                       r'(?P<seconds>\d{2})'
                                                                       r'(?P<seconds_milliseconds_seperator>\.)'
                                                                       r'(?P<milliseconds>\d{2})'
                                                                       r'(?P<right_bracket>[]>])')
    # 普通模式时间标签的正则表达式
    TIME_TAB_NORMAL_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                                       r'(?P<minutes>\d{2})'
                                                                       r'(?P<minutes_seconds_seperator>:)'
                                                                       r'(?P<seconds>\d{2})'
                                                                       r'(?P<seconds_milliseconds_seperator>[:.])'
                                                                       r'(?P<milliseconds>\d{2,3})'
                                                                       r'(?P<right_bracket>[]>])')
    # 宽松模式时间标签的正则表达式
    TIME_TAB_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                                      r'(?P<minutes>\d*)'
                                                                      r'(?P<minutes_seconds_seperator>:)'
                                                                      r'(?P<seconds>\d*)'
                                                                      r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                      r'(?P<milliseconds>\d*)?'
                                                                      r'(?P<right_bracket>[]>])')
    # 非常宽松模式时间标签的正则表达式
    TIME_TAB_VERY_LOOSE_REGREX: Final[Pattern[str]] = re.compile(r'(?P<left_bracket>[\[<])'
                                                                           r'(?P<minutes>\d*)'
                                                                           r'(?P<minutes_seconds_seperator>:)'
                                                                           r'(?P<seconds>\d*)'
                                                                           r'(?P<seconds_milliseconds_seperator>[:.])?'
                                                                           r'(?P<milliseconds>\d*)?'
                                                                           r'(?P<right_bracket>[]>])')

    # 正则表达式列表
    TIME_TAB_DIFFERENT_MODE_REGREX: dict[str, Pattern[str]] = dict({
        MODE_TYPE[0]: TIME_TAB_STRICT_REGREX,
        MODE_TYPE[1]: TIME_TAB_NORMAL_REGREX,
        MODE_TYPE[2]: TIME_TAB_LOOSE_REGREX,
        MODE_TYPE[3]: TIME_TAB_VERY_LOOSE_REGREX
    })

    """
    接受一个时间标签字符串，分离出时间标签的各个部分
    """

    def __init__(self,
                 tab: Optional[str | UserString],
                 mode: tuple[str, Optional[Pattern[str]]] = ('normal', None)) -> None:

        # ================== 类的属性 ==================
        # 时间标签原始字符串，作为拷贝，
        self._original_time_tab: Optional[str] = tab
        # 时间标签字符串
        self._current_time_tab: Optional[str] = tab
        # 模式 + 自定义正则表达式
        self._mode: tuple[str, Optional[Pattern[str]]] = mode

        self._match_result: Optional[Match[str]] = None

        # 时间标签类型 [] or <> or None
        self._brackets: Optional[list[str, str]] = None
        # 时间戳
        self._time_stamp: Optional[datetime.timedelta] = None

        # 分钟秒钟分割符
        self._minutes_seconds_seperator: Optional[str] = None
        # 秒钟毫秒分割符
        self._seconds_milliseconds_seperator: Optional[str] = None

        # 时间标签分钟位数
        self._len_of_minutes: Optional[int | math.inf] = None  # 标准: math.inf
        # 时间标签秒位数
        self._len_of_seconds: Optional[int] = None  # 标准: 2
        # 时间标签毫秒位数
        self._len_of_millisecond: Optional[int] = None  # 标准: 2


        # ================== 类型检查 🛂🛡️ ==================
        # ------------------ tab ------------------
        # str 则是字符串相关都可以，包括 UserString
        # None 严格为 None
        var_type_guard(tab, (str, UserString, None))

        # ------------------ mode ------------------
        # mode 必须是 str + self_defined_regex
        # 必须是 strict, normal, loose, very_loose, self_defined
        var_type_guard(mode, (tuple, ))
        # 必须是 strict, normal, loose, very_loose 或者 self_defined
        self.__mode_guard()


        # ================== 初始化 预处理 ==================
        # 预分离时间标签
        # None: 初始化
        # str: 时间标签字符串
        self._initialize_time_tab()


    # 返回时间标签时间戳
    def __int__(self):
        return self.get_millisecond_time_stamp()

    # 返回时间标签字符串
    def __str__(self):
        return self._current_time_tab

    # 返回时间标签列表
    def __repr__(self):
        return self._current_time_tab, self._mode

    """
    预分离标签，判断是否合法，分离出时间标签的各个部分，储存到类的属性中，供其他方法调用
    私有方法
    """

    def _initialize_time_tab(self) -> None:
        """
        中文注释：
        预分离标签，判断是否合法，分离出时间标签的各个部分，储存到类的属性中，供其他方法调用
        私有方法

        English comment:
        Pre-separate the label, judge whether it is legal, separate the various parts of the time label,
        and store them in the properties of the class for other methods to call
        Private method

        :return: None
        """
        # None 则初始化，不会触及初始标签
        # if: 初始标签为 None
        if self.current_time_tab is None:
            # 匹配结果（粗处理）
            self._match_result = None

            # 描述符
            self._len_of_minutes = None
            self._len_of_seconds = None
            self._len_of_millisecond = None

            # 括号
            self._brackets = None

            # 分割符
            self._minutes_seconds_seperator = None
            self._seconds_milliseconds_seperator = None

            # 时间
            self._time_stamp = None

            return

        # else: 其他情况
        # 前面已经检查过了，直接匹配
        # 分离时间标签
        if self.mode == self.MODE_TYPE[4]:
            self._match_result = self.mode[1].match(self.current_time_tab)

        # 匹配结果（粗处理）
        self._match_result = self.TIME_TAB_DIFFERENT_MODE_REGREX[self.mode[0]].match(self.current_time_tab)

        # ================== 判断是否合法 ==================
        if self._match_result is None:
            raise ValueError('Time tab is not valid: ' + self.current_time_tab + "under mode: " + self.mode[0])


        # ================== 分离时间/分隔符/括号 ==================
        # 添加到类的属性中
        # 描述符
        self._len_of_minutes = len(self._match_result.group('minutes'))
        self._len_of_seconds = len(self._match_result.group('seconds'))
        self._len_of_millisecond = len(self._match_result.group('milliseconds'))

        # 括号
        self._brackets = (self._match_result.group('left_bracket'), self._match_result.group('right_bracket'))

        # 分隔符
        self._minutes_seconds_seperator = self._match_result.group('minutes_seconds_seperator')
        self._seconds_milliseconds_seperator = self._match_result.group('seconds_milliseconds_seperator')

        # ================== 时间戳 ==================
        # ------------------ 转整数 ------------------
        # 自动计算时间戳
        # 要考虑没有("")的情况
        # "" 会被转换成 0
        minutes_int: int
        seconds_int: int
        milliseconds_int: int
        # 防止有 微秒 的情况
        microseconds_int: float

        # 时间
        minutes_int = int(self.match_result.group('minutes')) \
            if self.match_result.group('minutes') != "" else 0
        seconds_int = int(self.match_result.group('seconds')) \
            if self.match_result.group('seconds') != "" else 0

        # 毫秒特殊处理，小数点左边
        # 先标准化为3位（补全则补全0）（4位是因为需要微妙）
        milliseconds_str: str = self.match_result.group('milliseconds').rjust(4, "0")
        # 毫秒
        milliseconds_int = int(milliseconds_str[0:3])
        # 防止微秒
        microseconds_int = int(milliseconds_str[3:]) / (10 ** (len(milliseconds_str) - 3))

        # ------------------ 计算时间戳 ------------------
        # 调用函数，计算时间戳
        # 使用python 自带的 datetime.timedelta
        self._time_stamp = datetime.timedelta(minutes=minutes_int,
                                              seconds=seconds_int,
                                              milliseconds=milliseconds_int,
                                              microseconds=microseconds_int)


    def __mode_guard(self) -> None:
        # 先检查mode 是否是 self_defined
        # 不是则 self_defined_regex 必须是 None
        # 否则报 Warning
        # 是则 self_defined_regex 必须是 Pattern[str]
        if self.mode[0] != self.MODE_TYPE[4]:
            if self.mode[1] is not None:
                # warning
                warnings.warn('Mode is not "self_defined", self_defined_regex must be None')
            else:
                pass
        else:
            if isinstance(self.mode[0], Pattern):
                # check whether the group name is correct
                # 检查组名是否正确
                if self.SELF_DEFINED_GROUP_NAME.issubset(tuple(self.mode[1].groupindex.keys())):
                    pass
                else:
                    raise ValueError('The group name of self_defined_regex is not correct; \
                                     should contain ' + str(self.SELF_DEFINED_GROUP_NAME))
            else:
                raise TypeError('Mode is "self_defined", self_defined_regex must be Pattern[str]')


    def get_millisecond_time_stamp(self) -> float:
        """
        中文：\n
        计算时间戳，分、秒、毫秒，小时（可选）\n
        返回毫秒位单位的时间戳(3位)

        English: \n
        Calculate the time stamp, minute, second, millisecond, hour (optional) \n
        Return the time stamp in milliseconds_str (3 digits)

        :return: 毫秒位单位的时间戳(3位) The time stamp in milliseconds_str (3 digits)
        """
        if self._time_stamp is None:
            raise ValueError("Not Initialized Time Stamp")

        # 括号不影响，不会转为元组
        return (int(self._time_stamp.total_seconds()) * self.CONVERSION_TIME_1000 +
                int(self._time_stamp.microseconds // self.CONVERSION_TIME_1000)
                )

    # ======================== 更新 tab，需要重新初始化 ========================
    @property
    def current_time_tab(self) -> str:
        return self._current_time_tab

    @current_time_tab.setter
    def current_time_tab(self, value: str | UserString) -> None:
        # ================== Type Guard 🛡️ ==================
        # str 则是字符串相关都可以，包括 UserString
        var_type_guard(value, (str, UserString))
        self._current_time_tab = value
        self._initialize_time_tab()

    @property
    def mode(self) -> tuple[str, Optional[Pattern[str]]]:
        return self._mode

    # 允许换一种匹配模式
    @mode.setter
    def mode(self, value: tuple[str, Optional[Pattern[str]]]):
        # ================== Type Guard 🛡️ ==================
        # mode 必须是 str + self_defined_regex
        var_type_guard(value, (tuple, ))
        # 必须是 strict, normal, loose, very_loose 或者 self_defined
        self.__mode_guard(value)

        self._mode = value
        self._initialize_time_tab()

    # ======================== 不更新 tab，特殊值 ========================
    @property
    def original_time_tab(self) -> str:
        return self._original_time_tab

    # 匹配结果不可更改
    @property
    def match_result(self) -> Match[str]:
        return self._match_result

    # ======================== 不更新 tab，因为最后是分隔符+时间+括号拼接 ========================
    # tab更新才需要重新初始化
    @property
    def brackets(self) -> list[str, str]:
        return self._brackets

    @brackets.setter
    def brackets(self, value: list[str, str]) -> None:
        var_type_guard(value, (list, ))
        self._brackets = value


    @property
    def minutes_seconds_seperator(self) -> str:
        return self._minutes_seconds_seperator

    @minutes_seconds_seperator.setter
    def minutes_seconds_seperator(self, value: str) -> None:
        var_type_guard(value, (str, ))
        self._minutes_seconds_seperator = value


    @property
    def seconds_milliseconds_seperator(self) -> str:
        return self._seconds_milliseconds_seperator

    @seconds_milliseconds_seperator.setter
    def seconds_milliseconds_seperator(self, value: str) -> None:
        var_type_guard(value, (str, ))
        self._seconds_milliseconds_seperator = value


    @property
    def time_stamp(self) -> datetime.timedelta:
        return self._time_stamp

    @time_stamp.setter
    def time_stamp(self, value: datetime.timedelta) -> None:
        var_type_guard(value, (datetime.timedelta, ))
        self._time_stamp = value

    # ======================== len 时间标签位数，set也不更新tab ========================
    @property
    def len_of_minutes(self) -> int:
        return self._len_of_minutes

    @len_of_minutes.setter
    def len_of_minutes(self, value: int) -> None:
        # 范围检查
        int_leq_0_guard(value)
        self._len_of_minutes = value


    @property
    def len_of_seconds(self) -> int:
        return self._len_of_seconds

    @len_of_seconds.setter
    def len_of_seconds(self, value: int) -> None:
        # 范围检查
        int_leq_0_guard(value)
        self._len_of_seconds = value


    @property
    def len_of_millisecond(self) -> int:
        return self._len_of_millisecond

    @len_of_millisecond.setter
    def len_of_millisecond(self, value: int) -> None:
        # 范围检查
        int_leq_0_guard(value)
        self._len_of_millisecond = value

    # ======================== 其他方法 ========================

    """
    规范时间戳，按需求转为len_of_millisecond位的时间戳
    """
    def get_standard_time_stamp(self) -> int:
        """
        中文：\n
        返回规范的时间戳，以秒为单位

        English: \n
        Return the standard time stamp in seconds

        :return: 规范的时间戳 The standard time stamp
        """
        return int(self.time_stamp.total_seconds())

    class __OperatorIntFloadGuard(object):
        def __init__(self, operator_name: str):
            self.operator_name = operator_name

        def __call__(self,
                     operator: Callable[["LyricTimeTab",
                                        Union[int, float, "LyricTimeTab", datetime.timedelta]
                                        ],
                     "LyricTimeTab"]
                     ) -> Callable[[Any, Any], "LyricTimeTab"]:
            @wraps(operator)
            def decorated_operator(obj_instance, other):
                # 调用的时候一定要加入self的参数，self在这里不会被自动传入
                # 实例化类
                if isinstance(other, LyricTimeTab):
                    other: LyricTimeTab
                    return operator(obj_instance, other.time_stamp)

                # 可以和 int 或者 float 加减乘除
                elif isinstance(other, (int, float)):
                    return operator(obj_instance, other)

                elif isinstance(other, datetime.timedelta):
                    return operator(obj_instance, other.total_seconds())

                else:
                    raise TypeError("LyricTimeTab is not valid for" + self.operator_name +
                                    " with type " + str(type(other)) + ": " + str(other))

            return decorated_operator

    @__OperatorIntFloadGuard(operator_name="+")
    def __add__(self, other: Any) -> Any:
        # 复制之后再加，不改变原来的值
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp += datetime.timedelta(seconds=other)

        return returned_time_stamp

    @__OperatorIntFloadGuard(operator_name="-")
    def __sub__(self, other: Any) -> Any:
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp -= datetime.timedelta(seconds=other)

        return returned_time_stamp

    @__OperatorIntFloadGuard(operator_name="*")
    def __mul__(self, other: Any) -> Any:
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp *= datetime.timedelta(seconds=other)

        return returned_time_stamp

    @__OperatorIntFloadGuard(operator_name="/")
    def __truediv__(self, other: Any) -> Any:
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp /= datetime.timedelta(seconds=other)

        return returned_time_stamp

    @__OperatorIntFloadGuard(operator_name="//")
    def __floordiv__(self, other: Any) -> Any:
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp //= datetime.timedelta(seconds=other)

        return returned_time_stamp

    @__OperatorIntFloadGuard(operator_name="%")
    def __mod__(self, other: Any) -> Any:
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp %= datetime.timedelta(seconds=other)

        return returned_time_stamp

    @__OperatorIntFloadGuard(operator_name="**")
    def __pow__(self, other: Any) -> Any:
        returned_time_stamp: "LyricTimeTab" = copy.deepcopy(self)
        returned_time_stamp.time_stamp **= datetime.timedelta(seconds=other)

        return returned_time_stamp

    def __float__(self) -> Any:
        return self.time_stamp.total_seconds()

    def __eq__(self, other: Any) -> bool:
        # 实例化类
        if isinstance(other, LyricTimeTab):
            return self.time_stamp == other.time_stamp
        # int 或者 float
        elif isinstance(other, (int, float)):
            return self.time_stamp.total_seconds() == other
        # 非实例化类
        elif other == LyricTimeTab:
            return self.time_stamp == other.time_stamp
        else:
            raise TypeError("LyricTimeTab is not comparable with type " + str(type(other)) + " " + str(other))

    def __lt__(self: C, other: C) -> bool:
        # 实例化类
        if isinstance(other, LyricTimeTab):
            return self.time_stamp < other.time_stamp
        # int 或者 float
        elif isinstance(other, (int, float)):
            return self.time_stamp.total_seconds() < other
        # 非实例化类 也不可比较
        else:
            raise TypeError("LyricTimeTab is not comparable with type " + str(type(other)) + " " + str(other))

    @classmethod
    def convert_time_stamp_to_time_tab_static(cls,
                                              time_stamp: datetime.timedelta,
                                              ignore_minute_second_zero: bool = False,
                                              len_of_millisecond_output: Optional[int] = 2,
                                              brackets: tuple[str, str] = ("[", "]"),
                                              seperator: tuple[str, str] = (":", ".")) -> str:
        """
        中文：\n
        将时间戳转为时间标签

        English: \n
        It is a staticmethod. It converts the time stamp of time tag in to a tag.

        :param time_stamp: 时间戳 The time stamp
        :param ignore_minute_second_zero: 是否忽略分秒中的数字0 Whether to ignore the number 0 in minutes and seconds
        :param len_of_millisecond_output: 输出的时间戳的毫秒位的位数 The number of milliseconds_str of the output time stamp
        :param brackets: 括号 The brackets
        :param seperator: 分隔符 The seperator
        :return: 时间标签 The time tag
        """
        minutes_int: int
        seconds_int: int
        microsecond_int: int

        minutes_str: str
        seconds_str: str
        millisecond_str: str

        time_tab_output: str

        # 计算分秒毫秒，输入的时间戳是len_of_millisecond位相关的
        # // 返回int, 不用管类型提醒，第一行int可以不用加
        minutes_int = int(time_stamp.total_seconds() // cls.CONVERSION_TIME_60)
        seconds_int = int(time_stamp.total_seconds() % cls.CONVERSION_TIME_60)
        microsecond_int = time_stamp.microseconds

        if ignore_minute_second_zero:
            # 毫秒
            millisecond_int = int(microsecond_int / cls.CONVERSION_TIME_1000)

            # 加上 左右括号 和 分隔符
            # 格式化字符串
            time_tab_output = f"{brackets[0]}" \
                              f"{minutes_int}" \
                              f"{seperator[0]}" \
                              f"{seconds_int}" \
                              f"{seperator[1]}" \
                              f"{millisecond_int}" \
                              f"{brackets[1]}"
        # else:
        # 分 秒
        minutes_str = str(minutes_int)
        seconds_str = str(seconds_int)
        # 不足则左边补0
        seconds_str = seconds_str.rjust(2, "0")
        minutes_str = minutes_str.rjust(2, "0")

        # 毫秒
        # 如果有小数位，抹去小数位
        millisecond_int = int(millisecond_int)
        # 转为字符串
        millisecond_str = str(millisecond_int)
        # 输出的毫秒位长度
        # 不足则右边补0
        millisecond_str = millisecond_str.ljust(len_of_millisecond_output, "0")
        # 截取
        millisecond_str = millisecond_str[:len_of_millisecond_output]


        # 返回最终结果
        return time_tab_output

    def convert_to_time_tab(self,
                            len_of_millisecond_inputted: int = 3,
                            len_of_millisecond_output: int = 2,
                            brackets: tuple[str, str] = ("[", "]"),
                            seperator: tuple[str, str] = (":", ".")) -> str:
        """
        中文：\n
        将时间戳转为时间标签，对实例本身进行操作

        English: \n
        It converts the time stamp of time tag in to a tag. It operates on the instance itself.

        :param len_of_millisecond_inputted: 输入的时间戳的毫秒位的位数 The number of milliseconds_str of the input time stamp
            默认在实例化类的时候已经转换成了3位毫秒位的时间戳 Default is 3 digits in property time_stamp of class LyricTimeTab
        :param len_of_millisecond_output: 输出的时间戳的毫秒位的位数 The number of milliseconds_str of the output time stamp
        :param brackets: 括号 The brackets
        :param seperator: 分隔符 The seperator
        :return: 时间标签 The time tag
        """
        # 如果time stamp是None，返回空字符串，表明没有时间标签
        if self.time_stamp is None:
            return ""
        else:
            return LyricTimeTab.convert_time_stamp_to_time_tab_static(self.time_stamp,
                                                                      len_of_millisecond_inputted,
                                                                      len_of_millisecond_output,
                                                                      brackets,
                                                                      seperator)

    # 返回自身
    def shift_time(self,
                   minutes: int,
                   seconds: int,
                   milliseconds: int,
                   len_of_millisecond: int = 3
                   ) -> Self:
        """
        中文：\n
        将时间标签向前或向后移动

        English: \n
        Move the time tag forward or backward

        :param minutes: 分钟数 The number of minutes_str
        :param seconds: 秒数 The number of seconds_str
        :param milliseconds: 毫秒数 The number of milliseconds_str
        :param len_of_millisecond: 毫秒位的位数 The number of milliseconds_str
        """

        # 转毫秒位为3位（规范化）
        milliseconds = int(milliseconds * (10 ** (3 - len_of_millisecond)))

        # 修改属性
        self.minutes_str += minutes
        self.seconds_str += seconds
        self.milliseconds_str += milliseconds

        # 修改时间列表
        self.time_list[1] += minutes
        self.time_list[3] += seconds
        self.time_list[5] += milliseconds

        # 计算时间戳
        time_stamp_shift: float = LyricTimeTab.calculate_time_stamp(minutes, seconds, milliseconds)

        # 移动时间戳
        self.time_stamp += time_stamp_shift

        # 修改时间标签
        self._current_time_tab = self.convert_to_time_tab()

        return self

    # 返回自身
    def format_time_tab_self(self,
                             brackets: Optional[tuple[str, str]],
                             seperator: Optional[tuple[str, str]]
                             ) -> Self:
        """
        中文：\n
        格式化时间标签对象本身 \n
        把秒 限制在0-59之间 \n
        把毫秒 限制在0-999之间 \n
        并且补全括号，分隔符 \n
        如果brackets和seperator为None，则不补全括号，分隔符
        返回规范化后的自身

        English: \n
        Format the time tag object itself\n
        Limit the seconds_str between 0 and 59 \n
        Limit the milliseconds_str between 0 and 999 \n
        And complete the brackets and seperator \n
        If brackets and seperator are None, do not complete the brackets and seperator
        Return the normalized self


        :return: self
        """

        # ==================== 时分秒毫秒单位溢出处理 ==================== #

        # 预处理 类型转换
        # 转为float
        minutes: int = int(self.minutes_str)
        seconds: int = int(self.seconds_str)
        milliseconds: float = float(self.milliseconds_str)

        # 毫秒
        # 如果大于等于1000
        if milliseconds >= 1000:
            # 计算多余的秒数
            seconds_extra: int = int(milliseconds // 1000)
            # 计算剩余的毫秒数
            milliseconds = milliseconds % 1000
            # 秒数加上多余的秒数
            seconds += seconds_extra

        # 如果小于0
        elif milliseconds < 0:
            # 注意这里 用的是负数相加，milliseconds是负数，所以退位减一是负一
            # 计算多余的秒数
            seconds_extra: int = -1 + int(milliseconds // 1000)
            # 计算剩余的毫秒数
            milliseconds = 1000 + milliseconds % 1000
            # 秒数加上多余的秒数
            seconds += seconds_extra

        # 秒
        # 如果大于等于60
        if seconds >= 60:
            # 计算多余的分钟数
            minutes_extra: int = int(seconds // 60)
            # 计算剩余的秒数
            seconds = seconds % 60
            # 分钟数加上多余的分钟数
            minutes += minutes_extra

        # 如果小于0
        elif seconds < 0:
            # 注意这里 用的是负数相加，seconds是负数，所以退位减一是负一
            # 计算多余的分钟数
            minutes_extra: int = -1 + int(seconds // 60)
            # 计算剩余的秒数
            seconds = 60 + seconds % 60
            # 分钟数加上多余的分钟数
            minutes += minutes_extra

        # 赋值回去
        self.minutes_str = str(minutes)
        self.seconds_str = str(seconds)
        self.milliseconds_str = str(milliseconds)

        # ==================== 括号分隔符补全 ==================== #

        # 如果brackets和seperator为None，则不补全括号，分隔符
        if brackets is not None:
            self.brackets = brackets

            # 也赋值到时间列表内
            self.time_list[0] = self.brackets[0]
            self.time_list[6] = self.brackets[1]

        if seperator is not None:
            self.minutes_seconds_seperator = seperator[0]
            self.seconds_milliseconds_seperator = seperator[1]

            # 也赋值到时间列表内
            self.time_list[2] = self.minutes_seconds_seperator
            self.time_list[4] = self.seconds_milliseconds_seperator

        # ==================== 修改时间列表内的分秒毫秒 ==================== #
        self.time_list[1] = minutes
        self.time_list[3] = seconds
        self.time_list[5] = milliseconds

        return self

    def isspace(self) -> bool:
        return self.original_time_tab.isspace()


"""
中文：\n
测试内容

English: \n
Test content
"""
if __name__ == '__main__':
    # 打印正则表达式列表

    # 测试时间标签 += 运算符
    time_tab = LyricTimeTab("[00:00.00]", ('normal', "None"))
    time_tab = time_tab + 1
    print(time_tab.convert_to_time_tab())
