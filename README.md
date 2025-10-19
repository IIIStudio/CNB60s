```shell
cnb-init-from https://cnb.cool/RubyOSS/Template/Python
```

```yml
$:
  vscode:
    - services:
      - vscode
      - docker
      runner:
        cpus: 32
      env:
        CNB_WELCOME_CMD: |
          docker compose up -d
          python start.py
      # 开发环境在销毁之前执行的任务
      endStages:
        - name: sync code
          script: git add . && git commit -m "自动提交：$(date "+%Y-%m-%d %H:%M:%S")" && git push
```
start.py
```py
import sys
import os
import webbrowser

端口 = sys.argv[1] if len(sys.argv) > 1 else "3000"
原始网址 = os.getenv("CNB_VSCODE_PROXY_URI")
应用网址 = 原始网址.replace("{{port}}", 端口)

print("访问地址为：")
print(f'- {应用网址}')
print(f'密码：666')
浏览器 = webbrowser.open_new_tab(应用网址)
```