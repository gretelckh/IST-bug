"""Host层故障2：LLM漏传必填参数 b"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加，a和b都是必填"""
        return a + b

    async with Client(server) as client:
        try:
            # Host 错误：只传了 a，漏了必填的 b
            result = await client.call_tool("add", {"a": 5})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 缺少必填参数 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())