import customtkinter
from tkinter import ttk

# Custom Tkinter Setup
customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class GuiPart(customtkinter.CTk):

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("GVS AI V1_0")

        # Configure Window Size
        self.windowx = 1915
        self.windowy = 1015
        self.master.geometry(f"{self.windowx}x{self.windowy}+0+0")
        self.master.resizable(width=False, height=False)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure Left Side Bar Frame
        self.frame = customtkinter.CTkFrame(master=self.master, width=200, height=100, corner_radius=0)
        self.frame.grid(row=0, column=0)

        # Left Side Bar --> Title
        title = customtkinter.CTkLabel(master=self.frame, text="GVS AI V1_1",
                                       font=customtkinter.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=10)

        # Left Side Bar --> View
        title = customtkinter.CTkLabel(master=self.frame, text="View:", font=customtkinter.CTkFont(size=14))
        title.grid(row=1, column=0, padx=20, pady=5)

        # Left Side Bar --> main
        button1 = customtkinter.CTkButton(master=self.frame, text="Main", command=self.open_main)
        button1.grid(row=2, column=0, padx=40, pady=10)

        # Left Side Bar --> Setup Exit Button
        console = customtkinter.CTkButton(master=self.frame, text='Exit', command=self.button_event)
        console.grid(row=10, column=0, padx=40, pady=10)

        # UI Button And Object Functions
        self.framePosX = 220
        self.framePosY = 0
        self.frameSizeW = 1695 # Width & Height Of All Main Windows
        self.frameSizeH = 1015

        # Open Main window to start
        self.activeWindow = 0
        self.open_main()
        self.activeWindow = 2

    def button_event(self):
        print("button pressed")

    def open_main(self):
        self.closeWindows()
        self.activeWindow = 2

        # Configure Main Viewing Frame
        self.frame2 = customtkinter.CTkFrame(master=self.master, width=self.frameSizeW, height=self.frameSizeH, corner_radius=0, fg_color="transparent")
        self.frame2.place(x=self.framePosX, y=self.framePosY)

        # Main Viewing Frame --> Title
        title = customtkinter.CTkLabel(master=self.frame2, text="Main Frame", font=customtkinter.CTkFont(size=20, weight="bold"))
        title.place(x=self.frameSizeW/2, y=20, anchor='center')

        # Need To Grab Table Name --> Column Names --> Data

        # Setup Scrollable Frame Window
        self.tree_frame = customtkinter.CTkFrame(master=self.frame2)
        self.tree_frame.place(x=self.frameSizeW/2, y=40, anchor='n', height=500, width=500)

        tree_scrollY = ttk.Scrollbar(self.tree_frame, orient='vertical')
        tree_scrollY.pack(side='right', fill='y')
        tree_scrollX = ttk.Scrollbar(self.tree_frame, orient='horizontal')
        tree_scrollX.pack(side='bottom', fill='x')

        # Setup Tree View selectmode="" prevents selecting item
        self.my_tree = ttk.Treeview(master=self.tree_frame, height=45, yscrollcommand=tree_scrollY.set, xscrollcommand=tree_scrollX.set, selectmode="none")

        # Configure the scrollbar
        tree_scrollY.configure(command=self.my_tree.yview)
        tree_scrollX.configure(command=self.my_tree.xview)

        # Define Our Columns
        self.my_tree['columns'] = ("Name", "ID", "Favourite Pizza","Name", "ID", "Favourite Pizza","Name", "ID", "Favourite Pizza","Name", "ID", "Favourite Pizza")
        # Format Our Columns
        self.my_tree.column("#0", width=0, minwidth=0, stretch='NO')
        self.my_tree.column("Name", anchor='w', width=120, minwidth=25)
        self.my_tree.column("ID", anchor='center', width=120, minwidth=25)
        self.my_tree.column("Favourite Pizza", anchor='w', width=120, minwidth=25)
        # Create Headings
        self.my_tree.heading("#0", text="", anchor='w')
        self.my_tree.heading("Name", text="Name", anchor='w')
        self.my_tree.heading("ID", text="ID", anchor='center')
        self.my_tree.heading("Favourite Pizza", text="Favourite Pizza", anchor='w')
        self.my_tree.pack()
        # Alternating Line Colour
        self.my_tree.tag_configure('oddrow', background="grey")
        self.my_tree.tag_configure('evenrow', background="lightblue")
        data = [
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
            ["hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni","hn", 1, "Pepperoni"],
        ]
        # Insert Data Into Treeview with For Loop
        count = 0
        for record in data:
            if count % 2 == 0:  # If we divide count by 2 and the remainder is 0 (even Row)
                self.my_tree.insert(parent='', index='end', iid=count, text="", values=record, tags=('evenrow',))
            else:
                self.my_tree.insert(parent='', index='end', iid=count, text="", values=record, tags=('oddrow',))
            # values could also = (record[0],record[1],record[2])
            count += 1

    def closeWindows(self):
        # Close All Frames Before Opening New Frame
        if self.activeWindow == 2:
            self.frame2.destroy()
        elif self.activeWindow == 3:
            self.frame3.destroy()
        elif self.activeWindow == 4:
            self.frame4.destroy()
        elif self.activeWindow == 5:
            self.frame5.destroy()
        elif self.activeWindow == 6:
            self.frame6.destroy()
        elif self.activeWindow == 7:
            self.frame7.destroy()


    def close(self):
        self.master.quit()


class ThreadedClient:
    def __init__(self, master):
        self.master = master

        self.gui = GuiPart(master)



if __name__ == '__main__':

    #try:
    root = customtkinter.CTk()
    client = ThreadedClient(root)
    root.mainloop()