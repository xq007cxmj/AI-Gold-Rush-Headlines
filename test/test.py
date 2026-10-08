from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field


class UserInfoResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


# 模拟 ORM 对象
class UserInfoORM:
    def __init__(self):
        self.id = 1
        self.name = "Alice"


@dataclass
class UserInfoORMpro:
    id: int = 18
    name: str = "张三"


class UserORM:
    def __init__(self):
        self.token = "abc123"
        self.user_info = UserInfoORM()
        # self.user_info = {"id": 1, "name": "Alice"}
        # self.user_info = asdict(UserInfoORMpro())


orm_user = UserORM()
print(orm_user)

resp = UserAuthResponse.model_validate(orm_user)

print(resp)
# token='abc123' user_info=UserInfoResponse(id=1, name='Alice')


# print("##" * 20)

# aaa = {"token": "abc123", "user_info": {"id": 1, "name": "Alice"}}

# respaaa = UserAuthResponse.model_validate(aaa)

# print(respaaa)
