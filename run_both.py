import subprocess
import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('run_both.log', encoding='gbk'),
        logging.StreamHandler()
    ]
)

# 获取项目根目录
project_root = Path(__file__).parent.resolve()

# 定义要运行的脚本路径
test_script = project_root / 'main.py'
qd_script = project_root / 'vlu' / 'qd.py'

# 验证脚本存在
if not test_script.exists():
    logging.error(f"Test script not found at {test_script}")
    exit(1)

if not qd_script.exists():
    logging.error(f"QD script not found at {qd_script}")
    exit(1)


try:
    test_process = subprocess.Popen(
        ['python', str(test_script)],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8'
    )
    logging.info(f"Started test.py (PID: {test_process.pid})")
except Exception as e:
    logging.error(f"Failed to start test.py: {str(e)}")
    exit(1)

# 运行qd.py的进程
try:
    qd_process = subprocess.Popen(
        ['uv', 'run', str(qd_script)],
        cwd=project_root / 'vlu',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8'
    )
    logging.info(f"Started qd.py (PID: {qd_process.pid})")
except Exception as e:
    logging.error(f"Failed to start qd.py: {str(e)}")
    test_process.terminate()
    exit(1)

# 输出处理线程函数
def output_reader(pipe, prefix):
    try:
        for line in iter(pipe.readline, ''):
            logging.info(f'[{prefix}] {line.strip()}')
    except ValueError:
        pass  # 管道关闭时的正常异常

# 创建并启动输出线程
from threading import Thread

test_thread = Thread(target=output_reader, args=(test_process.stdout, 'test.py'))
qd_thread = Thread(target=output_reader, args=(qd_process.stdout, 'qd.py'))
test_thread.daemon = True
qd_thread.daemon = True
test_thread.start()
qd_thread.start()

# 进程监控循环
try:
    while True:
        if test_process.poll() is not None and qd_process.poll() is not None:
            break
        
        # 降低CPU占用
        test_thread.join(0.1)
        qd_thread.join(0.1)

except KeyboardInterrupt:
    logging.warning("收到中断信号，终止进程...")

finally:
    # 确保进程终止
    for p in [test_process, qd_process]:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    
    logging.info("所有进程已终止")