from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "黄师互助 (JMarKet) API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./jmarket.db"

    # 免责声明固定文案
    DISCLAIMER: str = (
        "【免责声明】黄师互助小程序仅提供校园学生之间的信息发布与撮合对接平台，"
        "平台不参与线下具体交易、不托管交易资金、不收取任何佣金。双方请在自愿、"
        "诚信原则下核实身份并完成互助，严禁发布违法违规、违反校纪校规的违禁需求，"
        "谨防网络诈骗。"
    )

settings = Settings()
