#!/bin/bash

# Скрипт для настройки SSL сертификатов для GitLab
# Использует Let's Encrypt для бесплатных SSL сертификатов

set -e

DOMAIN=${1:-"gitlab.yourdomain.com"}
EMAIL=${2:-"admin@yourdomain.com"}

echo "🔐 Настройка SSL для домена: $DOMAIN"
echo "📧 Email для уведомлений: $EMAIL"

# Проверяем наличие certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 Устанавливаем certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Создаем директорию для SSL
sudo mkdir -p /etc/nginx/ssl

# Получаем SSL сертификат
echo "🎫 Получаем SSL сертификат от Let's Encrypt..."
sudo certbot certonly \
    --standalone \
    --pre-hook "sudo systemctl stop nginx" \
    --post-hook "sudo systemctl start nginx" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# Копируем сертификаты в нужную директорию
echo "📁 Копируем сертификаты..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/nginx/ssl/$DOMAIN.crt
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/nginx/ssl/$DOMAIN.key

# Устанавливаем правильные права
sudo chmod 644 /etc/nginx/ssl/$DOMAIN.crt
sudo chmod 600 /etc/nginx/ssl/$DOMAIN.key

# Создаем cron задачу для автоматического обновления
echo "⏰ Настраиваем автоматическое обновление сертификатов..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL сертификат успешно настроен для $DOMAIN"
echo "🔄 Сертификат будет автоматически обновляться каждый день в 12:00"
echo "🌐 Теперь можно настроить Nginx для использования HTTPS"
