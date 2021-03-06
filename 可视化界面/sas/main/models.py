from django.db import models
import sys

sys.path.append("../")
from Login.models import Users


# Create your models here.
class Comments(models.Model):
    评论id = models.IntegerField(db_column='评论ID', primary_key=True)  # Field name made lowercase.
    顾客id = models.ForeignKey(Users, models.DO_NOTHING, db_column='顾客ID', blank=True,
                             null=True)  # Field name made lowercase.
    商品id = models.IntegerField(db_column='商品ID')  # Field name made lowercase.
    评论时间 = models.DateTimeField()
    评论内容 = models.CharField(max_length=500, db_collation='Chinese_PRC_CI_AS')
    
    class Meta:
        managed = False
        db_table = '评论数据表'


class Results(models.Model):
    结论id = models.IntegerField(db_column='结论ID', primary_key=True)
    评论id = models.ForeignKey(Comments, models.DO_NOTHING, db_column='评论ID', blank=True, null=True)
    属性极性对 = models.CharField(max_length=300, db_collation='Chinese_PRC_CI_AS')
    更新时间 = models.DateTimeField()
    
    class Meta:
        managed = False
        db_table = '结论数据表'
