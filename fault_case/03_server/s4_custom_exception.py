"""Server工具层故障4：工具抛出自定义业务异常"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class OrderNotFoundError(Exception):
    """自定义异常：订单不存在"""
    pass

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_order(order_id: str) -> str:
        """查询订单"""
        valid_orders = {"ORD001", "ORD002"}
        if order_id not in valid_orders:
            # Server 错误：抛出自定义业务异常
            raise OrderNotFoundError(f"订单 {order_id} 不存在")
        return f"订单 {order_id} 详情: ..."

    async with Client(server) as client:
        try:
            result = await client.call_tool("get_order", {"order_id": "ORD999"})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 自定义业务异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())