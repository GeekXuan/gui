#coding:utf-8
#需要安装pillow库 ~$pip3 install pillow
#Edit by:王智轩
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo
from PIL import Image,ImageTk
import threading,os,shutil,codecs,random
#----------------全局变量-------------------
mut = 1.7     #放大倍数
split_path = ''
split_list = []
filepath = ''
img_list = []
t_result = []
check_all = []
number = 0
if os.path.exists('btn.txt'):
    trans_list = {}
    with codecs.open('btn.txt', 'r', 'utf-8') as f:
        btnlist = [i.strip() for i in f.readlines() if i.strip() != '']
    for i, j in enumerate(btnlist):
        trans_list[str(i+1)] = j
else:
    trans_list = {'1': '待定', '2': '合格', '3': '不合格'}


def main():
    # -----------------func------------------------
    def start_thread(func, *myargs):#开启多线程
        t = threading.Thread(target = func, args = myargs)
        t.start()

    def info():#信息
        str_temp1 = '文件：' + img_list[number] + '\n大小：%d x %d\n' % (my_width,my_height)
        str_temp2 = '第' + str(number + 1) + '/' + str(len(img_list)) + '张； 进度：%.2f' % ((number+1)/len(img_list) * 100) + '%\n'
        str_temp3 = ''
        temp = t_result[number].split()
        for each in temp[1:]:
            a = len([x for x in t_result if each.split(':')[0] in x])
            b = len([x for x in check_all if each.split(':')[0] in x])
            str_temp3 += each + ';盲审不一致率：%.2f%%\n' % (a/b*100)
        show_num_label['text'] = str_temp1 + str_temp2 + str_temp3
        show_num_label.text = str_temp1 + str_temp2 + str_temp3

    def show_pic():#显示图片
        global my_height, my_width
        filename = os.path.join(filepath,'盲审不一致',img_list[number])
        im = Image.open(filename)
        w, h = im.size
        my_width = w
        my_height = h
        im = im.resize((int(mut * w), int(mut * h)))
        img = ImageTk.PhotoImage(im)
        pic_label['image'] = img
        pic_label.image = img

    def pre():#上一页
        global number
        if number == 0:
            showinfo('提示','当前已经是第一张！')
        else:
            number -= 1
            show_pic()
            info()
        e.set(number+1)


    def next():#下一页
        global number
        if number == len(img_list) - 1:
            showinfo('提示', '当前已经是最后一张！')
        else:
            number += 1
            show_pic()
            info()
        e.set(number+1)

    def topic():#跳转
        global number
        pagenum = e.get()
        if pagenum.isdigit() and 0 < int(pagenum) <= len(img_list):
            number = int(pagenum) - 1
            show_pic()
            info()
        elif pagenum in img_list:
            number = img_list.index(pagenum)
            show_pic()
            info()
        elif pagenum+'.jpg' in img_list:
            number = img_list.index(pagenum+'.jpg')
            show_pic()
            info()
        else:
            showinfo('提示', '请输入正确的页数或文件名！')

    # 调整大小
    def set_mut():
        global mut
        mutt = e2.get()
        try:
            mut = float(mutt)
            show_pic()
        except:
            showinfo('提示', '请输入正确的倍数！')

    # 分配图片选择文件夹
    def choose_folder():
        global split_list,split_path
        split_path = askdirectory(initialdir=".", title='Pick a directory')
        split_list = [i for i in os.listdir(split_path) if i.endswith('.jpg')]
        #showinfo('提示', '共有%s张图片。'  % (len(split_list)))
        e_num_all.set(len(split_list))
        e_num_spl.set(3)
        temp = len(split_list) // 10
        e_num_per.set(temp if temp > 3 else 3)

    # 分配图片
    def split_img():
        global newlist
        flag = True
        #验证数据输入的正确性
        if split_path == '':
            showinfo('提示', '请选择图片文件夹！')
            return
        try:
            t_all = int(e_num_all.get())
            if not 2 <= t_all <= len(split_list):
                showinfo('提示', '分配数量应当在2-%d之间！'%(len(split_list)))
                return
        except:
            showinfo('提示', '分配数量输入不正确！')
            return
        try:
            t_spl = int(e_num_spl.get())
            if not 1 <= t_spl <= t_all:
                showinfo('提示', '分配份数应当在1-%d之间！'%(t_all))
                return
        except:
            showinfo('提示', '分配份数输入不正确！')
            return
        t_per = e_num_per.get()
        if t_per == '0':
            t_per = 0
            flag = False
        elif t_per.endswith('%'):
            try:
                t_per = float(e_num_per.get().strip('%'))
                t_per = int(t_per * t_all / 100)
                if t_per > t_all:
                    showinfo('提示', '盲审数量不能大于分配数量！')
                    return
                if mut_func(t_spl - 1) > t_all:
                    showinfo('提示', '分配数量过少或分配份数过多，无法实现盲审！')
                    return
                if not mut_func(t_spl - 1) <= t_per:
                    showinfo('提示', '盲审百分比应当在%.2f%%-%.2f%%之间！' % ((mut_func(t_spl - 1)/t_all*100,100)))
                    return
            except:
                showinfo('提示', '盲审百分比输入不正确！')
        else:
            try:
                t_per = int(e_num_per.get())
                if t_per > t_all:
                    showinfo('提示', '盲审数量不能大于分配数量！')
                    return
                if mut_func(t_spl - 1) > t_all:
                    showinfo('提示', '分配数量过少或分配份数过多，无法实现盲审！')
                    return
                if not mut_func(t_spl - 1) <= t_per:
                    showinfo('提示', '盲审数量应当在%d-%d之间！' % ((mut_func(t_spl - 1),t_all)))
                    return
            except:
                showinfo('提示', '盲审数量输入不正确！')
                return
        #开始分配
        os.chdir(split_path)
        newlist = split_list[:t_all]
        checklist = random.sample(newlist, t_per)
        for x in checklist:
            newlist.remove(x)
        num_new = len(newlist)
        # 划分不盲审的
        spl_num_list = [0]
        mut = num_new // t_spl
        spl_num_list.extend([mut] * t_spl)
        for i in range(num_new % t_spl):
            spl_num_list[i + 1] += 1
        for i in range(t_spl):
            spl_num_list[i + 1] += spl_num_list[i]
        # 移动图片
        folder_name = os.path.split(os.getcwd())[1]
        for i in range(t_spl):
            i += 1
            name_temp = folder_name + '_' + str(i).rjust(len(str(t_spl)))
            if not os.path.exists(name_temp):
                os.mkdir(name_temp)
            for x in newlist[spl_num_list[i - 1]:spl_num_list[i]]:
                shutil.copy(x, os.path.join(name_temp, x))
        # 划分盲审的
        if  flag:
            t_spl2 = mut_func(t_spl - 1)
            spl_num_list2 = [0]
            mut2 = t_per // t_spl2
            spl_num_list2.extend([mut2] * t_spl2)
            for i in range(t_per % t_spl2):
                spl_num_list2[i + 1] += 1
            for i in range(t_spl2):
                spl_num_list2[i + 1] += spl_num_list2[i]
            # 移动图片
            key = 0
            for k in range(1, t_spl):
                for i in range(t_spl - k):
                    for each in checklist[spl_num_list2[key]:spl_num_list2[key + 1]]:
                        shutil.copy(each, os.path.join(folder_name + '_' + str(i + 1).rjust(len(str(t_spl))), each))
                        shutil.copy(each, os.path.join(folder_name + '_' + str(i + k + 1).rjust(len(str(t_spl))), each))
                    key += 1
            # 写入txt和存入文件夹
            os.mkdir('盲审')
            with open('盲审.txt', 'w') as f:
                for x in checklist:
                    shutil.copy(x, os.path.join('盲审',x))
                    f.write(x + '\n')
        showinfo('提示', '分配完成！')


    #累加
    def mut_func(n):
        return 1 if n == 1 else n + mut_func(n - 1)

    #选择数据并处理
    def choose_data():
        global img_list, t_result, check_all, check_dif
        filepath = askdirectory(initialdir=".", title='Pick a directory')
        os.chdir(filepath)
        if os.path.exists('结果.txt'):
            os.remove('结果.txt')
        if os.path.exists('盲审不一致.txt'):
            os.remove('盲审不一致.txt')
        if os.path.exists('盲审不一致'):
            shutil.rmtree('盲审不一致')
        txtlist = [x for x in os.listdir('.') if x.endswith('.txt')]
        txtlist.remove('盲审.txt')
        with codecs.open('盲审.txt', 'r','utf-8') as f:
            result = [x.rstrip('\n') for x in f.readlines() if x.endswith(('.jpg', '.jpg\n'))]
        data = {}
        for each in txtlist:
            with codecs.open(each, 'r', 'utf-8') as f:
                f.readline()
                temp = [x.rstrip('\n') for x in f.readlines()]
                temp2 = {x.split()[0]: x.split()[1] for x in temp}
                data[each.rstrip('.txt')] = temp2
        for i, each in enumerate(result):
            for x in data:
                if each in data[x]:
                    result[i] += ' ' + x + ':' + trans_list[data[x][each]]
        with codecs.open('结果.txt', 'w', 'utf-8') as f:
            for each in result:
                f.write(each + '\n')
        t_result = []
        for x in result:
            flag = False
            for y in trans_list:
                if 0 < x.count(':' + trans_list[y]) < len(txtlist):
                    flag = True
                    break
            if flag:
                t_result.append(x)
        if len(t_result) > 0:
            if not os.path.exists('盲审不一致'):
                os.mkdir('盲审不一致')
            with codecs.open('盲审不一致.txt', 'w','utf-8') as f:
                for each in t_result:
                    f.write(each + '\n')
                    shutil.copy(os.path.join('盲审', each.split()[0]),os.path.join('盲审不一致', each.split()[0]))
            img_list = [x.split()[0] for x in t_result]
            check_all = result[:]
            show_pic()
            info()

        else:
            showinfo('提示', '没有盲审不一致的图片！')


    def key_call(event):#键盘事件
        #print(event.keycode,event.char,event.keysym)
        temp = event.keycode
        if temp == 37 or event.keysym == 'Left':
            start_thread(pre)
        elif temp == 39 or event.keysym == 'Right':
            start_thread(next)


    # -----------------GUI-------------------------
    root = tk.Tk()
    root.title('人脸关键点盲审工具')
    # 键盘事件
    root.bind_all('<KeyPress-Left>', key_call)
    root.bind_all('<KeyPress-Right>', key_call)
    # 主要面板
    mypw = tk.PanedWindow(showhandle=True, sashrelief=tk.SUNKEN)
    mypw.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)
    # 左侧图片显示
    img_frame = tk.LabelFrame(mypw, text='图片', padx=5, pady=5)
    img_frame.pack(padx=10, pady=10)
    pic_label = tk.Label(img_frame)
    pic_label.pack()
    # 右侧面板
    myframe = tk.LabelFrame(mypw, text='功能', padx=5, pady=5)
    myframe.pack(padx=10, pady=10)
    # 1.分配图片
    split_frame = tk.LabelFrame(myframe, text='1.分配图片', font=24, padx=18, pady=5)
    split_frame.pack(padx=10, pady=10)
    tk.Button(split_frame, text='选择文件夹', command=lambda: start_thread(choose_folder), padx=20, pady=5, font=28, width=10,height=1).grid(row = 0, column = 0, columnspan=2, pady = 5, padx = 10)
    tk.Button(split_frame, text='分配', command=lambda: start_thread(split_img), font=28, padx=20, pady=5, width=10,height=1).grid(row = 4, column = 0, columnspan=2, pady = 5, padx = 10)
    tk.Label(split_frame, text='分配数量：', font=16).grid(row=1, column=0, sticky=tk.W, pady=5)
    tk.Label(split_frame, text='分配份数：', font=16).grid(row=2, column=0, sticky=tk.W, pady=5)
    tk.Label(split_frame, text='盲审数量(或百分比)：', font=16).grid(row=3, column=0, sticky=tk.W, pady=5)

    e_num_all = tk.StringVar()
    num_all = tk.Entry(split_frame,textvariable=e_num_all, justify=tk.CENTER)
    num_all.grid(row=1, column=1)
    e_num_spl = tk.StringVar()
    num_spl = tk.Entry(split_frame,textvariable=e_num_spl, justify=tk.CENTER)
    num_spl.grid(row=2, column=1)
    e_num_per = tk.StringVar()
    num_per = tk.Entry(split_frame,textvariable=e_num_per, justify=tk.CENTER)
    num_per.grid(row=3, column=1)
    # 2.功能
    menu_frame = tk.LabelFrame(myframe, text='3.图片筛选', font=24, padx=5, pady=5)
    menu_frame.pack(padx=10, pady=10)
    btn_choose = tk.Button(menu_frame, text='选择数据文件夹', command=lambda: start_thread(choose_data), font=24, padx=20, pady=5, width=10, height=1)
    btn_choose.grid(row = 0, column = 0, columnspan=2, pady = 5, padx = 10)
    # 跳转
    tk.Label(menu_frame, text='请输入要跳转的页数或文件名：', font=16).grid(row=1, column=0,columnspan=2, sticky=tk.W, pady=5)
    e = tk.StringVar()
    entry = tk.Entry(menu_frame, textvariable=e, font=28, width=10, justify='center')
    e.set(1)
    entry.grid(row=2, column=0)
    tk.Button(menu_frame, text='跳转', command=lambda: start_thread(topic), font=28, padx=20, pady=5, width=10,
              height=1).grid(row=2, column=1, pady = 5, padx = 10)
    # 放大缩小
    tk.Label(menu_frame, text='请输入需要放大缩小的倍数：', font=16).grid(row=3, column=0,columnspan=2, sticky=tk.W, pady=5)
    e2 = tk.StringVar()
    entry2 = tk.Entry(menu_frame, textvariable=e2, font=28, width=10, justify='center')
    e2.set(mut)
    entry2.grid(row=4, column=0)
    tk.Button(menu_frame, text='调整', command=lambda: start_thread(set_mut), font=28, padx=20, pady=5, width=10,
              height=1).grid(row=4, column=1, pady = 5, padx = 10)

    show_num_label = tk.Label(menu_frame, text='信息')
    show_num_label.grid(row=5, column=0, columnspan=2, pady = 5, padx = 10)
    tk.Button(menu_frame, text='上一张', command=lambda: start_thread(pre), font=28, padx=20, pady=5, width=10,
              height=1).grid(row=6, column=0, pady = 5, padx = 10)
    tk.Button(menu_frame, text='下一张', command=lambda: start_thread(next), font=28, padx=20, pady=5, width=10,
              height=1).grid(row=6, column=1 , pady = 5, padx = 10)
    mypw.add(img_frame)
    mypw.add(myframe)
    root.mainloop()

if __name__ == '__main__':
    main()
