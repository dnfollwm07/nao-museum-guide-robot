"""
NAO博物馆导览机器人主入口
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.robot_controller import RobotController


def main():
    """主函数"""
    print("=" * 60)
    print("NAO博物馆导览机器人系统")
    print("=" * 60)
    print("\n正在初始化机器人控制器...")
    
    controller = RobotController()
    
    try:
        print("开始运行导览系统...")
        controller.run()
    except KeyboardInterrupt:
        print("\n\n用户中断，正在关闭系统...")
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("系统已关闭")
        print("注意力记录:", controller.attention_records)


if __name__ == "__main__":
    main()

