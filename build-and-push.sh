#!/bin/bash

echo "🔨 Building FitMind Coach images..."

# Проверить, что мы в правильной директории
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Building API image...${NC}"
docker build -t fitmindlab.hopto.org/root/fitmind-coach/api:latest -f Dockerfile.api .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ API image built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build API image${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Building Bot image...${NC}"
docker build -t fitmindlab.hopto.org/root/fitmind-coach/bot:latest -f Dockerfile.bot .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bot image built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build Bot image${NC}"
    exit 1
fi

echo -e "${YELLOW}📤 Pushing images to GitLab Registry...${NC}"

echo -e "${YELLOW}📤 Pushing API image...${NC}"
docker push fitmindlab.hopto.org/root/fitmind-coach/api:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ API image pushed successfully${NC}"
else
    echo -e "${RED}❌ Failed to push API image${NC}"
    exit 1
fi

echo -e "${YELLOW}📤 Pushing Bot image...${NC}"
docker push fitmindlab.hopto.org/root/fitmind-coach/bot:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bot image pushed successfully${NC}"
else
    echo -e "${RED}❌ Failed to push Bot image${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 All images built and pushed successfully!${NC}"
echo -e "${GREEN}📦 Available images:${NC}"
echo -e "   🔹 fitmindlab.hopto.org/root/fitmind-coach/api:latest"
echo -e "   🔹 fitmindlab.hopto.org/root/fitmind-coach/bot:latest"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "   1. Copy docker-compose.prod.yml to VPS"
echo -e "   2. Create .env file on VPS with required variables"
echo -e "   3. Run: docker-compose -f docker-compose.prod.yml up -d"
