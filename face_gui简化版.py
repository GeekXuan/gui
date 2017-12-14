#coding:utf-8
#需要安装pillow库 ~$pip3 install pillow
#Edit by:王智轩
#版本：第四版
import tkinter as tk
from tkinter.filedialog import askdirectory,askopenfilename,asksaveasfilename
from tkinter.messagebox import showinfo,askyesno
from PIL import Image,ImageTk
import threading,time,os,shutil,codecs
#----------------全局变量-------------------
img_list = []
state_list = []
btn_list = ['待定', '合格', '不合格']
number = 0
part = 0
filepath = ''
my_width = 0
my_height = 0
mut = 0.8     #放大倍数
#读写txt
read_folder_path = '-1'
read_txt_path = '-1'
write_folder_path ='-1'

def main():
    #-----------------func------------------------
    def read_btn():#读取自定义按钮
        global btn_list
        if os.path.exists('btn.txt'):
            with codecs.open('btn.txt', 'r', 'utf-8') as f:
                btn_list = [i.strip() for i in f.readlines() if i.strip() != '']

    def start_thread(func, *myargs):#开启多线程
        t = threading.Thread(target = func, args = myargs)
        t.start()
        #t.join()

    def log(mylog = ''):
        with codecs.open(os.path.join(filepath,'log.txt'), 'a', 'utf-8') as f:
            f.write(time_now() + ':' + mylog + '\r\n')

    def time_now():#用于获得当前时间
        return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    def write_data():#存储信息
        with codecs.open('data.txt', 'w', 'utf-8') as f:
            f.write(str(number) + '\r\n')
            for i in range(len(img_list)):
                f.write(img_list[i] + ' ' + str(state_list[i]) + '\r\n')


    def img_split(index = 0):#分割图片
        os.chdir(filepath)
        try:
            img_temp = Image.open(img_list[number])#.convert('RGB')
            x, y = img_temp.size
            img_temp.save(os.path.join('results','temp','im0.jpg'), 'JPEG')
            img_temp.crop((0, 0, x / 3, y / 2)).save(os.path.join('results','temp','im1.jpg'))
            img_temp.crop((x / 3, 0, x , y/2)).save(os.path.join('results','temp','im2.jpg'))
            img_temp.crop((0, y / 2, x / 3, y)).save(os.path.join('results','temp','im3.jpg'))
            img_temp.crop((x / 3, y / 2, x / 3 * 2, y)).save(os.path.join('results','temp','im4.jpg'))
            img_temp.crop((x / 3 * 2, y / 2, x, y)).save(os.path.join('results','temp','im5.jpg'))
            img_temp.close()
        except OSError:
            print('无法读取' + img_list[number])
            log('无法读取' + img_list[number])
            shutil.copy(os.path.join(filepath, img_list[number]), os.path.join(filepath, 'results', '不支持的文件'))
            state_list[number] = 404
            if index:
                pre()
            else:
                next()

    def show_new_pic():#显示图片
        global my_height, my_width
        filename = os.path.join(filepath,'results','temp','im' + str(part) + '.jpg')
        #w_s, h_s = get_screen_size(root)
        #w_s -= 200
        im = Image.open(filename)
        w, h = im.size
        my_width = w
        my_height = h
        if part >= 0:
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
            img_split(1)
            show_new_pic()
            prograss()
        write_data()
        e1.set(number)
        log('点击了上一页，现在在第%d页' % (number + 1))


    def next():#下一页
        global number
        if number == len(img_list) - 1:
            showinfo('提示', '当前已经是最后一张！')
        else:
            number += 1
            img_split()
            show_new_pic()
            prograss()
        write_data()
        e1.set(number)
        log('点击了下一页，现在在第%d页' % (number + 1))

    def topic():#跳转
        global number
        pagenum = e1.get()
        if pagenum.isdigit() and 0 < int(pagenum) <= len(img_list):
            number = int(pagenum) - 1
            img_split()
            show_new_pic()
            prograss()
        elif pagenum in img_list:
            number = img_list.index(pagenum)
            img_split()
            show_new_pic()
            prograss()
        elif pagenum+'.jpg' in img_list:
            number = img_list.index(pagenum+'.jpg')
            img_split()
            show_new_pic()
            prograss()
        else:
            showinfo('提示', '请输入正确的页数或文件名！')
        write_data()
        log('跳转到第%d页' % (number + 1))

    #调整大小
    def  set_mut():
        global mut
        mutt = e2.get()
        try:
            mut = float(mutt)
            img_split()
            show_new_pic()
        except:
            showinfo('提示', '请输入正确的倍数！')
        log('调整为%f倍' % (mut))


    def btn_click(index):#标记
        global number, state_list
        if number == len(img_list) - 1:
            showinfo('提示', '当前已经是最后一张！')
        remark()
        shutil.copy(os.path.join(filepath, img_list[number]), os.path.join(filepath, 'results', btn_list[index-1]))
        state_list[number] = index
        if number < len(img_list) - 1:
            number += 1
            img_split()
            show_new_pic()
        prograss()
        write_data()
        e1.set(number)
        log('将第%d张%s标记为%s' % (number, img_list[number - 1], btn_list[index - 1]))

    def remark():#修改前删除原来标记的文件
        if state_list[number] > 0:
            path_temp = filepath + '/results/' +  btn_list[state_list[number]-1]
            os.remove(path_temp+'/' + img_list[number])
            log('将%s移出%s文件夹'%(img_list[number], btn_list[state_list[number]-1]))

    def prograss():#进度
        global img_list,number,state_list
        str_temp1 = '文件：' + img_list[number] + '\n大小：%d x %d\n' % (my_width,my_height)
        str_temp2 = '上次标记为：' + ('未标记' if state_list[number] == 0 else btn_list[state_list[number]-1]) + '\n'
        str_temp3 = '第' + str(number + 1) + '/' + str(len(img_list)) + '张； 进度：%.2f' % ((len(state_list)- state_list.count(0))/len(state_list) * 100) + '%\n'
        str_temp4 = ''
        for i,x in enumerate(btn_list):
            try:
                str_temp4 += x + '个数：' + str(state_list.count(i+1)) + ';  占比：%.2f' % (state_list.count(i+1)/(len(state_list) - state_list.count(0) - state_list.count(404)) * 100) + '%\n'
            except:
                str_temp4 += x + '个数：' + str(state_list.count(i+1)) + ';  占比：0.00%\n'
        str_temp5 = '无法读取的个数：' + str(state_list.count(404))
        show_num_label['text'] = str_temp1 + str_temp2 + str_temp3 + str_temp4 + str_temp5
        show_num_label.text = str_temp1 + str_temp2 + str_temp3 + str_temp4 + str_temp5

    def quit_callback():#退出
        global number,img_list,filepath,state_list
        ans = askyesno('提示', '将把未标记的图片移入“未处理”文件夹下，\n继续吗?')
        log('做到第%d张%s\n' % (number, img_list[number - 1]))
        if ans:
            os.mkdir(os.path.join(filepath, '未处理'))
            for each in img_list[number:]:
                if state_list[number] == 0:
                    shutil.move(os.path.join(filepath, each), os.path.join(filepath, '未处理', each))
            root.destroy()

    def part_callback(i = 6):#选择显示的图片部分
        global part
        part = i
        show_new_pic()

    def prepare():#读取文件夹
        global img_list,filepath,state_list
        filepath = askdirectory(initialdir="/",title='Pick a directory')
        os.chdir(filepath)
        t, r = check_data()
        if not r:
            name_old = 'results_'+time_now().replace(':','-')
            os.rename('results', name_old)
            os.mkdir('results')
        if not os.path.exists('results'):
            os.mkdir('results')
        os.chdir('results')
        temp = ['不支持的文件', 'temp']
        for x in temp:
            if not os.path.exists(x):
                os.mkdir(x)
        for x in btn_list:
            if not os.path.exists(x):
                os.mkdir(x)
        img_list = [x for x in os.listdir('..') if x.lower().endswith(('.jpg','.jpeg','.png'))]
        if t:
            state_list = [0 for i in range(len(img_list))]
        img_split()
        show_new_pic()
        prograss()

    def key_call(event):
       #print(event.keycode,event.char,event.keysym)
        temp = event.keycode
        if temp == 37:
            start_thread(pre)
        elif temp == 39:
            start_thread(next)
        elif temp == 32:
            start_thread(lambda :btn_click(2))

    def check_data():#检查上次保存的信息
        global state_list, number
        t = 1
        if os.path.exists('data.txt'):
            t = askyesno('提示', '发现之前的记录，是否读取并继续？')
            if t:
                with codecs.open('data.txt', 'r', 'utf-8') as f:
                    temp = f.readlines()
                    number = int(temp[0].strip())
                    state_list = [int(i.split()[1].strip()) for i in temp[1:]]
                return (0, t)
        return (1, t)

    #-----------------GUI-------------------------
    read_btn()
    root = tk.Tk()
    root.title('人脸关键点审核工具')
    #键盘事件
    root.bind_all('<KeyPress-Left>', key_call)
    root.bind_all('<KeyPress-Right>', key_call)
    root.bind_all('<KeyPress-space>', key_call)
    #root.bind_all('<Key>', key_call)
    #面板
    mypw = tk.PanedWindow(showhandle = True, sashrelief = tk.SUNKEN)
    mypw.pack(fill = tk.BOTH, expand = 1, padx = 10, pady = 10)
    #左侧图片显示
    img_frame = tk.LabelFrame(mypw, text = '图片', padx = 5, pady = 5)
    img_frame.pack(padx = 10, pady = 10)
    pic_label = tk.Label(img_frame)
    pic_label.pack()
    #右侧面板
    myframe = tk.LabelFrame(mypw, text = '功能', padx = 5, pady = 5)
    myframe.pack(padx=10, pady=10)
    #图片筛选
    menu_frame = tk.LabelFrame(myframe, text = '图片筛选', font = 24, padx = 5, pady = 5)
    menu_frame.pack(padx = 10, pady = 10)
    btn_choose = tk.Button(menu_frame, text='选择文件夹', command = lambda : start_thread(prepare), font=24, padx=20, pady=5, width=10,height=1)
    btn_choose.pack()
    v = tk.IntVar()
    my_rb_00 = tk.Radiobutton(menu_frame, text='原图', variable=v, value=0, indicatoron=True, width=18, height=1, command=lambda: part_callback(0))
    my_rb_00.select()
    my_rb_00.pack()
    #tk.Button(menu_frame, text='旋转', command=lambda: start_thread(my_rotate), font=28, padx=20, pady=5, width=10,height=1).pack()
    #跳转
    e1 = tk.StringVar()
    entry = tk.Entry(menu_frame, textvariable=e1, font=28, width=10, justify = 'center')
    e1.set(1)
    entry.pack()
    tk.Button(menu_frame, text='跳转', command=lambda: start_thread(topic), font=28, padx=20, pady=5, width=10, height=1).pack()
    #放大缩小
    e2 = tk.StringVar()
    entry2 = tk.Entry(menu_frame, textvariable=e2, font=28, width=10, justify='center')
    e2.set(mut)
    entry2.pack()
    tk.Button(menu_frame, text = '调整', command = lambda : start_thread(set_mut), font=28, padx=20, pady=5, width=10,height=1).pack()
    #tk.Button(menu_frame, text = '最后一张', command = lambda : start_thread(lastpic), font=28, padx=20, pady=5, width=10,height=1).pack()
    tk.Button(menu_frame, text = '上一张', command = lambda : start_thread(pre), font=28, padx=20, pady=5, width=10,height=1).pack()
    tk.Button(menu_frame, text='下一张', command=lambda: start_thread(next), font=28, padx=20, pady=5, width=10,height=1).pack()

    show_num_label = tk.Label(menu_frame, text = '信息')
    show_num_label.pack()
    for i,x in enumerate(btn_list):
        tk.Button(menu_frame, text = x, command=lambda i = i + 1:start_thread(btn_click,i), font=28, padx=20, pady=5, width=10,height=1).pack()
    btn_quit = tk.Button(menu_frame, text='退出', command=lambda: start_thread(quit_callback), font=24, padx=20, pady=5, width=10,height=1)
    btn_quit.pack()

    mypw.add(img_frame)
    mypw.add(myframe)

    root.mainloop()


if __name__ == '__main__':
    main()
