# 在线拼音输入法

这是一个简单的在线中文输入法，后端基于 HMM 模型，前端基于 `React` 和 `Chakra UI`

目前仅支持在电脑端使用，**使用时请关闭电脑自带的输入法**

## Docker 部署

在安装了 Docker 的机器上运行命令：`docker run -p 8080:80 caomingjun/webime` 并访问 `http://localhost:8080` 

## 开发容器

本仓库包含了 `.devcontainer` ，可以在 VSCode 内使用开发容器打开。

在创建容器时会安装所有依赖并进行前端构建。完成后可以直接运行 `python server.py` 启动服务器。容器也内置了 Docker ，运行下面的命令即可构建并测试 Docker：

```bash
$ docker build -t webime .
$ docker run -p 8080:80 caomingjun/webime
```

VSCode 会处理好端口转发。

## 本地开发

如果你要在本地开发，可以执行下面的步骤。

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

## 致谢

HMM 模型的训练使用了[北京语言大学BCC语料库](http://bcc.blcu.edu.cn/)。

