# 在线拼音输入法

这是一个简单的在线中文输入法，后端基于 HMM 模型，前端基于 `React` 和 `Chakra UI`

目前仅支持在电脑端使用，**使用时请关闭电脑自带的输入法**

## 立即体验

### 使用在线 Demo

访问 https://ime.caomingjun.com 即可

### Docker 部署

在安装了 Docker 的机器上运行命令：`docker run -p 8080:80 caomingjun/webime` 并访问 `http://localhost:8080` 

## 开发

### 前端

进入 `frontend` 目录并运行 `npm ci` 以安装依赖。

`npm start` 启动开发服务器（端口 3000），`npm run build` 构建。

> 注意此时的无法访问后端，需要在 `frontend/src/components/InputArea.tsx` 中将 `serverURL` 改为 `http://localhost:5000/api/candidate` 并启动后端的开发服务器。

### 后端

在根目录运行 `pip install -r requirements.txt`

运行 `python server.py` 启动开发服务器（端口 5000）。

### 构建 Docker 并运行

> 构建前记得把 `serverURL` 改回去

```bash
$ docker build -t webime .
$ docker run -p 8080:80 caomingjun/webime
```



