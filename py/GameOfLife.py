from threading import BrokenBarrierError, Barrier, Thread
from tkinter import *
import platform
import time
import copy

class GameOfLife:

    def __init__(self):
        self.root = Tk()
        self.root.title("Game of Life")
        
        slash = "\\" if platform.system() == "Windows" else "/"
        self.root.iconbitmap(f".{slash}imgs{slash}icon.ico")
        self.root.minsize(500, 500)
        self.root.geometry("")
        
        self.up_frame = Frame(self.root)
        self.up_frame.grid(row = 0, column = 0)
        
        self.width_entry = Entry(self.up_frame)
        self.width_entry.insert(0, "Width")
        self.width_entry.bind("<Button-1>", self.__width_focus_in)
        self.width_entry.bind("<FocusOut>", self.__width_focus_out)
        self.width_entry.grid(column = 0, row = 0)
        
        self.height_entry = Entry(self.up_frame)
        self.height_entry.insert(0, "Height")
        self.height_entry.bind("<Button-1>", self.__height_focus_in)
        self.height_entry.bind("<FocusOut>", self.__height_focus_out)
        self.height_entry.grid(column = 1, row = 0)
        
        self.sleep_entry = Entry(self.up_frame)
        self.sleep_entry.insert(0, "Sleep Time (seconds)")
        self.sleep_entry.bind("<Button-1>", self.__sleep_focus_in)
        self.sleep_entry.bind("<FocusOut>", self.__sleep_focus_out)
        self.sleep_entry.grid(column = 2, row = 0)
        
        self.update_settings_button = Button(self.up_frame, text = "UPDATE SETTINGS", command = self.__update_settings)
        self.update_settings_button.grid(column = 3, row = 0)
        
        self.status_label = Label(self.up_frame, text = "")
        self.status_label.grid(column = 0, row = 1)
        
        self.mid_frame = Frame(self.root)
        self.mid_frame.grid(row = 1, column = 0)
        
        self.modes = ("Sequential", "Multi-Threaded")
        self.variable = StringVar()
        self.variable.set(self.modes[0])
        self.mode_menu = OptionMenu(self.mid_frame, self.variable, *self.modes, command = self.__change_mode)
        self.mode_menu.grid(column = 0, row = 0)
        
        self.start_button = Button(self.mid_frame, text = "START", command = self.__start_game)
        self.start_button.grid(column = 1, row = 0)
        
        self.stop_button = Button(self.mid_frame, text = "STOP", command = self.__stop_game)
        self.stop_button.grid(column = 2, row = 0)
        
        self.game_grid_frame = Frame(self.root)
        self.game_grid_frame.grid(row = 2, column = 0)
        
        self.width = 0
        self.height = 0
        self.sleep_time = 0
        self.game_grid = []
        self.gui_cells_grid = []
        self.mode = False
        self.playing = False
        self.game_thread = None
        self.grid_threads = []
        
        self.root.protocol("WM_DELETE_WINDOW", self.__on_close)
        self.root.mainloop()
    
    
    # GUI
    
    def __width_focus_in(self, event):
        self.width_entry.delete(0, END)
        
        
    def __width_focus_out(self, event):
        if self.width_entry.get().strip() == "":
            self.width_entry.delete(0, END)
            self.width_entry.insert(0, "Width")
    
        
    def __height_focus_in(self, event):
        self.height_entry.delete(0, END)
        
        
    def __height_focus_out(self, event):
        if self.height_entry.get().strip() == "":
            self.height_entry.delete(0, END)
            self.height_entry.insert(0, "Height")
            
    
    def __sleep_focus_in(self, event):
        self.sleep_entry.delete(0, END)
        
    
    def __sleep_focus_out(self, event):
        if self.sleep_entry.get().strip() == "":
            self.sleep_entry.delete(0, END)
            self.sleep_entry.insert(0, "Sleep Time (seconds)")
            
            
    def __change_mode(self, event):
        self.mode = self.variable.get() == "Multi-Threaded"
            
    
    def __start_game(self):
        self.start_button.focus_set()
        if self.width > 0 and self.height > 0 and self.sleep_time >= 0:
            self.width_entry.configure(state = "disabled")
            self.height_entry.configure(state = "disabled")
            self.sleep_entry.configure(state = "disabled")
            self.update_settings_button.configure(state = "disabled")
            self.mode_menu.configure(state = "disabled")
            self.start_button.configure(state = "disabled")
            
            if self.mode:
                self.playing = True
                self.game_thread = Thread(target = self.__mt_game)
                self.game_thread.start()
                
            elif not self.mode:
                self.playing = True
                self.game_thread = Thread(target = self.__seq_game)
                self.game_thread.start()
        
    
    def __stop_game(self):
        self.stop_button.focus_set()
        self.width_entry.configure(state = "normal")
        self.height_entry.configure(state = "normal")
        self.sleep_entry.configure(state = "normal")
        self.update_settings_button.configure(state = "normal")
        self.mode_menu.configure(state = "normal")
        self.start_button.configure(state = "normal")
        self.playing = False
        
    
    def __update_settings(self):
        self.update_settings_button.focus_set()
        w = self.width_entry.get().strip()
        h = self.height_entry.get().strip()
        s = self.sleep_entry.get().strip()
        
        if w != "" and w.isnumeric() and h != "" and h.isnumeric() and s != "" and int(w) > 0 and int(h) > 0 and float(s) >= 0 and float(s) <= 3:
            w = int(w)
            h = int(h)
            s = float(s)
            
            if w == self.width and h == self.height:
                self.sleep_time = s
                self.status_label.config(text = "Update successful", fg = "green")
                self.status_label.update()
                return
        
            self.width = w
            self.height = h
            self.sleep_time = s
            
            self.game_grid = []
            up_down_row = [-1] * (self.width + 2)
            cells = [0] * (self.width + 2)
            
            self.game_grid.append(up_down_row.copy())
            for _ in range(self.height):
                self.game_grid.append(cells.copy())
            self.game_grid.append(up_down_row.copy())
            
            y = 1
            while y < self.height + 1:
                self.game_grid[y][0] = -1
                self.game_grid[y][len(self.game_grid[0]) - 1] = -1
                y += 1
                
            for button_row in self.gui_cells_grid:
                for button in button_row:
                    button.destroy()
            
            self.gui_cells_grid = []
            
            for y in range(self.height):
                self.gui_cells_grid.append([])
                for x in range(self.width):
                    btn = Button(self.game_grid_frame, text = "", command = lambda row = y, column = x: self.__cell_status_update(column, row))
                    btn.config(height = 0, width = 2, bg = "white")
                    self.gui_cells_grid[y].append(btn)
                    btn.grid(row = y, column = x)
            
            self.game_grid_frame.update()
            self.status_label.config(text = "Update successful", fg = "green")
            self.status_label.update()
            
        else:
            self.status_label.config(text = "Update failed", fg = "red")
            self.status_label.update()
        
        
    def __cell_status_update(self, x, y):
        self.game_grid[y + 1][x + 1] = 1 if self.game_grid[y + 1][x + 1] == 0 else 0
        actual_color = self.gui_cells_grid[y][x].cget("bg")
        
        if actual_color == "white":
            self.gui_cells_grid[y][x].config(bg = "black")
        else:
            self.gui_cells_grid[y][x].config(bg = "white")
            
    
    def __on_close(self):
        self.playing = False
        self.root.destroy()
        if self.mode:
            time.sleep(self.sleep_time)
    
    
    # LOGIC (SEQUENTIAL)
    
    def __seq_check_neighbors(self, x, y):
        y1 = y - 1
        y2 = y + 1
        alive = 0
        
        nx = x - 1
        c = 0
        while c < 3:
            if self.game_grid[y1][nx] == 1:
                alive += 1
            if self.game_grid[y2][nx] == 1:
                alive += 1
            c += 1
            nx += 1
        
        if self.game_grid[y][x + 1] == 1:
            alive += 1
        if self.game_grid[y][x - 1] == 1:
            alive += 1
        return alive
        
        
    def __seq_game(self):
        while self.playing:
            time.sleep(self.sleep_time)
            new_grid = copy.deepcopy(self.game_grid)
            x, y = 1, 1
            
            while x < self.width + 1:
                while y < self.height + 1:
                    alive_neighbors = self.__seq_check_neighbors(x, y)
                    
                    if alive_neighbors < 2 or alive_neighbors > 3:
                        new_grid[y][x] = 0
                        self.gui_cells_grid[y - 1][x - 1].config(bg = "white")
                    
                    elif alive_neighbors == 3:
                        new_grid[y][x] = 1
                        self.gui_cells_grid[y - 1][x - 1].config(bg = "black")
                    
                    y += 1
                x += 1
                y = 1
            
            self.game_grid = new_grid
    
    
    # LOGIC (MULTI-THREADED)
    
    def __mt_thread_iteration(self, barrier, x):
        try:
            barrier.wait()
        
            while self.playing:
                column = [0] * self.height
                y = 1
                    
                while y < self.height + 1:
                    alive_neighbors = self.__seq_check_neighbors(x, y)
                    column[y - 1] = {3 : 1, 2 : self.game_grid[y][x]}.get(alive_neighbors, 0)
                    y += 1
                    
                barrier.wait(timeout = self.sleep_time + 0.1)
                y = 1
                    
                while y < self.height + 1:
                    self.game_grid[y][x] = column[y - 1]
                    
                    if self.game_grid[y][x] == 0:
                        self.gui_cells_grid[y - 1][x - 1].config(bg = "white")
                    else:
                        self.gui_cells_grid[y - 1][x - 1].config(bg = "black")
                        
                    y += 1
        except BrokenBarrierError:
            pass
        
    
    def __mt_game(self):
        barrier = Barrier(self.width + 1)
        x = 1
        
        while x < self.width + 1:
            cell_thread = Thread(target = self.__mt_thread_iteration, args = (barrier, x))
            cell_thread.should_abort_immediately = True
            self.grid_threads.append(cell_thread)
            self.grid_threads[len(self.grid_threads) - 1].start()
            x += 1
        
        while self.playing:
            try:
                barrier.wait(timeout = self.sleep_time + 0.15)
                time.sleep(self.sleep_time)
            except BrokenBarrierError:
                pass
        
        self.grid_threads = []
        
        
    # UTILITY
    
    def __print_grid(self):
        for y in range(len(self.game_grid)):
            for x in range(len(self.game_grid[0])):
                print(f"{self.game_grid[y][x]} ", end = "")
            print()
        print()
        
        
def main():
    GameOfLife()
    
    
if __name__ == "__main__":
    main()
    
