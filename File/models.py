from django.db import models
import django.utils.timezone as timezone


class fileInfo(models.Model):
    # 文档重命名，保存到static/media/classify/code.ext
    def user_directory_path(self, filename):
        import os
        ext = os.path.splitext(filename)[1]
        name = self.code + ext
        return '{0}/{1}'.format(self.classify, name)

    classifyTest = 'XL'
    classifyDefault = 'XS'
    classifyChoices = (
        (classifyTest, 'XL'),
        (classifyDefault, 'XS'),
    )
    code = models.CharField("文档编号", max_length=60, null=False, unique=True)
    filename = models.CharField("文件名", max_length=60, null=False)
    classify = models.CharField('文档类别', max_length=60, null=False, 
                                choices=classifyChoices,
                                default=classifyDefault
                                )
    createby = models.CharField("创建人",max_length=32)
    createtime = models.DateTimeField("创建时间", default=timezone.now)
    comment = models.CharField('文档描述',max_length=128)
    image_url = models.FileField(verbose_name="上传文档",upload_to=user_directory_path)

    def __str__(self):
        return self.filename
