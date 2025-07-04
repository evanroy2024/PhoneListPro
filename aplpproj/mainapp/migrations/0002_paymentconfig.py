# Generated by Django 5.1.7 on 2025-03-30 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('paypal', 'PayPal'), ('stripe', 'Stripe')], max_length=10)),
                ('client_id', models.CharField(blank=True, max_length=255, null=True)),
                ('client_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('stripe_publishable_key', models.CharField(blank=True, max_length=255, null=True)),
                ('stripe_secret_key', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
