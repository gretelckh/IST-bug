"""Server工具层故障3：工具内部业务断言失败"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def withdraw(amount: int) -> str:
        """取款"""
        balance = 100
        # Server 错误：余额不足时断言失败
        assert amount <= balance, f"余额不足，当前余额: {balance}"
        return f"取款成功，剩余余额: {balance - amount}"

    async with Client(server) as client:
        try:
            result = await client.call_tool("withdraw", {"amount": 500})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 断言异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())