from django.db import models


class Track(models.Model):
    name = models.CharField('地块名称', max_length=100)
    created_at = models.DateTimeField('导入时间', auto_now_add=True)

    class Meta:
        verbose_name = '地块'
        verbose_name_plural = '地块'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TrackPoint(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='points', verbose_name='地块')
    sequence = models.IntegerField('序列号')
    gps_time = models.DateTimeField('GPS时间')
    longitude = models.FloatField('经度')
    latitude = models.FloatField('纬度')
    x = models.FloatField('x坐标')
    y = models.FloatField('y坐标')
    speed = models.FloatField('速度(km/h)')
    heading = models.FloatField('航向')
    working_status = models.BooleanField('工作状态')
    width = models.FloatField('幅宽(m)')
    depth = models.FloatField('深度(mm)')
    depth_standard = models.FloatField('深度标准值')

    class Meta:
        verbose_name = '轨迹点'
        verbose_name_plural = '轨迹点'
        ordering = ['track', 'sequence']
        indexes = [
            models.Index(fields=['track', 'sequence']),
        ]

    def __str__(self):
        return f'{self.track.name} - {self.sequence}'
