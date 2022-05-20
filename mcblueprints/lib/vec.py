from typing import Any, Generic, TypeVar

from typing_extensions import Self

from mcblueprints.lib.normalizable_model import NormalizableGenericModel

__all__ = ["Vec3"]


T = TypeVar("T", bound=float)


class Vec3(NormalizableGenericModel, Generic[T]):
    x: T
    y: T
    z: T

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, list):
            return dict(x=value[0], y=value[1], z=value[2])  # type: ignore
        return value

    def __init__(self, x: T, y: T, z: T):
        super().__init__(x=x, y=y, z=z)  # type: ignore

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y, -self.z)

    def __pos__(self) -> Self:
        return self.__class__(+self.x, +self.y, +self.z)

    def __abs__(self) -> Self:
        return self.__class__(abs(self.x), abs(self.y), abs(self.z))

    def __add__(self, other: Self | T) -> Self:
        if not isinstance(other, self.__class__):
            other = self.__class__(other, other, other)
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

    def __radd__(self, other: Self | T) -> Self:
        if not isinstance(other, self.__class__):
            other = self.__class__(other, other, other)
        return self.__class__(other.x + self.x, other.y + self.y, other.z + self.z)

    def __sub__(self, other: Self | T) -> Self:
        if not isinstance(other, self.__class__):
            other = self.__class__(other, other, other)
        return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: T) -> Self:
        return self.__class__(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other: T) -> Self:
        return self.__class__(other * self.x, other * self.y, other * self.z)

    def __truediv__(self, other: T) -> Self:
        return self.__class__(self.x / other, self.y / other, self.z / other)

    def __floordiv__(self, other: T) -> Self:
        return self.__class__(self.x // other, self.y // other, self.z // other)

    def __mod__(self, other: T) -> Self:
        return self.__class__(self.x % other, self.y % other, self.z % other)

    def __pow__(self, other: T) -> Self:
        return self.__class__(self.x**other, self.y**other, self.z**other)

    @property
    def components(self) -> tuple[T, ...]:
        return self.x, self.y, self.z
