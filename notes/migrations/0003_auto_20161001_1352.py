# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-01 13:52
from __future__ import unicode_literals

from django.db import migrations, models
import markupfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0002_note_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='_text_rendered',
            field=models.TextField(default='', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='note',
            name='text_markup_type',
            field=models.CharField(choices=[(b'', b'--'), (b'html', 'HTML'), (b'plain', 'Plain'), (b'markdown', 'Markdown'), (b'restructuredtext', 'Restructured Text')], default='markdown', editable=False, max_length=30),
        ),
        migrations.AlterField(
            model_name='note',
            name='text',
            field=markupfield.fields.MarkupField(rendered_field=True, verbose_name='Text'),
        ),
    ]