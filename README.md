---
- name: "{{name}}"
- type: auto hotkey
- lang: python
- description: "{{description}}"
- author: "{{author}}"
- github-id: "{{github-id}}"
---

## install

```sh
# cd [PARENT DIR]
cd {{current-dir}}

# <syntax> xcli -e init -r "[REPO_NAME]||[USER_NAME]||[TEMPLATE_NAME]||[DESCRIPTION]"
xcli -e init -r "{{name}}||{{github-id}}||py-pipenv-ahk||{{description}}"

# package install
pip install -r requirements.txt 
```

## functions

