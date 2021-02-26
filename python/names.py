#coding=utf-8
lastname_list = {
    "9":["怡",'玥','思','姝','星','昱'],
    '8':['依','亚','佳','炘','林'],
    '3':['上','千','子','弋']
}

nextname_list = {
    '7':['彤','希','言','含','妤','君'],
    '8':['卓','妮','奇','宜','东'],
    '14':['榕','瑞','菁','歌']
}
new_name_list = list()
lastname = lastname_list['3']
nextname = nextname_list['14']
for item in lastname:
    for item2 in nextname:
        new_name = "刘" + item2 + item
        new_name_list.append(new_name)

print(new_name_list)


