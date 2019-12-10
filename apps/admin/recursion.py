# -*- coding:utf-8 -*-
def creat_commont_tree(data,p_id,level=0):
    tree = []
    for row in data:
        if row['parent_id'] ==p_id:
            row['level'] = level
            child = creat_commont_tree(data, row['id'], level+1)
            row['child'] = []
            if child:
                row['child'] += child
            tree.append(row)

    return tree
def creat_table(data, parent_title='顶级菜单'):
    html = ''
    for row in data:
        splice = '├ '
        id=row['id']
        title=row['title']
        comment = splice * row['level'] + row['comment']
        parent_id=row['parent_id']
        user_name=row['user_name']
        status = row['status']
        add_time=row['add_time']
        comment_ip=row['comment_ip']
        if status==0:
            status="已发布"
            status1 = "要下架？"
            status2='&#xe6de'
            status3="comment_stop"
        else:
            status="已下架"
            status1 = "要发布？"
            status2='&#xe603'
            status3="comment_start"
        tr_td = """<tr class="text-c">
					<td><input type="checkbox" value="" name="smallBox" id="smallBox"></td>
					<td>{id}</td>
					<td class="text-l">{comment}<u style="cursor:pointer" class="text-primary" onClick="comment_edit('查看','{id}','')" title="查看"></u></td>
					<td>{title}</td>
					<td>{user_name}</td>
					<td>{add_time}</td>
					<td>{comment_ip}</td>
					<td class="td-status">					
					<span class="label label-success radius">{status}</span>				
					</td>
					<td class="f-14 td-manage">					
					<a style="text-decoration:none" onClick="{status3}(this,'{id}')" href="javascript:;" title="{status1}"><i class="Hui-iconfont">{status2};</i></a> 				
					 
					<a style="text-decoration:none" class="ml-5" onClick="comment_del(this,'{id}')" href="javascript:;" title="删除"><i class="Hui-iconfont">&#xe6e2;</i></a></td>
				</tr>
                                                 """
        if row['child']:
            html += tr_td.format(class_name='top_menu', title=title,id=id,comment=comment,status=status,status1=status1,status2=status2,status3=status3,parent_id=parent_id,add_time=add_time,comment_ip=comment_ip,user_name=user_name)
            html += creat_table(row['child'], row['comment'])
        else:
            html += tr_td.format(class_name='', title=title,id=id,comment=comment,status=status,status1=status1,status2=status2,status3=status3,parent_id=parent_id,add_time=add_time,comment_ip=comment_ip,user_name=user_name)

    return html
#权限分类排序
def build_auth_tree(data,p_id,level=0):
    """
    生成树菜单
    :param data:    数据
    :param p_id:    上级分类
    :param level:   当前级别
    :return:
    """
    tree = []
    count=0
    for row in data:
        if row['parent_id'] ==p_id:
            row['level'] = level
            child = build_auth_tree(data, row['id'], level+1)
            row['child'] = []
            if child:
                row['child'] += child
            tree.append(row)
    return tree
#生成分类
def build_auth_table(data, parent_title='顶级菜单'):
    html = ''
    for row in data:
        splice = '├ '
        cat_id=row['id']
        title = splice * row['level'] + row['name']
        tr_td = """<option value={cat_id}>  {title}</option>
                                   """
        if row['child']:
            html += tr_td.format(class_name='top_menu', title=title,cat_id=cat_id)
            html += build_auth_table(row['child'], row['name'])
        else:
            html += tr_td.format(class_name='', title=title,cat_id=cat_id)
            # return html
    return html
#生成角色分类树
count=0
flag=0
def creat_auth_table(data, parent_title='顶级菜单'):
    html = ''
    global count
    global flag
    for row1 in data:
        if row1['child']:
            flag=0
        else:
            if row1['parent_id']:
                flag+=1
            else:
                flag=0

    for row in data:
        splice = '-- '
        cat_id=row['id']
        title = splice * row['level'] + row['name']
        parent_id=row['parent_id']
        level=row['level']
        tr_td = """
        
      <dl class="permission-list">
					<dt>
						<label>
							<input type="checkbox" value="{cat_id}" name="user-Character-0" id="user-Character-{cat_id}-{level}">
							{title}</label>
					</dt>
					<dd>
						<dl class="cl permission-list2"><dd>
                                   """

        tl_td = """
        
						<label>
							<input type="checkbox" value="{cat_id}" name="user-Character-1-0-0" id="user-Character-{parent_id}-{cat_id}">
							{title}</label>
					
                                          """
        tl_td_end = """
        </dd></dl></dd></dl>
                                """
        if row['child']:#父节点,有子节点
            html += tr_td.format(class_name='top_menu', title=title,cat_id=cat_id,parent_id=parent_id,level=level)
            count=0
            html += creat_auth_table(row['child'], row['name'])


        else:#父节点，没有子节点
            if row['parent_id']:#子节点
                html += tl_td.format(class_name='', title=title,cat_id=cat_id,parent_id=parent_id,level=level)
                count+=1
                if flag==count:
                    html += tl_td_end.format(class_name='', title=title, cat_id=cat_id,parent_id=parent_id,level=level)
            else:#父节点，但是没有子节点
                html += tr_td.format(class_name='', title=title, cat_id=cat_id,parent_id=parent_id,level=level)
                html += tl_td_end.format(class_name='', title=title, cat_id=cat_id,parent_id=parent_id,level=level)
                count=0





    return html