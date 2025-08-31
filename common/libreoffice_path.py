import platform
import os
import subprocess
import glob


def get_libreoffice_path():
    """自动检测 LibreOffice 可执行文件路径"""
    system = platform.system().lower()
    
    # 常见路径列表
    paths = []
    if system == "darwin":  # macOS
        paths = [
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',
            '/usr/local/bin/libreoffice',
            '/opt/homebrew/bin/libreoffice'
        ]
    elif system == "linux":  # Linux
        paths = [
            '/usr/bin/libreoffice',
            '/usr/local/bin/libreoffice',
            '/opt/libreoffice*/program/soffice'
        ]
    elif system == "windows":  # Windows
        paths = [
            'C:\\Program Files\\LibreOffice\\program\\soffice.exe',
            'C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe'
        ]
    
    # 检查路径是否存在
    for path in paths:
        if '*' in path:  # 处理通配符路径
            matches = glob.glob(path)
            if matches and os.path.isfile(matches[0]):
                return matches[0]
        elif os.path.isfile(path):
            return path
    
    # 如果都找不到，尝试系统PATH中的命令
    try:
        result = subprocess.run(['which', 'libreoffice'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return 'libreoffice'  # 最后回退到系统PATH