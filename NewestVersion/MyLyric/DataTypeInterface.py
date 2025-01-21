import datetime
import typing
from functools import wraps
from typing import Any, TypeGuard, Union, Callable
from typing_extensions import Protocol
from abc import abstractmethod

C = typing.TypeVar("C", bound="Comparable")


def var_type_guard(var: Any, var_type: tuple[Any, ...]) -> TypeGuard[Any]:
    # ================== Type Guard 🛡️ ==================
    # str 则是字符串相关都可以，包括 UserString
    for each_type in var_type:
        if issubclass(each_type, type(var)):
            break
    # 没有break说明没有找到对应的类型
    else:
        raise TypeError(str(var) + ' must be one of ' + str(var_type))

    # break 说明找到了对应的类型，返回 True
    return True

def int_leq_0_guard(var: int) -> TypeGuard[int]:
    if var > 0:
        return True
    else:
        raise ValueError(str(var) + ' must be large than 0')

def str_len_eq_1_guard(var: str) -> TypeGuard[str]:
    if len(var) == 1:
        return True
    else:
        raise ValueError(var + ' must be a string with length of 1')


class Comparable(Protocol):
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __lt__(self: C, other: C) -> bool:
        pass

    def __gt__(self: C, other: C) -> bool:
        return (not self < other) and self != other

    def __le__(self: C, other: C) -> bool:
        return self < other or self == other

    def __ge__(self: C, other: C) -> bool:
        return not self < other

    def __ne__(self: C, other: C) -> bool:
        return not self == other


class Calculable(Protocol):
    @abstractmethod
    def __add__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __sub__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __mul__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __truediv__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __floordiv__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __mod__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __pow__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __int__(self) -> Any:
        pass

    @abstractmethod
    def __float__(self) -> Any:
        pass


class BinaryCalculable(Protocol):
    @abstractmethod
    def __and__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __or__(self, other: Any) -> Any:
        pass


    @abstractmethod
    def __xor__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __lshift__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __rshift__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def __invert__(self) -> Any:
        pass



