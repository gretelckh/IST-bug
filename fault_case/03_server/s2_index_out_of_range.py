"""Server工具层故障2：工具内部数组越界"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_item(index: int) -> str:
        """获取列表中的元素"""
        items = ["apple", "banana", "cherry"]
        # Server 错误：index 超出列表长度
        return items[index]

    async with Client(server) as client:
        try:
            result = await client.call_tool("get_item", {"index": 99})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 数组越界 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())