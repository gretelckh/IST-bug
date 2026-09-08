"""Host层故障4：LLM把int参数传成了字符串"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加"""
        return a + b

    async with Client(server) as client:
        try:
            # Host 错误：a 应该是 int，传成了字符串 "5"
            result = await client.call_tool("add", {"a": "5", "b": 3})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 参数类型错误 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())