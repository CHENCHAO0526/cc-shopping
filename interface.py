import logging
import os
import queue
import threading
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

from consts.consts import *
from log import logger, formatter


# 自定义re_Text, 自定义IO有write方法
class ReText(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, content):
        self.queue.put(content)


'''
1、支持动态地更改抢购的商品；
根据输入的sku_ids更改  done
2、执行的信息放入gui中  done
3、支持同时抢购多个商品组合
'''
#TODO 界面优化
class RushGUI(object):
    def __init__(self, jd_user):
        self.root = Tk()
        self.user_nickname = StringVar()
        self.submit_mode = StringVar()
        self.jd_user = jd_user
        self.root.title("私家车")
        self.root.geometry("%dx%d" % (800, 600))  # 窗体尺寸

        #如果给整个窗口弄滚动条需要建一个大frame
        # scrollBar = Scrollbar(self.root)
        # scrollBar.pack(side=RIGHT, fill=Y)

        self.plan_control = PlanControl(self.root, borderwidth=1, relief="flat")

        self.body()  # 绘制窗体组件
        self.threads = []
        #self.start_rush()
        self.root.mainloop()

    def body(self):
        self.account_rush().pack(side=TOP, expand=False, anchor='w',fill=X)
        # self.account_choose().pack(side=TOP, expand=False, anchor='w')
        # self.rush_control().pack(side=TOP, expand=False, anchor='w')
        self.plan_control.pack(side=TOP, expand=False, anchor='w',fill=X)
        self.log().pack(side=TOP, expand=False, anchor='w',fill=X)

    def account_rush(self):
        account_rush_frame = Frame(self.root, borderwidth=5, relief="flat")
        self.account_choose(account_rush_frame).pack(side=LEFT, expand=False, anchor='w')
        self.presall_choose(account_rush_frame).pack(side=LEFT, expand=False, anchor='w')
        self.rush_control(account_rush_frame).pack(side=RIGHT, expand=False, anchor='e')
        return account_rush_frame


    def account_choose(self,top_frame):
        account_choose_frame = Frame(top_frame, borderwidth=1, relief="groove")
        account_label = Label(account_choose_frame, text="账号:")
        login_button = Button(account_choose_frame, text="登录账号", command=self.login)
        cookie_files = os.listdir(COOKIE_DIR)
        cookie_files = [file for file in cookie_files if file.endswith('.cookie')]
        nicknames = [file.split('.')[0] for file in cookie_files]

        if len(nicknames) > 0:
            self.user_nickname.set(nicknames[0])
        accouts_combobox = ttk.Combobox(
            master=account_choose_frame,  # 父容器
            height=10,  # 高度,下拉显示的条目数量
            width=20,  # 宽度
            state="readonly",  # 设置状态 normal(可选可输入)、readonly(只可选)、 disabled
            cursor="arrow",  # 鼠标移动时样式 arrow, circle, cross, plus...
            #font=("", 20),  # 字体
            textvariable=self.user_nickname,  # 通过StringVar设置可改变的值
            values=nicknames,  # 设置下拉框的选项
        )
        account_label.pack(side=LEFT)
        accouts_combobox.pack(side=LEFT)
        login_button.pack(side=LEFT)
        return account_choose_frame

    def login(self):
        if self.jd_user.get_nickname() == self.user_nickname.get() and self.jd_user.get_login_status():
            logger.info("{}已登录".format(self.user_nickname.get()))
            return
        self.jd_user.login(self.user_nickname.get())

    def presall_choose(self,top_frame):
        presall_choose_frame = Frame(top_frame, borderwidth=1, relief="groove")
        account_label = Label(presall_choose_frame, text="购买模式:")
        login_button = Button(presall_choose_frame, text="改变模式", command=self.set_submit_mode)

        self.submit_mode.set("预售")
        accouts_combobox = ttk.Combobox(
            master=presall_choose_frame,  # 父容器
            height=10,  # 高度,下拉显示的条目数量
            width=20,  # 宽度
            state="readonly",  # 设置状态 normal(可选可输入)、readonly(只可选)、 disabled
            cursor="arrow",  # 鼠标移动时样式 arrow, circle, cross, plus...
            # font=("", 20),  # 字体
            textvariable=self.submit_mode,  # 通过StringVar设置可改变的值
            values=["现货", "预售"],  # 设置下拉框的选项
        )
        account_label.pack(side=LEFT)
        accouts_combobox.pack(side=LEFT)
        login_button.pack(side=LEFT)
        return presall_choose_frame

    def set_submit_mode(self):
        self.jd_user.set_submit_mode(self.submit_mode.get())

    def rush_control(self,top_frame):
        rush_control_frame = Frame(top_frame, borderwidth=1, relief="groove")
        rush_button = Button(rush_control_frame, text='开始rush', command=self.start_rush)
        stop_rush_button = Button(rush_control_frame, text='停止rush', command=self.stop_rush)
        rush_button.pack(side=LEFT)
        stop_rush_button.pack(side=LEFT)
        return rush_control_frame

    def log(self):
        """
        日志输出到GUI上
        :return:
        """
        log_frame = Frame(self.root, borderwidth=1, relief="ridge")
        scroll_bar = Scrollbar(log_frame)
        scroll_bar.pack(side="right", fill="y")
        text = Text(log_frame, yscrollcommand=scroll_bar.set)
        text.pack(side="top", fill=BOTH, padx=10, pady=10)
        scroll_bar.config(command=text.yview)

        # 设置log，将日志也投射到gui的log panel上
        msg_queue = queue.Queue()
        handler = logging.StreamHandler(ReText(msg_queue))
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # 在show_msg方法里，从Queue取出元素，输出到Text
        def show_msg():
            while not msg_queue.empty():
                content = msg_queue.get()
                text.insert(INSERT, content)
                text.see(END)
            text.after(100, show_msg)
        text.after(100, show_msg)

        return log_frame

    def start_rush(self):
        self.stop_rush()
        self.jd_user.set_rushing(True)
        self.set_buy_plan()
        t = threading.Thread(target=self.jd_user.buy_item_in_stock)
        t.start()

   #停止可能存在的抢购线程
    def stop_rush(self):
        self.jd_user.set_rushing(False)
        if len(self.threads) == 0:
            return
        self.threads[0].join()


    def set_buy_plan(self):
        buy_plans = self.plan_control.get_buy_plans()
        # gui设置的plan为空，使用config中的设置
        if buy_plans == []:
            return
        # 暂时只考虑一个plan
        self.jd_user.set_sku_ids(buy_plans[0])


class PlanControl(Frame):
    def __init__(self, master=None, cnf={}, **kw):
        super(PlanControl, self).__init__(master=master, cnf=cnf, **kw)
        self.add_plan_button = Button(self, text='增加plan', command=self.add_plan)
        self.head_frame = Frame(self, borderwidth=3, relief="groove")
        self.plan_frames = PlanFrames(self, borderwidth=3)

        self.init_body()

    def init_body(self):

        self.init_head()
        self.add_plan_button.pack(side=LEFT, expand=False, anchor=N)
        # self.head_frame.pack(side=TOP, expand=False, anchor=CENTER)
        self.plan_frames.pack(side=RIGHT, expand=False, anchor=CENTER)

    def init_head(self):
        plan_label = Label(self.head_frame, text="plan", borderwidth=3, relief="sunken")
        sku_id_label = Label(self.head_frame, text="sku_id", borderwidth=3, relief="sunken")
        quality_label = Label(self.head_frame, text="数量", borderwidth=3, relief="sunken")

        plan_label.pack(side=LEFT, expand=False, anchor=N)
        sku_id_label.pack(side=LEFT, expand=False, anchor=N)
        quality_label.pack(side=LEFT, expand=False, anchor=N)

    def add_plan(self):
        self.plan_frames.add_plan()

    def get_buy_plans(self):
        return self.plan_frames.get_buy_plans()

class PlanFrames(Frame):
    def __init__(self, master=None, cnf={}, **kw):
        super(PlanFrames, self).__init__(master=master, cnf=cnf, **kw)
        self.plan_count = 0
        self.plan_frames = {}

        self.init_body()

    def init_body(self):
        self.add_plan()

    def add_plan(self):
        self.plan_frames[self.plan_count] = PlanFrame(self, plan_index=self.plan_count, borderwidth=3, relief="groove")
        self.plan_frames[self.plan_count].pack(side=TOP, expand=False, anchor='center')
        self.plan_count += 1

    def remove_plan(self, plan_index):
        if len(self.plan_frames) == 1:
            showinfo(message="plan数量至少为1")
            return False
        del self.plan_frames[plan_index]
        return True

    def get_buy_plans(self):
        buy_plans = []
        for _, plan_frame in self.plan_frames.items():
            buy_plan = plan_frame.get_buy_plan()
            if buy_plan == {}:
                continue
            buy_plans.append(plan_frame.get_buy_plan())
        return buy_plans


class PlanFrame(Frame):
    def __init__(self, master=None, plan_index=-1, cnf={}, **kw):
        super(PlanFrame, self).__init__(master=master, cnf=cnf, **kw)
        assert plan_index != -1
        self.plan_index = plan_index
        self.plan_label = Label(self, text="plan {}".format(plan_index))
        self.sku_frames = SkuFrames(self, borderwidth=3, relief="flat")
        self.add_sku_button = Button(self, text='增加商品', command=self.add_sku)
        self.remove_plan_button = Button(self, text='移除plan', command=self.remove_plan)

        self.init_body()

    def init_body(self):
        self.plan_label.pack(side=LEFT, expand=False, anchor=CENTER)
        self.sku_frames.pack(side=LEFT, expand=False, anchor=CENTER)
        self.add_sku_button.pack(side=LEFT, expand=False, anchor=N)
        self.remove_plan_button.pack(side=LEFT, expand=False, anchor=N)

    def add_sku(self):
        self.sku_frames.add_sku()

    def remove_plan(self):
        if not self.master.remove_plan(self.plan_index):
            return
        self.destroy()

    def get_buy_plan(self):
        """
        获取每个商品及对应的数量
        :return:
        """
        return self.sku_frames.get_buy_plan()

class SkuFrames(Frame):
    def __init__(self, master=None, cnf={}, **kw):
        super(SkuFrames, self).__init__(master=master, cnf=cnf, **kw)
        self.sku_count = 0
        self.sku_frames = {}
        self.init_body()

    def init_body(self):
        self.add_sku()

    def add_sku(self):
        self.sku_frames[self.sku_count] = SkuFrame(self, sku_index=self.sku_count, borderwidth=3, relief="flat")
        self.sku_frames[self.sku_count].pack(side=TOP, expand=False, anchor='center')
        self.sku_count += 1

    def remove_sku(self, count):
        if len(self.sku_frames) == 1:
            showinfo(message="sku数量至少为1")
            return False
        del self.sku_frames[count]
        return True

    def get_buy_plan(self):
        buy_plan = {}
        for _, sku_item in self.sku_frames.items():
            if sku_item.get_sku_id() == "":
                continue
            buy_plan[sku_item.get_sku_id()] = sku_item.get_quality() if sku_item.get_quality() else '1'
        return buy_plan


class SkuFrame(Frame):
    def __init__(self, master=None, sku_index=-1, cnf={}, **kw):
        super(SkuFrame, self).__init__(master=master, cnf=cnf, **kw)
        assert sku_index != -1
        self.index_by_father = sku_index
        # StringVar整个tk下根据name确定，利用内存地址保证基本的唯一性，有小概率出问题
        self.sku_id = StringVar(master=self, name="sku_ids_{}".format(id(self)))
        self.quality = StringVar(master=self, name="quality_{}".format(id(self)))
        self.sku_id_label_entry = Entry(self, textvariable=self.sku_id)
        self.sku_id_count_entry = Entry(self, textvariable=self.quality)
        self.remove_sku_button = Button(self, text='-', command=self.remove)
        self.init_body()

    def init_body(self):
        self.sku_id_label_entry.pack(side=LEFT, expand=False, anchor=N)
        self.sku_id_count_entry.pack(side=LEFT, expand=False, anchor=N)
        self.remove_sku_button.pack(side=LEFT, expand=False, anchor=N)

    def remove(self):
        if not self.master.remove_sku(self.index_by_father):
            return
        self.destroy()

    def get_sku_id(self):
        return self.sku_id.get()

    def get_quality(self):
        return self.quality.get()


if __name__ == '__main__':
    RushGUI()
    