import requests
import os
import re
import sys
from datetime import datetime, timedelta

def 获取60秒内容并保存(日期=None):
    """
    获取60秒读懂世界内容并保存
    
    Args:
        日期: 日期字符串，格式为 YYYY-MM-DD，如果不指定则获取最新内容
    """
    # 创建保存目录
    保存目录 = "./60s/"
    if not os.path.exists(保存目录):
        os.makedirs(保存目录)
    
    # 构建URL
    if 日期:
        # 如果有指定日期，添加到URL参数中
        请求URL = f"https://60s.mizhoubaobei.top/v2/60s?encoding=text&date={日期}"
    else:
        # 如果没有指定日期，获取最新内容
        请求URL = "https://60s.mizhoubaobei.top/v2/60s?encoding=text"
    
    try:
        # 发送GET请求，禁用SSL验证
        响应 = requests.get(请求URL, timeout=10, verify=False)
        响应.raise_for_status()  # 如果请求失败会抛出异常
        
        # 获取内容
        内容 = 响应.text
        
        # 从内容中提取日期
        日期模式 = r'每天 60s 看世界（(\d{4}-\d{2}-\d{2})）'
        匹配结果 = re.search(日期模式, 内容)
        
        if 匹配结果:
            实际日期 = 匹配结果.group(1)
            年份 = 实际日期[:4]
            月份 = 实际日期[5:7]
            
            # 创建年份和月份子目录
            日期目录 = os.path.join(保存目录, 年份, 月份)
            if not os.path.exists(日期目录):
                os.makedirs(日期目录)
            
            文件名 = f"{实际日期}.md"
            文件路径 = os.path.join(日期目录, 文件名)
            
            # 检查返回的日期是否与请求的日期一致
            if 日期 and 实际日期 != 日期:
                print(f"警告：请求日期 {日期}，但返回日期为 {实际日期}")
        else:
            # 如果没有匹配到日期，使用传入的日期或当前日期
            if 日期:
                实际日期 = 日期
            else:
                实际日期 = datetime.now().strftime("%Y-%m-%d")
            
            年份 = 实际日期[:4]
            月份 = 实际日期[5:7]
            日期目录 = os.path.join(保存目录, 年份, 月份)
            if not os.path.exists(日期目录):
                os.makedirs(日期目录)
            
            文件名 = f"{实际日期}.md"
            文件路径 = os.path.join(日期目录, 文件名)
            
            if not 日期:
                print("警告：未从内容中提取到日期，使用当前日期作为文件名")
        
        # 检查文件是否已存在
        if os.path.exists(文件路径):
            print(f"文件已存在：{文件路径}")
            return 文件路径, 内容
        
        # 写入文件
        with open(文件路径, 'w', encoding='utf-8') as 文件:
            文件.write(内容)
        
        print(f"成功保存文件：{文件路径}")
        print(f"文件内容长度：{len(内容)} 字符")
        
        return 文件路径, 内容
        
    except requests.exceptions.RequestException as 异常:
        print(f"请求失败：{异常}")
        return None, None
    except Exception as 异常:
        print(f"发生错误：{异常}")
        return None, None

def 重试失败日期(失败日期列表, 最大重试次数=3):
    """重试下载失败的日期"""
    if not 失败日期列表:
        return []
    
    print(f"\n开始重试 {len(失败日期列表)} 个失败的日期...")
    
    仍然失败的日期列表 = []
    
    for 日期 in 失败日期列表:
        print(f"\n重试下载 {日期} 的内容...")
        重试成功 = False
        
        for 重试次数 in range(最大重试次数):
            print(f"  第 {重试次数 + 1} 次重试...")
            文件路径, 内容 = 获取60秒内容并保存(日期=日期)
            
            if 文件路径 and 内容:
                print(f"  ✅ 重试成功")
                重试成功 = True
                break
            else:
                if 重试次数 < 最大重试次数 - 1:
                    print(f"  ⏳ 重试失败，等待后再次尝试...")
                    import time
                    time.sleep(2)  # 等待2秒后重试
        
        if not 重试成功:
            print(f"  ❌ 经过 {最大重试次数} 次重试仍然失败")
            仍然失败的日期列表.append(日期)
    
    return 仍然失败的日期列表

def 记录失败日期(失败日期列表):
    """将失败日期记录到日志文件"""
    if not 失败日期列表:
        return
    
    日志文件路径 = "./60s/失败日期.log"
    
    # 确保目录存在
    日志目录 = os.path.dirname(日志文件路径)
    if not os.path.exists(日志目录):
        os.makedirs(日志目录)
    
    # 读取现有的失败日期
    现有失败日期 = set()
    if os.path.exists(日志文件路径):
        with open(日志文件路径, 'r', encoding='utf-8') as 日志文件:
            for 行 in 日志文件:
                日期 = 行.strip()
                if 日期:
                    现有失败日期.add(日期)
    
    # 添加新的失败日期
    所有失败日期 = 现有失败日期.union(set(失败日期列表))
    
    # 写入日志文件
    with open(日志文件路径, 'w', encoding='utf-8') as 日志文件:
        for 日期 in sorted(所有失败日期):
            日志文件.write(日期 + '\n')
    
    print(f"\n已将 {len(失败日期列表)} 个失败日期记录到: {日志文件路径}")

def 下载最新内容():
    """下载最新内容"""
    print("\n开始获取最新内容...")
    文件路径, 内容 = 获取60秒内容并保存()
    
    if 文件路径 and 内容:
        print("\n文件保存成功！")
        print("=" * 50)
        行列表 = 内容.split('\n')[:5]
        for 行 in 行列表:
            print(行)
        if len(内容.split('\n')) > 5:
            print("...")
    else:
        print("文件保存失败！")

def 下载指定日期内容(日期输入):
    """下载指定日期内容"""
    if re.match(r'\d{4}-\d{2}-\d{2}', 日期输入):
        print(f"\n开始下载 {日期输入} 的内容...")
        文件路径, 内容 = 获取60秒内容并保存(日期=日期输入)
        
        if 文件路径 and 内容:
            print("\n文件保存成功！")
            # 检查日期是否匹配
            日期模式 = r'每天 60s 看世界（(\d{4}-\d{2}-\d{2})）'
            匹配结果 = re.search(日期模式, 内容)
            if 匹配结果:
                返回日期 = 匹配结果.group(1)
                if 返回日期 != 日期输入:
                    print(f"⚠️ 注意：请求日期 {日期输入}，但返回日期为 {返回日期}")
            
            print("=" * 50)
            行列表 = 内容.split('\n')[:5]
            for 行 in 行列表:
                print(行)
            if len(内容.split('\n')) > 5:
                print("...")
        else:
            print("文件保存失败！")
    else:
        print("日期格式不正确，请使用 YYYY-MM-DD 格式")

def 下载指定月份内容(月份输入=None, 年份输入=None):
    """下载指定月份的内容"""
    当前年份 = datetime.now().year
    
    try:
        if 月份输入 is None:
            月份输入 = input(f"请输入月份 (1-12，默认使用当前年份 {当前年份}): ").strip()
        
        if not 月份输入:
            print("未输入月份，使用当前月份")
            月份 = datetime.now().month
        else:
            月份 = int(月份输入)
            if 月份 < 1 or 月份 > 12:
                print("月份无效，使用当前月份")
                月份 = datetime.now().month
        
        if 年份输入 is None:
            年份输入 = input(f"请输入年份 (默认 {当前年份}): ").strip()
        if 年份输入:
            年份 = int(年份输入)
        else:
            年份 = 当前年份
        
        print(f"开始下载 {年份}年{月份:02d}月全月内容...")
        
        # 计算该月的第一天和最后一天
        开始日期 = datetime(年份, 月份, 1)
        if 月份 == 12:
            结束日期 = datetime(年份 + 1, 1, 1) - timedelta(days=1)
        else:
            结束日期 = datetime(年份, 月份 + 1, 1) - timedelta(days=1)
        
        当前日期 = 开始日期
        成功数量 = 0
        失败数量 = 0
        日期不匹配数量 = 0
        失败日期列表 = []
        
        while 当前日期 <= 结束日期:
            日期字符串 = 当前日期.strftime("%Y-%m-%d")
            print(f"\n正在下载 {日期字符串} 的内容...")
            
            文件路径, 内容 = 获取60秒内容并保存(日期=日期字符串)
            
            if 文件路径 and 内容:
                # 检查日期是否匹配
                日期模式 = r'每天 60s 看世界（(\d{4}-\d{2}-\d{2})）'
                匹配结果 = re.search(日期模式, 内容)
                
                if 匹配结果:
                    返回日期 = 匹配结果.group(1)
                    if 返回日期 == 日期字符串:
                        成功数量 += 1
                        print(f"  ✅ 下载成功")
                    else:
                        日期不匹配数量 += 1
                        print(f"  ⚠️ 日期不匹配: 请求{日期字符串}，返回{返回日期}")
                else:
                    成功数量 += 1
                    print(f"  ✅ 下载成功（未验证日期）")
                
                # 打印第一行内容预览
                行列表 = 内容.split('\n')
                for 行 in 行列表:
                    if 行.strip():
                        print(f"  {行}")
                        break
            else:
                失败数量 += 1
                失败日期列表.append(日期字符串)
                print(f"  ❌ 下载失败")
            
            当前日期 += timedelta(days=1)
            
            # 添加短暂延迟，避免请求过于频繁
            import time
            time.sleep(1)
        
        # 显示失败日期
        if 失败日期列表:
            print(f"\n失败的日期：{', '.join(失败日期列表)}")
            
            # 重试失败的日期
            最终失败日期列表 = 重试失败日期(失败日期列表)
            
            # 更新统计信息
            if 最终失败日期列表:
                成功数量 += (len(失败日期列表) - len(最终失败日期列表))
                失败数量 = len(最终失败日期列表)
                
                # 记录最终失败的日期
                记录失败日期(最终失败日期列表)
            else:
                成功数量 += len(失败日期列表)
                失败数量 = 0
        
        print(f"\n下载完成！")
        print(f"成功：{成功数量} 个文件")
        print(f"日期不匹配：{日期不匹配数量} 个文件") 
        print(f"失败：{失败数量} 个文件")
        
        if 日期不匹配数量 > 0:
            print("\n⚠️ 注意：部分文件日期不匹配，可能超过当前日期，或者服务器不支持过于久远的日期。")
            
    except ValueError:
        print("输入格式错误，请输入有效的数字")

def 下载日期范围内容(开始日期字符串, 结束日期字符串):
    """下载指定日期范围的内容"""
    try:
        开始日期 = datetime.strptime(开始日期字符串, "%Y-%m-%d")
        结束日期 = datetime.strptime(结束日期字符串, "%Y-%m-%d")
        
        print(f"开始下载 {开始日期字符串} 到 {结束日期字符串} 的内容...")
        
        当前日期 = 开始日期
        成功数量 = 0
        失败数量 = 0
        日期不匹配数量 = 0
        失败日期列表 = []
        
        while 当前日期 <= 结束日期:
            日期字符串 = 当前日期.strftime("%Y-%m-%d")
            print(f"\n正在下载 {日期字符串} 的内容...")
            
            文件路径, 内容 = 获取60秒内容并保存(日期=日期字符串)
            
            if 文件路径 and 内容:
                # 检查日期是否匹配
                日期模式 = r'每天 60s 看世界（(\d{4}-\d{2}-\d{2})）'
                匹配结果 = re.search(日期模式, 内容)
                
                if 匹配结果:
                    返回日期 = 匹配结果.group(1)
                    if 返回日期 == 日期字符串:
                        成功数量 += 1
                        print(f"  ✅ 下载成功")
                    else:
                        日期不匹配数量 += 1
                        print(f"  ⚠️ 日期不匹配: 请求{日期字符串}，返回{返回日期}")
                else:
                    成功数量 += 1
                    print(f"  ✅ 下载成功（未验证日期）")
                
                # 打印第一行内容预览
                行列表 = 内容.split('\n')
                for 行 in 行列表:
                    if 行.strip():
                        print(f"  {行}")
                        break
            else:
                失败数量 += 1
                失败日期列表.append(日期字符串)
                print(f"  ❌ 下载失败")
            
            当前日期 += timedelta(days=1)
            
            # 添加短暂延迟，避免请求过于频繁
            import time
            time.sleep(1)
        
        # 显示失败日期
        if 失败日期列表:
            print(f"\n失败的日期：{', '.join(失败日期列表)}")
            
            # 重试失败的日期
            最终失败日期列表 = 重试失败日期(失败日期列表)
            
            # 更新统计信息
            if 最终失败日期列表:
                成功数量 += (len(失败日期列表) - len(最终失败日期列表))
                失败数量 = len(最终失败日期列表)
                
                # 记录最终失败的日期
                记录失败日期(最终失败日期列表)
            else:
                成功数量 += len(失败日期列表)
                失败数量 = 0
        
        print(f"\n下载完成！")
        print(f"成功：{成功数量} 个文件")
        print(f"日期不匹配：{日期不匹配数量} 个文件")
        print(f"失败：{失败数量} 个文件")
        
        if 日期不匹配数量 > 0:
            print("\n⚠️ 注意：部分文件日期不匹配，可能服务器不支持日期参数")
        
    except ValueError as 异常:
        print(f"日期格式错误：{异常}")

def 显示使用说明():
    """显示使用说明"""
    print("""
60秒读懂世界内容下载工具

交互模式：
  python 60s.py                    # 进入交互菜单

快捷指令模式：
  python 60s.py latest             # 下载最新内容
  python 60s.py date 2025-10-01    # 下载指定日期
  python 60s.py month 10           # 下载当前年份的指定月份
  python 60s.py month 10 2025      # 下载指定年份和月份
  python 60s.py range 2025-10-01 2025-10-07  # 下载日期范围
  python 60s.py help               # 显示此帮助信息

示例：
  python 60s.py latest
  python 60s.py date 2025-09-15
  python 60s.py month 9
  python 60s.py month 9 2025
  python 60s.py range 2025-09-01 2025-09-30
""")

def 处理命令行参数():
    """处理命令行参数"""
    if len(sys.argv) == 1:
        return None
    
    命令 = sys.argv[1].lower()
    
    if 命令 == "latest":
        return {"类型": "latest"}
    elif 命令 == "date" and len(sys.argv) == 3:
        return {"类型": "date", "日期": sys.argv[2]}
    elif 命令 == "month" and len(sys.argv) == 3:
        return {"类型": "month", "月份": sys.argv[2], "年份": None}
    elif 命令 == "month" and len(sys.argv) == 4:
        return {"类型": "month", "月份": sys.argv[2], "年份": sys.argv[3]}
    elif 命令 == "range" and len(sys.argv) == 4:
        return {"类型": "range", "开始日期": sys.argv[2], "结束日期": sys.argv[3]}
    elif 命令 in ["help", "-h", "--help"]:
        return {"类型": "help"}
    else:
        print("无效的命令行参数")
        显示使用说明()
        return {"类型": "invalid"}

def 主程序():
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 处理命令行参数
    命令行参数 = 处理命令行参数()
    
    if 命令行参数:
        # 快捷指令模式
        if 命令行参数["类型"] == "latest":
            下载最新内容()
        elif 命令行参数["类型"] == "date":
            下载指定日期内容(命令行参数["日期"])
        elif 命令行参数["类型"] == "month":
            下载指定月份内容(命令行参数["月份"], 命令行参数["年份"])
        elif 命令行参数["类型"] == "range":
            下载日期范围内容(命令行参数["开始日期"], 命令行参数["结束日期"])
        elif 命令行参数["类型"] == "help":
            显示使用说明()
        return
    
    # 交互模式
    print("60秒读懂世界内容下载工具")
    print("1. 下载最新内容")
    print("2. 下载指定日期内容")
    print("3. 下载指定月份内容")
    print("4. 下载指定日期范围内容")
    print("5. 显示使用说明")
    
    选择 = input("请选择操作 (1/2/3/4/5): ").strip()
    
    if 选择 == "1":
        下载最新内容()
    elif 选择 == "2":
        日期输入 = input("请输入日期 (格式: YYYY-MM-DD): ").strip()
        下载指定日期内容(日期输入)
    elif 选择 == "3":
        下载指定月份内容()
    elif 选择 == "4":
        开始日期 = input("请输入开始日期 (格式: YYYY-MM-DD): ").strip()
        结束日期 = input("请输入结束日期 (格式: YYYY-MM-DD): ").strip()
        if re.match(r'\d{4}-\d{2}-\d{2}', 开始日期) and re.match(r'\d{4}-\d{2}-\d{2}', 结束日期):
            下载日期范围内容(开始日期, 结束日期)
        else:
            print("日期格式不正确，请使用 YYYY-MM-DD 格式")
    elif 选择 == "5":
        显示使用说明()
    else:
        print("无效选择，请重新运行程序")

if __name__ == "__main__":
    主程序()