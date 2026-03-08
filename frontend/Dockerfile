# Node.js 基础镜像
FROM node:20

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制 frontend 代码
COPY . .

# 暴露 Next.js 开发端口
EXPOSE 3000

# 启动 Next.js dev
CMD ["npm", "run", "dev"]