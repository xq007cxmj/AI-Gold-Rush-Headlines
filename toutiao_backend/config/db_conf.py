from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 数据库URL
ASYNC_DATABASE_URL = (
    "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
)

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 是否打印SQL语句
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


# 创建异步会话依赖
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
