"""Host层故障3：LLM把参数名 user_id 写成 userId"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_user(user_id: int) -> str:
        """根据用户ID查询用户"""
        return f"User_{user_id}"

    async with Client(server) as client:
        try:
            # Host 错误：参数名应该是 user_id，写成了 userId
            result = await client.call_tool("get_user", {"userId": 123})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 参数名拼写错误 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())