from tkinter import *
from PIL import ImageTk, Image
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import os
from tkinter import ttk
from datetime import date, datetime


class Database:
    def __init__(self):
        """
        Initialize database and cursor
        """
        self.file = 'expense.db'
        os.remove(os.getcwd() + '/' + self.file)
        self.connection = sqlite3.connect(self.file)
        self.cursor = self.connection.cursor()

    def create_table(self):
        """
        Create database
        """
        self.cursor.execute(""" CREATE TABLE expenses (
                    amount real,
                    type text,
                    message text,
                    date text
                    ) """)

        self.connection.commit()

    def add_expense(self, amount, type, message, date):
        """
        Add expense to database
        :param amount: Expense amount
        :param type: Expense type
        :param message: Expense message
        :param date: Expense date
        """
        self.cursor.execute("INSERT INTO expenses (amount, type, message, date) VALUES (?, ?, ?, ?)",
                            (amount, type, message, date))
        self.connection.commit()

    def get_single_type(self, type):
        """
        Get expense data from a single expense type
        :param type:
        :return:
        """
        self.cursor.execute("SELECT * FROM expenses WHERE type = " + str(type))
        out_type = self.cursor.fetchone()
        return out_type

    def get_types(self):
        """
        Get all expense types
        :return: numpy array of expense type strings
        """
        self.cursor.execute("SELECT DISTINCT type FROM expenses")
        all_types = self.cursor.fetchall()
        types = np.empty(0)
        for unique_type in all_types:
            types = np.append(types, unique_type[0])
        return types

    def get_amount(self, type):
        """
        Get spent amount per expense type
        :param type: Expense type
        :return: Integer amount
        """
        self.cursor.execute("SELECT amount FROM expenses WHERE type =?", (type,))
        amount = self.cursor.fetchall()
        total = []
        for a in amount:
            b, = a
            total.append(b)
        total_amount = sum(total)
        return total_amount

    def get_dates(self):
        """
        Get all dates of expenses
        :return: all dates
        """
        self.cursor.execute("SELECT date FROM expenses")
        all_dates = self.cursor.fetchall()
        int_dates = []
        for a in all_dates:
            b, = a
            int_dates.append(b)
        return int_dates

    def get_maxdate(self):
        """
        Get maximum date of expenses
        :return: string of maximum date
        """
        dates = self.get_dates()
        max_date = max(dates, key=lambda d: datetime.strptime(d, '%Y,%m,%d'))
        max_date = max_date.replace(",", "-")
        return max_date

    def get_mindate(self):
        """
        Get minimum date of expenses
        :return: string of minimum date
        """
        dates = self.get_dates()
        min_date = min(dates, key=lambda d: datetime.strptime(d, '%Y,%m,%d'))
        min_date = min_date.replace(",", "-")
        return min_date

    def get_latest_messages(self, type):
        """
        Get latest 2 messages per expense type
        :param type: Expense type
        :return: Array of 2 string
        """
        self.cursor.execute("SELECT message FROM expenses WHERE type =?", (type,))
        all_messages = self.cursor.fetchall()
        latest_messages = all_messages[-2:]
        messages = []
        for message in latest_messages:
            a, = message
            messages.append(a)
        return messages


class Application:
    def __init__(self):
        """
        Initialize database and screen with buttons and entry fields
        """
        # initialise Database
        self.database = Database()
        self.database.create_table()

        # initialise first window
        self.master = Tk()
        self.master.geometry("600x300")
        self.master.title("Expense tracker")

        self.canv = Canvas(self.master, relief='raised', borderwidth=2)
        self.canv.pack(fill=BOTH, expand=1)

        self.spent = 0.0

        self.background_image = Image.open('Grey-Gradient-Background.jpg')
        self.background_image_copy = self.background_image.copy()
        self.img = ImageTk.PhotoImage(self.background_image.resize((600, 300)))
        self.canvas_img = self.canv.create_image(0, 0, image=self.img, anchor=NW)
        self.canv.bind('<Configure>', self.resize_image)

        self.canv.create_text(8, 8, anchor="nw", text="Add expense" )
        self.canv.create_text(85, 35, anchor="nw", text="Amount" )
        self.canv.create_text(85, 65, anchor="nw", text="Type" )
        self.canv.create_text(85, 95, anchor="nw", text="Message" )
        self.canv.create_text(85, 125, anchor="nw", text="Date" )

        self.amount_txt = Entry(self.master, width=10)
        self.amount_txt.place(x=150, y=30, anchor=NW)

        self.expense_type_txt = Entry(self.master, width=10)
        self.expense_type_txt.place(x=150, y=60, anchor=NW)

        self.message_txt = Entry(self.master, width=10)
        self.message_txt.place(x=150, y=90)

        self.current_expense = Label(self.master, text="Spent " + str(self.spent), relief='raised',borderwidth=4)
        self.current_expense.place(x=8, y=200, anchor=NW)

        add_button = Button(self.master, text="Add", command= self.clicked)
        add_button.place(x=150, y=160)

        btn = Button(self.master, text="Done", command=self.quit)
        btn.place(x=500, y=160)
        self.date_picker()

        self.master.mainloop()

    def resize_image(self, event):
        """
        Resize background image if screen is resized
        """
        new_width = event.width
        new_height = event.height
        self.img2 = ImageTk.PhotoImage(self.background_image_copy.resize((new_width, new_height)))
        self.canv.itemconfig(self.canvas_img, image=self.img2, anchor=NW)

    def date_picker(self):
        """
        Create date picker
        """
        days = list(range(1,32))
        self.months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        years = list(range(2000,2031))

        today = date.today()
        d1 = today.strftime("%B,%d,%Y").split(",")

        self.day = ttk.Combobox(self.canv, values=days, width=9)
        self.day.current(days.index(int(d1[1])))
        self.day.place(x=150, y=120)
        self.month = ttk.Combobox(self.canv, values=self.months, width=9)
        self.month.current(self.months.index(d1[0]))
        self.month.place(x=250, y=120)
        self.year = ttk.Combobox(self.canv, values=years, width=9)
        self.year.current(years.index(int(d1[2])))
        self.year.place(x=350, y=120)

    def clicked(self):
        """
        Add expense information to database and update spent amount
        """
        # Get date
        month_nr = self.months.index(str(self.month.get())) + 1
        expense_date = ",".join([str(self.year.get()), str(month_nr), str(self.day.get())])
        # Add expense to database
        self.database.add_expense(self.amount_txt.get(), self.expense_type_txt.get(), self.message_txt.get(), expense_date)
        # calculate cumulative expenses
        self.spent += float(self.amount_txt.get())
        self.current_expense.configure(text="Spent €" + '{:.2f}'.format(self.spent))

    def quit(self):
        """
        Continue to next screen
        """
        self.master.destroy()
        self.analysis_screen()

    def analysis_screen(self):
        """
        Analysis of expenses. Plot pie and bar chart
        """
        self.master = Tk()
        self.master.title("Analysis")

        # Pie chart
        labels = self.database.get_types()
        sizes = np.empty(0)
        for i in range(len(labels)):
            sizes = np.append(sizes, self.database.get_amount(labels[i]))

        self.sorted_sizes = sizes[np.argsort(sizes)]
        self.sorted_labels = labels[np.argsort(sizes)]

        # define gradient colors
        base = ['#0D6E1F', '#358644', '#5D9E69', '#86B68F', '#AECEB4', '#D6E6D9', '#F0F1EE']
        colors = base[0:len(labels)][::-1]
        inv_colors = colors[::-1]

        # define figure and plot
        self.fig = Figure(figsize=(6, 10))
        self.a = self.fig.add_subplot(211)
        self.patches, texts, autotexts = self.a.pie(self.sorted_sizes, colors=colors, autopct='%1.1f%%',
                                    startangle=90, pctdistance=1.2)

        # draw centre circle
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        self.a.add_artist(centre_circle)

        # centre text
        kwargs = dict(size=10, va='center')
        kwargs2 = dict(size=15, fontweight='bold', va='center')
        kwargs3 = dict(size=8, va='center')
        self.a.text(0, 0.23, 'Expenses', ha = 'center', **kwargs)
        self.a.text(0, 0.03, '\n€{:.2f}'.format(self.spent), ha='center', **kwargs2)
        self.a.text(0, -0.25, '{} - {}'.format(self.database.get_mindate(), self.database.get_maxdate()), ha='center', **kwargs3)

        # Equal aspect ratio ensures that pie is drawn as a circle
        self.a.axis('equal')
        # a.set_title()
        self.a.legend(self.patches[::-1], self.sorted_labels[::-1], loc='upper left', bbox_to_anchor = [-0.1, 1.2])

        # annotations
        self.annot = self.a.annotate("", xy=(0, 0), xytext=(-20, 20), xycoords="polar", textcoords="offset points",
                                     bbox=dict(boxstyle="round", fc="white", ec="black", lw=2),
                                     arrowprops=dict(arrowstyle="wedge"))
        self.annot.set_visible(False)

        # ----------------------------------------------------

        # second plot
        x = range(len(sizes))
        b = self.fig.add_subplot(212)
        b.bar(x, self.sorted_sizes[::-1], color=inv_colors, tick_label=self.sorted_labels[::-1])

        # make pretty
        b.set_ylabel('Spent amount (€)')
        b.set_xlabel('Expense type')
        b.spines['top'].set_visible(False)
        b.spines['right'].set_visible(False)

        canvas = FigureCanvasTkAgg(self.fig, self.master)
        canvas.get_tk_widget().pack()

        canvas.mpl_connect("motion_notify_event", self.hover)

        canvas.draw()

    def update_annot(self, patch, ind):
        """
        Updating annotation box with last 2 messages
        :param patch: Wedge that mouse hovers over
        :param ind: indix of wedge in labels
        """
        theta = patch.theta1
        r = 0.5
        self.annot.xy = (theta, r)
        latest = self.database.get_latest_messages(self.sorted_labels[ind])
        amount = self.sorted_sizes[ind]
        if len(latest) == 1:
            my_message = ("Amount: €" + str(amount) + "\n " + "\n " + latest[0])
        elif len(latest) == 2:
            my_message = ("Amount: €" + str(amount) + "\n " + "\n" + latest[0] + "\n" + latest[1])
        self.annot.set_text(my_message)
        self.annot.get_bbox_patch().set_alpha(1)

    def hover(self, event):
        """
        Find out if mouse hovers over wedge of pie chart,
        if so display spent amount and messages for that wedge
        """
        vis = self.annot.get_visible()
        i = 0
        if event.inaxes == self.a:
            for patch in self.patches:
                cont, ind = patch.contains(event)
                if cont:
                    self.update_annot(patch, i)
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    i += 1
                    return
                i += 1
        if vis:
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()


my_gui = Application()