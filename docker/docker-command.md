docker login docker.cnb.cool -u cnb -p 7FTxER23109aSdK1OplKAbQkkQD

**1、构建镜像**

# AMD64 架构
docker build --platform linux/amd64 -f docker/Dockerfile -t docker.cnb.cool/huanglixian/gdy-docker/data-clean:latest .

**2、推送镜像**

docker push docker.cnb.cool/huanglixian/gdy-docker/data-clean:latest

=== 新增：导出和导入镜像 ===
导出镜像为 tar 文件（适合离线迁移/备份）
docker save -o data-clean-latest.tar docker.cnb.cool/huanglixian/gdy-docker/data-clean:latest

导入镜像 tar 文件（适合离线恢复/迁移）
docker load -i data-clean-latest.tar

**3、启动/停止镜像**

进入各自文件夹：

docker-compose up -d  # 普通启动
docker compose up -d  # 新版命令

docker-compose pull && docker-compose up -d   # 更新镜像并启动
docker compose pull && docker compose up -d   # 新版命令

docker-compose down  # 停止镜像
docker compose down  # 新版命令

**4、自己运行**

docker-compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml up -d

docker-compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml down