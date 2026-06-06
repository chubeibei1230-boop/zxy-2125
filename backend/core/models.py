from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', '管理者'),
        ('executor', '执行者'),
        ('reviewer', '复核者'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='角色')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.username} - {self.get_role_display()}'


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class Project(BaseModel):
    name = models.CharField(max_length=100, verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='managed_projects', verbose_name='负责人')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Station(BaseModel):
    name = models.CharField(max_length=100, verbose_name='工位名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='工位编号')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='stations', verbose_name='所属项目')
    description = models.TextField(blank=True, verbose_name='工位描述')

    class Meta:
        verbose_name = '工位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.code} - {self.name}'


class TaskTemplate(BaseModel):
    name = models.CharField(max_length=100, verbose_name='模板名称')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='templates', verbose_name='所属项目')
    preparation_content = models.TextField(verbose_name='准备内容要求')
    reception_content = models.TextField(verbose_name='接待内容要求')
    closing_content = models.TextField(verbose_name='收尾内容要求')
    description = models.TextField(blank=True, verbose_name='模板描述')

    class Meta:
        verbose_name = '任务模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Task(BaseModel):
    STATUS_CHOICES = (
        ('pending_prep', '待准备'),
        ('in_progress', '进行中'),
        ('pending_review', '待复核'),
        ('rectification_pending', '待整改'),
        ('rectified_pending_review', '已整改待复核'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    title = models.CharField(max_length=200, verbose_name='任务标题')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='tasks', verbose_name='所属项目')
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='tasks', verbose_name='工位')
    template = models.ForeignKey(TaskTemplate, on_delete=models.PROTECT, related_name='tasks', verbose_name='任务模板')
    executor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='executed_tasks', verbose_name='执行者')
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reviewed_tasks', verbose_name='复核者')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_prep', verbose_name='状态')
    scheduled_time = models.DateTimeField(verbose_name='计划时间')

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    @property
    def has_flow_records(self):
        return self.flow_records.exists()

    def can_hard_delete(self):
        return not self.has_flow_records

    def delete(self, using=None, keep_parents=False):
        if self.can_hard_delete():
            super().delete(using, keep_parents)
        else:
            self.soft_delete()

    def can_transition_to(self, new_status):
        valid_transitions = {
            'pending_prep': ['in_progress', 'cancelled'],
            'in_progress': ['pending_review', 'cancelled'],
            'pending_review': ['completed', 'rectification_pending'],
            'rectification_pending': ['rectified_pending_review'],
            'rectified_pending_review': ['completed', 'rectification_pending'],
            'completed': [],
            'cancelled': [],
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition_to(self, new_status, operator, remark='', skip_rectification_check=False):
        if not self.can_transition_to(new_status):
            raise ValueError(f'无法从 {self.get_status_display()} 转换到 {new_status}')
        
        if new_status in ['rectification_pending', 'rectified_pending_review'] and not skip_rectification_check:
            raise ValueError('整改状态必须通过专用接口设置，请使用整改功能')
        
        if new_status == 'pending_review':
            if not hasattr(self, 'preparation'):
                raise ValueError('请先填写准备记录')
            if not hasattr(self, 'reception'):
                raise ValueError('请先填写接待记录')
            if not hasattr(self, 'closing'):
                raise ValueError('请先填写收尾记录')
        
        if new_status == 'completed':
            if not hasattr(self, 'closing'):
                raise ValueError('请先填写收尾记录')
            if self.closing.has_exception and not self.exception_handlings.exists():
                raise ValueError('请先处理异常，填写异常处理意见')
            self.rectification_records.filter(status__in=['pending', 'rectified']).update(status='closed')
        
        old_status = self.status
        self.status = new_status
        self.save()
        
        TaskFlowRecord.objects.create(
            task=self,
            old_status=old_status,
            new_status=new_status,
            operator=operator,
            remark=remark
        )
        return True


class TaskFlowRecord(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='flow_records', verbose_name='任务')
    old_status = models.CharField(max_length=30, choices=Task.STATUS_CHOICES, verbose_name='原状态')
    new_status = models.CharField(max_length=30, choices=Task.STATUS_CHOICES, verbose_name='新状态')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '任务流转记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title}: {self.old_status} -> {self.new_status}'


class PreparationRecord(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='preparation', verbose_name='任务')
    content = models.TextField(verbose_name='准备记录内容')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='填写人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='填写时间')

    class Meta:
        verbose_name = '准备记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.task.title} - 准备记录'


class ReceptionRecord(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='reception', verbose_name='任务')
    content = models.TextField(verbose_name='接待记录内容')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='填写人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='填写时间')

    class Meta:
        verbose_name = '接待记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.task.title} - 接待记录'


class ClosingRecord(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='closing', verbose_name='任务')
    content = models.TextField(verbose_name='收尾记录内容')
    has_exception = models.BooleanField(default=False, verbose_name='是否有异常')
    exception_description = models.TextField(blank=True, verbose_name='异常描述')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='填写人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='填写时间')

    class Meta:
        verbose_name = '收尾记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.task.title} - 收尾记录'


class ExceptionHandling(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='exception_handlings', verbose_name='任务')
    handling_content = models.TextField(verbose_name='异常处理内容')
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='复核人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='处理时间')

    class Meta:
        verbose_name = '异常处理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.task.title} - 异常处理'


class RectificationRecord(models.Model):
    STAGE_CHOICES = (
        ('preparation', '准备记录'),
        ('reception', '接待记录'),
        ('closing', '收尾记录'),
    )
    STATUS_CHOICES = (
        ('pending', '待整改'),
        ('rectified', '已整改'),
        ('closed', '已闭环'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='rectification_records', verbose_name='任务')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name='整改环节')
    rectification_content = models.TextField(verbose_name='整改意见')
    rectification_note = models.TextField(blank=True, verbose_name='整改说明')
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='initiated_rectifications', verbose_name='复核人')
    executor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='rectifications', verbose_name='执行人')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='整改状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    rectified_at = models.DateTimeField(null=True, blank=True, verbose_name='整改时间')

    class Meta:
        verbose_name = '整改记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title} - {self.get_stage_display()}整改'


class TaskReview(models.Model):
    PROBLEM_TYPE_CHOICES = (
        ('process', '流程问题'),
        ('execution', '执行问题'),
        ('communication', '沟通问题'),
        ('resource', '资源问题'),
        ('quality', '质量问题'),
        ('other', '其他问题'),
    )

    RESPONSIBILITY_STAGE_CHOICES = (
        ('preparation', '准备环节'),
        ('reception', '接待环节'),
        ('closing', '收尾环节'),
        ('review', '复核环节'),
        ('management', '管理环节'),
        ('other', '其他环节'),
    )

    FOLLOWUP_STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('closed', '已闭环'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reviews', verbose_name='任务')
    conclusion = models.TextField(verbose_name='复盘结论')
    problem_type = models.CharField(max_length=30, choices=PROBLEM_TYPE_CHOICES, verbose_name='问题类型')
    responsibility_stage = models.CharField(max_length=30, choices=RESPONSIBILITY_STAGE_CHOICES, verbose_name='责任环节')
    improvement_suggestion = models.TextField(verbose_name='改进建议')
    followup_status = models.CharField(max_length=30, choices=FOLLOWUP_STATUS_CHOICES, default='pending', verbose_name='跟进状态')
    rectification_feedback = models.TextField(blank=True, verbose_name='整改反馈')
    initiator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='initiated_reviews', verbose_name='发起人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    rectification_feedback_at = models.DateTimeField(null=True, blank=True, verbose_name='整改反馈时间')

    class Meta:
        verbose_name = '任务复盘记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title} - 复盘记录'

    def can_edit(self, user):
        if user.role == 'manager':
            return True
        if user.role == 'reviewer' and self.initiator == user:
            return True
        return False

    def can_submit_feedback(self, user):
        return user.role == 'executor' and self.task.executor == user


class TaskReviewOperationLog(models.Model):
    OPERATION_TYPE_CHOICES = (
        ('create', '创建复盘'),
        ('update', '编辑复盘'),
        ('update_status', '更新跟进状态'),
        ('submit_feedback', '提交整改反馈'),
        ('delete', '删除复盘'),
    )

    review = models.ForeignKey(TaskReview, on_delete=models.CASCADE, related_name='operation_logs', verbose_name='复盘记录')
    operation_type = models.CharField(max_length=30, choices=OPERATION_TYPE_CHOICES, verbose_name='操作类型')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    old_followup_status = models.CharField(max_length=30, choices=TaskReview.FOLLOWUP_STATUS_CHOICES, null=True, blank=True, verbose_name='原跟进状态')
    new_followup_status = models.CharField(max_length=30, choices=TaskReview.FOLLOWUP_STATUS_CHOICES, null=True, blank=True, verbose_name='新跟进状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '复盘操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.review.task.title} - {self.get_operation_type_display()}'
