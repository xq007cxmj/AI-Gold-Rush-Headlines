from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="分类id"
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="排序"
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name}, sort_order={self.sort_order})"


class News(Base):
    __tablename__ = "news"

    # 创建索引：提升查询速度
    __table_args__ = (
        Index("idx_category_id", "category_id"),  # 为 category_id 创建索引,高频查询场景
        Index(
            "idx_publish_time", "publish_time"
        ),  # 为 publish_time 创建索引，按发布时间排序
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="新闻id"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="新闻标题")
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="新闻描述"
    )
    content: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="新闻内容"
    )
    image: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="新闻图片url"
    )
    author: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="新闻作者"
    )
    category_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="分类id")
    views: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="浏览量"
    )
    publish_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="发布时间"
    )

    def __repr__(self) -> str:
        return f"News(id={self.id}, title={self.title}, content={self.content}, category_id={self.category_id})"
