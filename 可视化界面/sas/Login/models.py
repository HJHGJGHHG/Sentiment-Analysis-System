from django.db import models


# Create your models here.
class Users(models.Model):
    ID = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    用户名 = models.CharField(max_length=20, db_collation='Chinese_PRC_CI_AS')
    密码 = models.CharField(max_length=20, db_collation='Chinese_PRC_CI_AS')
    年龄 = models.IntegerField()
    身份 = models.CharField(max_length=6, db_collation='Chinese_PRC_CI_AS', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = '用户信息表'
        verbose_name = verbose_name_plural = '用户信息'
