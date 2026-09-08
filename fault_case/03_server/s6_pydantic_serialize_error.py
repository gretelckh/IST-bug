"""Server工具层故障6：工具返回不可JSON序列化的对象，序列化失败"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class User:
    """普通类，无法被JSON序列化"""
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_user_info(user_id: int) -> dict:
        """获取用户信息"""
        # Server 错误：返回了一个不可JSON序列化的自定义对象
        user = User(name="Alice", age=30)
        return {"user": user}  # User 对象无法被 JSON 序列化

    async with Client(server) as client:
        try:
            result = await client.call_tool("get_user_info", {"user_id": 1})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - JSON序列化失败 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())