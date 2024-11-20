# Generated by Django 5.1.3 on 2024-11-20 14:29

import cuid2.generator
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0094_alter_page_locale'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaitingListSignup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('referral_code', models.CharField(default=cuid2.generator.Cuid.generate, editable=False, max_length=10, unique=True)),
                ('referred_by', models.ForeignKey(blank=True, help_text='The person who referred this user', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals', to='home.waitinglistsignup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WaitingPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('tag', models.CharField(blank=True, help_text='Text for a tag above the title', max_length=255)),
                ('waiting_title', models.CharField(help_text='Title for the waiting page', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description for the waiting page')),
                ('show_signup', models.BooleanField(default=True, help_text='Show the signup form or not')),
                ('features', wagtail.fields.StreamField([('feature_list', 3)], block_lookup={0: ('wagtail.blocks.CharBlock', (), {}), 1: ('wagtail.blocks.TextBlock', (), {}), 2: ('wagtail.blocks.StructBlock', [[('icon', 0), ('title', 0), ('description', 1)]], {}), 3: ('wagtail.blocks.ListBlock', (2,), {})})),
                ('success_content', wagtail.fields.StreamField([('title', 0), ('body', 1), ('referral_code', 2), ('incentive_list', 6)], block_lookup={0: ('wagtail.blocks.CharBlock', (), {'blank': True, 'help_text': 'Title upon successful sign up to waiting list', 'max_length': 255}), 1: ('wagtail.blocks.RichTextBlock', (), {'blank': True, 'help_text': 'Body upon successful sign up'}), 2: ('wagtail.blocks.BooleanBlock', (), {'default': True, 'help_text': 'Show referral code here'}), 3: ('wagtail.blocks.CharBlock', (), {}), 4: ('wagtail.blocks.TextBlock', (), {}), 5: ('wagtail.blocks.StructBlock', [[('icon', 3), ('title', 3), ('description', 4)]], {}), 6: ('wagtail.blocks.ListBlock', (5,), {})})),
                ('signup_image', models.ForeignKey(blank=True, help_text='Sign Up image', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
