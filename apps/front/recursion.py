# -*- coding:utf-8 -*-
#分类排序
def build_cat_tree(data,p_id,level=0):
    tree = []
    count=0
    for row in data:
        if row['parent_id'] ==p_id:
            row['level'] = level
            child = build_cat_tree(data, row['cat_id'], level+1)
            row['child'] = []
            if child:
                row['child'] += child
            tree.append(row)
    return tree
#生成分类
count=0
flag=0
def build_cat_table(data, parent_title='顶级菜单'):
    html = ''
    global count
    global flag
    for row in data:
        splice = ' '
        cat_id=row['cat_id']
        title = splice * row['level'] + row['cat_name']
        tr_td = """
        
<li><a href="">{title}</li>	</a>				

                                   """
        tr_td_left = """

        <li><a href="">{title}	</a>			

                                           """
        p_tr_td_left = """

        </li>			

                                           """

        child_tr_td_left = """
                <ul>                
                  """
        child_tr_td_right = """   
             </ul></li>	     """
        if row['child']:#父节点，有子节点



            html += tr_td_left.format(class_name='top_menu', title=title,cat_id=cat_id)
            html += build_cat_table(row['child'], row['cat_name'])
            if row['level']==0:
                count=0
                html += child_tr_td_right.format(class_name='top_menu', title=title, cat_id=cat_id)

        else:#父节点，没有有子节点
            # print(row['cat_name'])
            if row['level'] == 0:

                html += tr_td_left.format(class_name='', title=title, cat_id=cat_id)

            if row['parent_id']:  #是子节点，但是该子节点下没有子节点了
                count += 1
                if count==1:
                    html += child_tr_td_left.format(class_name='top_menu', title=title, cat_id=cat_id)
                html += tr_td.format(class_name='', title=title, cat_id=cat_id)
            else:
                html += p_tr_td_left.format(class_name='top_menu', title=title, cat_id=cat_id)

    return html