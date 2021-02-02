# PM Lab Courseback/AppD 应用迁移指南

## 确保AppD正常启动

-   确保把Enterprise Console启动起来，参考如下命令：

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/home/appdynamics/platform/platform-admin/bin/platform-admin.sh start-platform-admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   然后在9191端口的GUI里把Controller连同数据库一起启动起来

-   安装新的License：

    -   把License文件xxxx.lic拷贝到/appdynamics/platform/product/controller目录下面

    -   记下Access Key

-   确保所有VM要解除防火墙保护

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
firewall-cmd --state
systemctl stop firewalld.service
systemctl disable firewalld.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   确保AppD服务器通过带内能够与NI连接，按需要添加静态路由，比如

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
vi /etc/sysconfig/network-scripts/route-ens192    
创建了该文件并添加如下内容
192.168.6.0/24 via 172.16.1.1 dev ens192
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   重启网络或主机

## 部署新的应用、App Agent和Machine Agent

-   web01和app02虚机里挑出和老Controller关联的进程，逐一杀掉（新启动的VM一般不需要，我没有设置开机应用加载）

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
挑出App Agent：ps aux | grep 172.16.1.97
挑出Machine Agent：ps aux | grep machineagent.jar
kill -9 <进程号>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   修改主机agent的配置，让其关联新Controller：

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
App Agent：vi /home/javaagent/conf/controller-info.xml
Machine Agent：vi /home/machineagent/conf/controller-info.xml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   修改其中的IP地址为新Controller，如果没有IP地址，则说明是在启动应用的时候配置的Controller信息，那么就在下面的启动步骤中用新的IP地址（我忘了我是用的哪一种方式，可能不同的node用的方式不同，都看一下）

    -   修改其中的License Key为刚才拷贝下来的新key

-   启动应用进程和App
    agent（两个应用，一个AppD官方的单机演示应用Vinyl-Fanatics，一个是我的courseback）

    -   在home目录下执行如下命令：

        -   web01虚机上：

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nohup java -javaagent:/home/javaagent/javaagent.jar -Dappdynamics.socket.collection.bci.enable=true -Dappdynamics.controller.hostName=172.16.1.97 -Dappdynamics.controller.port=8090 -Dappdynamics.agent.applicationName=Vinyl-Fanatics -Dappdynamics.agent.tierName=FrontEnd -Dappdynamics.agent.nodeName=FrontEndNode1 -Dhttp.ports=18010,18011 -jar /home/trainingapp/testappserver.jar /home/trainingapp/1stTierconfig.xml &
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nohup java -javaagent:/home/javaagent/javaagent.jar -Dappdynamics.controller.hostName=172.16.1.97 -Dappdynamics.controller.port=8090 -Dappdynamics.agent.applicationName=Vinyl-Fanatics -Dappdynamics.agent.tierName=OrderProcessing -Dappdynamics.agent.nodeName=OrderProcessingNode1 -Dhttp.port=18030 -jar /home/trainingapp/testappserver.jar /home/trainingapp/3dTierconfig.xml &
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nohup java -javaagent:/home/javaagent/javaagent.jar -Dappdynamics.controller.hostName=172.16.1.97 -Dappdynamics.controller.port=8090 -Dappdynamics.agent.applicationName=Vinyl-Fanatics -Dappdynamics.agent.tierName=Inventory -Dappdynamics.agent.nodeName=InventoryNode1 -Dhttp.port=18020 -jar /home/trainingapp/testappserver.jar /home/trainingapp/2ndTierconfig.xml &
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nohup java -javaagent:/home/javaagent/javaagent.jar -Dappdynamics.controller.hostName=172.16.1.97 -Dappdynamics.controller.port=8090 -Dappdynamics.agent.applicationName=Vinyl-Fanatics -Dappdynamics.agent.tierName=FrontEnd -Dappdynamics.agent.nodeName=FrontEndNode1 -Dhttp.ports=18010,18011 -jar /home/trainingapp/testappserver.jar /home/trainingapp/1stTierconfig.xml &
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nohup java -javaagent:/home/javaagent/javaagent.jar -Dappdynamics.controller.hostName=172.16.1.97 -Dappdynamics.controller.port=8090 -Dappdynamics.agent.applicationName=courseback -Dappdynamics.agent.tierName=coursefront -Dappdynamics.agent.nodeName=coursefront1 -jar /home/frontdemo-0.0.1-SNAPSHOT.jar &
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   app02虚机上：

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nohup java -javaagent:/home/javaagent/javaagent.jar -Dappdynamics.controller.hostName=172.16.1.97 -Dappdynamics.controller.port=8090 -Dappdynamics.agent.applicationName=courseback -Dappdynamics.agent.tierName=coursefund -Dappdynamics.agent.nodeName=courseback1 -jar /home/demo-0.0.1-SNAPSHOT.jar &
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   检查以上新进程是否在：ps aux \| grep 172.16.1.97

    -   db01主机上：mysql数据库可能需要重启一下（一般开机会自动加载）

        -   先停：service mysqld stop

        -   再重启：service mysqld start

-   启动Machine agent（内含Network Visibility Agent）

    -   在web01和app02输入如下启动Machine agent的命令（Network Visibility
        Agent会一起启动）

        nohup /home/machineagent/jre/bin/java
        \-Dlog4j.configuration=file:/home/machineagent/conf/logging/log4j.xml
        \-jar /home/machineagent/machineagent.jar &

    -   检查新进程是否在：

        -   查看machine agent：ps aux \| grep machineagent.jar

        -   查看appd net monitor和net agent：ps aux \| grep appd-net

-   回到AppD Server看应用是否已发现

-   修改Java
    Agent汇报规则，让其对实现自主发包的类和方法作为正常事务来进行监控：应用courseback是一个通过web点击实现Transaction的应用，为了演示效果，需要写一段代码自动生成模仿点击效果的Transaction，但AppD默认对这种代码不做监控，因此有如下配置来修改这个行为：

    -   进入courseback应用的Application菜单：Application---\>Configuration---\>Instrumentation（做配置以定义监控内容）----\>Transaction
        Detection（做配置以定义监测哪些Transaction）

    -   点击上方的Add Rule

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Agent Type=Java
Entry Point Type=POJO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   点击Next，进入Summary

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Name=自己取个名字，比如autodemo
Enable=保证是checked的
Priority=10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   点击Rule Configuration，指明要监控哪一个类和哪一个方法

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
with a Class Name that = com.yjxy.demo.frontdemo.HttpClientUtil
Method Name = doGet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   Save退出

-   等待一段时间，所有应用Flow Map应当能够显示在对应应用的Dashboard和Network
    Dashboard里
