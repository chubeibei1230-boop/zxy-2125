from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Project, Station, TaskTemplate, Task
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = '初始化示例数据'

    def handle(self, *args, **options):
        self.stdout.write('正在创建用户...')
        
        manager, _ = User.objects.get_or_create(
            username='manager',
            defaults={
                'role': 'manager',
                'email': 'manager@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        manager.set_password('123456')
        manager.save()

        executor, _ = User.objects.get_or_create(
            username='executor',
            defaults={
                'role': 'executor',
                'email': 'executor@example.com',
            }
        )
        executor.set_password('123456')
        executor.save()

        reviewer, _ = User.objects.get_or_create(
            username='reviewer',
            defaults={
                'role': 'reviewer',
                'email': 'reviewer@example.com',
            }
        )
        reviewer.set_password('123456')
        reviewer.save()

        self.stdout.write(self.style.SUCCESS('用户创建完成'))
        self.stdout.write('  - 管理者: manager / 123456')
        self.stdout.write('  - 执行者: executor / 123456')
        self.stdout.write('  - 复核者: reviewer / 123456')

        self.stdout.write('正在创建项目...')
        project, _ = Project.objects.get_or_create(
            name='体验中心项目',
            defaults={
                'description': '客户体验中心日常运营项目',
                'manager': manager,
            }
        )
        self.stdout.write(self.style.SUCCESS('项目创建完成'))

        self.stdout.write('正在创建工位...')
        stations_data = [
            {'code': 'ST001', 'name': '前台接待工位', 'description': '负责客户接待和引导'},
            {'code': 'ST002', 'name': '产品展示工位', 'description': '负责产品展示和讲解'},
            {'code': 'ST003', 'name': '体验洽谈工位', 'description': '负责客户体验和商务洽谈'},
        ]
        stations = []
        for s_data in stations_data:
            station, _ = Station.objects.get_or_create(
                code=s_data['code'],
                defaults={
                    'name': s_data['name'],
                    'project': project,
                    'description': s_data['description'],
                }
            )
            stations.append(station)
        self.stdout.write(self.style.SUCCESS('工位创建完成'))

        self.stdout.write('正在创建任务模板...')
        template, _ = TaskTemplate.objects.get_or_create(
            name='标准客户接待模板',
            defaults={
                'project': project,
                'preparation_content': '1. 检查工位设备是否正常\n2. 准备宣传资料和饮品\n3. 确认当日预约信息',
                'reception_content': '1. 热情迎接客户并引导就座\n2. 详细介绍产品功能和特点\n3. 记录客户需求和反馈',
                'closing_content': '1. 整理工位和资料\n2. 录入客户信息系统\n3. 发送感谢短信/邮件',
                'description': '标准的客户接待流程模板',
            }
        )
        self.stdout.write(self.style.SUCCESS('任务模板创建完成'))

        self.stdout.write('正在创建示例任务...')
        for i, station in enumerate(stations):
            task_title = f'客户接待任务 - {station.name}'
            Task.objects.get_or_create(
                title=task_title,
                defaults={
                    'project': project,
                    'station': station,
                    'template': template,
                    'executor': executor,
                    'reviewer': reviewer,
                    'scheduled_time': timezone.now() + timezone.timedelta(days=i + 1),
                }
            )
        self.stdout.write(self.style.SUCCESS('示例任务创建完成'))

        self.stdout.write(self.style.SUCCESS('数据初始化完成！'))
