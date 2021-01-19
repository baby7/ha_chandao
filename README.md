# ha_chandao
禅道接入HomeAssistant，可以查看任务和Bug的数量

### 安装
将```ha_chandao```文件夹复制到```custom_components/```目录下重启hass

### 配置

```
sensor:
  - platform: chandao
    name: '你的项目名'
    url: '禅道地址'
    username: '用户名'
    password: '密码'
    project_id: '项目id'
```

* url : 禅道地址，例如https://www.test.com:1234，不需要加/zentao
* project_id : 项目id，在项目的任务界面，可以看到地址栏后面有个```project-task-999.html```这样的地址，取后面的数字即可
