from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from toutiao_backend.schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    """
    添加历史记录请求
    """

    news_id: int = Field(..., alias="newsId")


# 规划两个类： 一个是新闻模型类 + 一个是浏览历史列表接口响应模型类
class HistoryNewsItemResponse(NewsItemBase):
    view_id: int = Field(alias="viewId")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# 浏览历史列表接口响应模型类
class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
