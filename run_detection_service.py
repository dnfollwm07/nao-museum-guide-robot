"""
启动检测服务的主入口
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.detection_service import DetectionService


def main():
    """主函数"""
    print("=" * 60)
    print("展品检测服务")
    print("=" * 60)
    print("\n正在初始化检测服务...")
    
    service = DetectionService(num_exhibits=2)
    
    try:
        print("检测服务已启动")
        print(f"  - 展品占用检测端口: {service.network_config.detection_port}")
        print(f"  - 语音识别服务端口: {service.network_config.audio_port}")
        print("\n按 Ctrl+C 停止服务\n")
        service.start_all_services()
    except KeyboardInterrupt:
        print("\n\n正在关闭检测服务...")
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.close()
        print("检测服务已关闭")


if __name__ == "__main__":
    main()

