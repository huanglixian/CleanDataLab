import queue
import threading
import subprocess
import tempfile
import shutil
import time
import uuid
from typing import List, Tuple, Optional


class LibreOfficeQueue:
    """LibreOffice转换队列，单例模式"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.task_queue = queue.Queue()
                    cls._instance.active_tasks = {}  # task_id -> task_dict
                    cls._instance.task_order = []    # 任务顺序列表
                    threading.Thread(target=cls._instance._worker_loop, daemon=True).start()
        return cls._instance
    
    def _worker_loop(self):
        """工作线程：处理队列中的任务"""
        while True:
            try:
                task_id = self.task_queue.get(timeout=1)
                task = self.active_tasks.get(task_id)
                if task:
                    task['status'] = "processing"
                    with self._lock:
                        if task_id in self.task_order:
                            self.task_order.remove(task_id)
                    
                    task['result'] = self._convert_batch(task['files_data'], task['source_ext'], task['target_ext'])
                    task['status'] = "completed"
                    task['completed_time'] = time.time()
                self.task_queue.task_done()
            except queue.Empty:
                self._cleanup_stale_tasks()
                continue
    
    def _convert_batch(self, files_data, source_ext, target_ext):
        """批量转换文件"""
        temp_dir = tempfile.mkdtemp()
        results = []
        
        try:
            # 写入临时文件并执行转换
            input_paths = []
            for i, (filename, content) in enumerate(files_data):
                path = f"{temp_dir}/file_{i}.{source_ext}"
                with open(path, 'wb') as f:
                    f.write(content)
                input_paths.append((path, filename))
            
            cmd = ['/Applications/LibreOffice.app/Contents/MacOS/soffice',
                   '--headless', '--convert-to', target_ext, '--outdir', temp_dir]
            cmd.extend([path for path, _ in input_paths])
            subprocess.run(cmd, check=True, timeout=120)
            
            # 读取结果
            for input_path, original_name in input_paths:
                output_path = input_path.replace(f'.{source_ext}', f'.{target_ext}')
                try:
                    with open(output_path, 'rb') as f:
                        results.append((original_name, f.read(), None))
                except Exception as e:
                    results.append((original_name, None, str(e)[:20]))
        
        except Exception as e:
            results = [(filename, None, str(e)[:20]) for filename, _ in files_data]
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return results
    
    def submit_task(self, files_data: List[Tuple[str, bytes]], source_ext: str, target_ext: str) -> str:
        """提交任务，返回任务ID"""
        task_id = str(uuid.uuid4())
        task = {
            'files_data': files_data,
            'source_ext': source_ext,
            'target_ext': target_ext,
            'status': 'waiting',
            'result': None,
            'created_time': time.time()
        }
        
        with self._lock:
            self.active_tasks[task_id] = task
            self.task_order.append(task_id)
        
        self.task_queue.put(task_id)
        return task_id
    
    def get_task_position(self, task_id: str) -> int:
        """获取任务在队列中的位置（1-based），0表示正在处理或已完成"""
        task = self.active_tasks.get(task_id)
        if not task or task['status'] != 'waiting':
            return 0
        
        with self._lock:
            try:
                return self.task_order.index(task_id) + 1
            except ValueError:
                return 0
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        task = self.active_tasks.get(task_id)
        return task['status'] if task else None
    
    def wait_for_task(self, task_id: str, timeout: int = 300):
        """等待任务完成并返回结果"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            task = self.active_tasks.get(task_id)
            if task and task['status'] == "completed":
                result = task['result']
                self._cleanup_task(task_id)
                return result
            time.sleep(0.2)
        
        # 超时清理
        self._cleanup_task(task_id)
        return None
    
    def _cleanup_task(self, task_id: str):
        """清理单个任务"""
        with self._lock:
            self.active_tasks.pop(task_id, None)
            if task_id in self.task_order:
                self.task_order.remove(task_id)
    
    def _cleanup_stale_tasks(self):
        """清理过期任务"""
        current_time = time.time()
        with self._lock:
            stale_tasks = []
            for task_id, task in self.active_tasks.items():
                # 清理超过10分钟的waiting任务或超过1小时的completed任务
                if (task['status'] == 'waiting' and current_time - task.get('created_time', current_time) > 600) or \
                   (task['status'] == 'completed' and current_time - task.get('completed_time', current_time) > 3600):
                    stale_tasks.append(task_id)
            
            for task_id in stale_tasks:
                self.active_tasks.pop(task_id, None)
                if task_id in self.task_order:
                    self.task_order.remove(task_id)
    
    def get_queue_size(self):
        """获取当前队列大小"""
        return self.task_queue.qsize()


# 全局实例
lo_queue = LibreOfficeQueue()