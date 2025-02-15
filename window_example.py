import tkinter as tk 

#Auteurs : Simon RIGOLLIER, Michelle SONG, Aurélien CHAMBOLLE-SOLAZ.

def launch_sequence_window():
    sequence_window = tk.Tk()
    sequence_window.title("Question du débat")
    sequence_window.geometry("500x400")

    arg1_button = tk.Button(sequence_window, 
                   text="Argument 1", 
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   width=40,
                   height=10)
    arg2_button = tk.Button(sequence_window, 
                   text="Argument 2",
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   width=40,
                   height=10)
    unable_button = tk.Button(sequence_window, 
                   text="Je ne peux pas décider",
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   width=40,
                   height=3)

    arg1_button.pack()
    arg2_button.pack()
    unable_button.pack()

    sequence_window.mainloop()

def main() :
    main_window = tk.Tk()
    main_window.title("Comparaison d'arguments")
    main_window.geometry("500x400")



    start_sequence_button = tk.Button(main_window, 
                   text="Commencer la séquence", 
                   command=launch_sequence_window,
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   width=25,
                   height=5)
    load_debate_button = tk.Button(main_window, 
                   text="Charger un débat",
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   width=25,
                   height=5)
    
    results_button = tk.Button(main_window, 
                   text="Voir les résultats",
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   width=25,
                   height=5)

    load_debate_button.pack()
    start_sequence_button.pack()
    results_button.pack()


    main_window.mainloop()



if __name__ == '__main__':
    main()