# APScheduler动态定时任务demo，支持crontab表达式
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import datetime
from typing import Dict, Optional


class DynamicScheduler:
    """
    动态定时任务管理器
    支持添加、删除、查看定时任务，支持crontab表达式
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, str] = {}  # 存储任务ID和描述
    
    async def start(self) -> None:
        """启动调度器"""
        self.scheduler.start()
        print("调度器已启动")
    
    def add_job_by_cron(self, job_id: str, cron_expression: str, description: str = "") -> bool:
        """
        使用crontab表达式添加定时任务
        
        Args:
            job_id: 任务唯一标识
            cron_expression: crontab表达式，如 "*/5 * * * *"
            description: 任务描述
            
        Returns:
            bool: 是否成功添加
        """
        if job_id in self.jobs:
            print(f"任务 {job_id} 已存在")
            return False
        
        try:
            # 创建cron触发器
            trigger = CronTrigger.from_crontab(cron_expression)
            
            # 添加任务
            self.scheduler.add_job(
                self._execute_job,
                trigger,
                id=job_id,
                args=[job_id, description],
                misfire_grace_time=60
            )
            
            self.jobs[job_id] = description
            print(f"成功添加任务 {job_id}: {description}, cron表达式: {cron_expression}")
            return True
            
        except Exception as e:
            print(f"添加任务失败: {e}")
            return False
    
    def add_interval_job(self, job_id: str, seconds: int, description: str = "") -> bool:
        """
        添加间隔定时任务
        
        Args:
            job_id: 任务唯一标识
            seconds: 间隔秒数
            description: 任务描述
            
        Returns:
            bool: 是否成功添加
        """
        if job_id in self.jobs:
            print(f"任务 {job_id} 已存在")
            return False
        
        try:
            self.scheduler.add_job(
                self._execute_job,
                "interval",
                seconds=seconds,
                id=job_id,
                args=[job_id, description]
            )
            
            self.jobs[job_id] = description
            print(f"成功添加间隔任务 {job_id}: {description}, 间隔: {seconds}秒")
            return True
            
        except Exception as e:
            print(f"添加任务失败: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        删除定时任务
        
        Args:
            job_id: 任务唯一标识
            
        Returns:
            bool: 是否成功删除
        """
        if job_id not in self.jobs:
            print(f"任务 {job_id} 不存在")
            return False
        
        try:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            print(f"成功删除任务 {job_id}")
            return True
            
        except Exception as e:
            print(f"删除任务失败: {e}")
            return False
    
    def list_jobs(self) -> None:
        """列出所有定时任务"""
        if not self.jobs:
            print("当前没有定时任务")
            return
        
        print("\n=== 当前定时任务列表 ===")
        for job_id, description in self.jobs.items():
            job = self.scheduler.get_job(job_id)
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job and job.next_run_time else "未知"
            print(f"任务ID: {job_id}")
            print(f"描述: {description}")
            print(f"下次执行时间: {next_run}")
            print(f"触发器: {job.trigger}")
            print("-" * 40)
    
    async def _execute_job(self, job_id: str, description: str) -> None:
        """
        执行定时任务的内部方法
        
        Args:
            job_id: 任务ID
            description: 任务描述
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 执行任务: {job_id} - {description}")


async def demo_interactive():
    """交互式演示动态添加定时任务"""
    scheduler = DynamicScheduler()
    await scheduler.start()
    
    # 演示添加不同类型的定时任务
    print("\n=== 演示动态添加定时任务 ===")
    
    # 1. 添加间隔任务
    scheduler.add_interval_job("interval_10s", 10, "每10秒执行一次")
    
    # 2. 添加crontab任务
    scheduler.add_job_by_cron("cron_minute", "*/1 * * * *", "每分钟执行一次")
    scheduler.add_job_by_cron("cron_hourly", "0 * * * *", "每小时执行一次")
    scheduler.add_job_by_cron("cron_daily", "0 9 * * *", "每天9点执行")
    scheduler.add_job_by_cron("cron_weekly", "0 9 * * 1", "每周一9点执行")
    
    # 3. 列出所有任务
    scheduler.list_jobs()
    
    # 4. 演示动态删除任务
    print("\n等待10秒后删除间隔任务...")
    await asyncio.sleep(10)
    scheduler.remove_job("interval_10s")
    
    # 5. 再次列出任务
    scheduler.list_jobs()
    
    # 6. 演示动态添加新任务
    print("\n动态添加新任务...")
    scheduler.add_job_by_cron("cron_custom", "*/2 * * * *", "每2分钟执行一次")
    
    # 7. 最终任务列表
    scheduler.list_jobs()
    
    print("\n=== 演示完成，程序将继续运行，按Ctrl+C退出 ===")
    
    # 保持程序运行
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n程序退出")


async def main():
    """主函数"""
    await demo_interactive()


if __name__ == "__main__":
    asyncio.run(main())