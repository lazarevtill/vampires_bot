#!/bin/bash

# Docker Test Script for Vampires Bot
echo "🧪 Testing Docker setup for Vampires Bot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_docker() {
    echo -e "${YELLOW}Testing Docker installation...${NC}"
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker is installed${NC}"
        docker --version
    else
        echo -e "${RED}❌ Docker is not installed${NC}"
        return 1
    fi
}

test_docker_compose() {
    echo -e "${YELLOW}Testing Docker Compose...${NC}"
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose is available${NC}"
        docker-compose --version
    else
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        return 1
    fi
}

test_dockerfile() {
    echo -e "${YELLOW}Testing Dockerfile...${NC}"
    if [ -f "Dockerfile" ]; then
        echo -e "${GREEN}✅ Dockerfile exists${NC}"
    else
        echo -e "${RED}❌ Dockerfile not found${NC}"
        return 1
    fi
}

test_docker_compose_file() {
    echo -e "${YELLOW}Testing docker-compose.yml...${NC}"
    if [ -f "docker-compose.yml" ]; then
        echo -e "${GREEN}✅ docker-compose.yml exists${NC}"
        if docker-compose config &> /dev/null; then
            echo -e "${GREEN}✅ docker-compose.yml is valid${NC}"
        else
            echo -e "${RED}❌ docker-compose.yml is invalid${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ docker-compose.yml not found${NC}"
        return 1
    fi
}

test_env_file() {
    echo -e "${YELLOW}Testing environment files...${NC}"
    if [ -f ".env.docker" ]; then
        echo -e "${GREEN}✅ .env.docker template exists${NC}"
    else
        echo -e "${RED}❌ .env.docker template not found${NC}"
        return 1
    fi
    
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env file exists${NC}"
        if grep -q "your_bot_token_here" .env; then
            echo -e "${YELLOW}⚠️  Bot token needs to be configured in .env${NC}"
        else
            echo -e "${GREEN}✅ Bot token appears to be configured${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  .env file not found (will be created from template)${NC}"
    fi
}

test_docker_build() {
    echo -e "${YELLOW}Testing Docker build...${NC}"
    if docker build -t vampires-bot:test . &> /dev/null; then
        echo -e "${GREEN}✅ Docker build successful${NC}"
        docker rmi vampires-bot:test &> /dev/null
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        return 1
    fi
}

test_database_startup() {
    echo -e "${YELLOW}Testing database startup...${NC}"
    
    # Start only the database
    if docker-compose up postgres -d &> /dev/null; then
        echo -e "${GREEN}✅ Database container started${NC}"
        
        # Wait for database to be healthy
        echo "Waiting for database to be ready..."
        sleep 10
        
        if docker-compose ps | grep -q "healthy"; then
            echo -e "${GREEN}✅ Database is healthy${NC}"
        else
            echo -e "${RED}❌ Database health check failed${NC}"
            docker-compose down &> /dev/null
            return 1
        fi
        
        # Clean up
        docker-compose down &> /dev/null
        echo -e "${GREEN}✅ Database test completed${NC}"
    else
        echo -e "${RED}❌ Failed to start database${NC}"
        return 1
    fi
}

# Run all tests
echo "Starting Docker tests..."
echo "=========================="

failed_tests=0

test_docker || ((failed_tests++))
echo ""
test_docker_compose || ((failed_tests++))
echo ""
test_dockerfile || ((failed_tests++))
echo ""
test_docker_compose_file || ((failed_tests++))
echo ""
test_env_file || ((failed_tests++))
echo ""
test_docker_build || ((failed_tests++))
echo ""
test_database_startup || ((failed_tests++))

echo "=========================="
if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Docker setup is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure your bot token in .env file"
    echo "2. Run: ./start-docker.sh"
else
    echo -e "${RED}❌ $failed_tests test(s) failed. Please fix the issues above.${NC}"
    exit 1
fi
