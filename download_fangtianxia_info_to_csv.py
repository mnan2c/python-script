import requests
from bs4 import BeautifulSoup
import re
import csv

def get_all_page_data(count):
    total_list=[]
    i=1
    while i <= int(count):
        print("开始下载第 %d 页.." % (i))
        total_list+=get_data_by_page_number(i)
        i+=1
    write_to_csv_file(total_list)

def get_data_by_page_number(pageNumber):
    r = requests.get('http://suzhou.newhouse.fang.com/house/s/b9'+str(pageNumber))
    r.encoding='gb2312'
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    house_info_tags = soup.find_all('div', class_="nlc_details")
    return build_json_data(house_info_tags)

def build_json_data(house_info_tags):
    house_list = []
    for house_info in house_info_tags:
        house_data = {}
        house_link_tag=house_info.select('div[class="nlcd_name"] > a')[0]
        # 1
        house_link=house_link_tag.get("href")
        house_data["小区链接"]=house_link
        # 2
        original_name=house_link_tag.string
        target_name=get_pure_str(original_name)
        house_data["小区名称"]=target_name
        # 3
        comment_tags=house_info.select("span[class='value_num']")
        comment_count=0
        if len(comment_tags) != 0:
            comment_count=comment_tags[0].string.split('条',1)[0][1:]
        house_data["评论数"]=comment_count
        # 4
        house_type=house_info.select("div[class='house_type clearfix']")[0]
        rooms=get_tag_content(house_type.select("a"))
        if len(rooms) > 0 and len(rooms[0]) < 5:
            house_data["房间数"]=rooms
        else:
            house_data["房间数"]=''
        # 5
        target_size=get_pure_str(house_type.contents[-1])[1:]
        house_data["大小"]=target_size
        # 6
        area=house_info.select("span[class='sngrey']")
        if len(area) == 0:
            area=""
        else:
            area=get_pure_str(area[0].string)[1:-1]
        house_data["区域"]=area
        # 7
        in_sale=house_info.select("span[class='inSale']")
        if len(in_sale) == 0:
            in_sale="未知"
        else:
            in_sale=in_sale[0].string
        house_data["销售状态"]=in_sale
        # 8
        home_types=house_info.select("div[class='fangyuan'] > a")
        home_types=get_tag_content(home_types)
        house_data["小区类型"]=home_types
        # 9
        price=house_info.select("div[class='nhouse_price']")
        digit=""
        unit=""
        if len(price) > 0 and len(price[0].select("span")) > 0:
            digit=price[0].select("span")[0].string
            hasPrice=True
            try:
                int(digit)
            except ValueError:
                digit="价格未知"
                hasPrice=False
            if hasPrice:
                if int(digit) > 5000:
                    unit="元/平米"
                else:
                    unit="万元/套"
        house_data["价格"]=digit
        house_data["价格单位"]=unit

        house_list.append(house_data)
    return house_list

def write_to_csv_file(obj_list):
    fileHeader=["小区名称","价格","价格单位","小区链接","评论数","房间数","大小","区域","销售状态","小区类型"]
    # newline=''去掉多余的空行
    csvFile=open("house_statics.csv","w",newline='')

    dict_writer=csv.DictWriter(csvFile, fileHeader)
    dict_writer.writerow(dict(zip(fileHeader,fileHeader)))
    for obj in obj_list:
        try:
            dict_writer.writerow(obj)
        except UnicodeEncodeError:
            print("%s 写入失败.." % (obj["小区名称"]))
    print("成功写入 %d 条房产信息数据！" % (len(obj_list)))
    csvFile.close()

def get_tag_content(list):
    result=[]
    for item in list:
        if len(item.contents) != 0:
            result.append(item.contents[0])
    return result

def get_pure_str(origin_str):
    return re.sub(r"[\t\n]*","",origin_str)

if __name__ == '__main__':
    count=input("请输入页数：")
    get_all_page_data(count)
