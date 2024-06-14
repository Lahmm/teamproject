# teamproject
 MISY410_team_project
# 修改所选页面高亮方法
如果当前页面属于payment的子页面  
在`{% block content %}`上一行中添加`{% block payactive %}text-uppercase fs-5 text-start border-0{% endblock payactive %}`  
如果当前页面属于order的子页面  
在`{% block content %}`上一行中添加`{% block orderactive %}text-uppercase fs-5 text-start border-0{% endblock orderactive %}`  
# 仓库使用方法
- fork本仓库至自己的GitHub仓库
- clone到本地的一个位置（不要覆盖原有代码）
- 根据原有代码更改本代码
- 将更新的代码上传至自己的仓库
- pull request至源仓库
- 可通过fetch下拉更新后的代码