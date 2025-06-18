import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import re
from serial.serialutil import SerialException

class ModernWeighingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧪 Weighing Scale Reader")
        self.root.geometry("480x320")
        self.root.configure(bg="#ecf0f3")
        self.root.resizable(False, False)

        self.create_styles()

        # Title
        title = tk.Label(root, text="Weighing Scale Reader", font=("Segoe UI", 18, "bold"),
                         bg="#ecf0f3", fg="#34495e")
        title.pack(pady=(25, 10))

        # Card Frame
        self.card = tk.Frame(root, bg="white", bd=0, relief="flat", highlightbackground="#dfe6e9", highlightthickness=2)
        self.card.pack(padx=30, pady=10, fill="both", expand=False)

        # COM Port Selector
        port_label = tk.Label(self.card, text="Select COM Port", font=("Segoe UI", 12),
                              bg="white", anchor="w")
        port_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.port_combo = ttk.Combobox(self.card, values=self.get_com_ports(), state="readonly", font=("Segoe UI", 11))
        self.port_combo.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.port_combo.set("Select Port")

        # Read Button
        self.read_button = ttk.Button(self.card, text="Read Weight", command=self.get_weight_from_scale)
        self.read_button.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")

        # Weight Display
        self.weight_label = tk.Label(self.card, text="Weight: 0.0 kg", font=("Segoe UI", 14, "bold"),
                                     bg="white", fg="#27ae60")
        self.weight_label.grid(row=3, column=0, padx=20, pady=(10, 20))

        self.card.columnconfigure(0, weight=1)

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                        font=("Segoe UI", 11),
                        padding=10,
                        background="#2ecc71",
                        foreground="white")
        style.map("TButton",
                  background=[("active", "#27ae60"), ("disabled", "#bdc3c7")])

        style.configure("TCombobox",
                        padding=5)

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def get_weight_from_scale(self):
        port = self.port_combo.get()
        default_weight = 0.0
        ser = None

        if port == "Select Port":
            messagebox.showwarning("Port Selection", "Please select a valid COM port.")
            return

        try:
            ser = serial.Serial(
                port=port,
                baudrate=9600,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=2
            )

            raw_data = ser.readline()

            if raw_data:
                decoded = raw_data.decode('ascii', errors='ignore').strip()

                if decoded.startswith('.') and decoded[1:].replace('.', '').isdigit():
                    decoded = '0' + decoded

                matches = re.findall(r"[-+]?\d*\.\d+|\d+", decoded)

                if matches:
                    weight = float(matches[-1])
                    self.weight_label.config(text=f"Weight: {weight} kg")
                    return weight
                else:
                    messagebox.showerror("Error", f"No valid numeric data found in: {decoded}")
            else:
                messagebox.showerror("Error", f"No data received from {port}")

        except SerialException as e:
            self.weight_label.config(text="Weight: 0.0 kg", fg="red")
            messagebox.showerror("Error", f"Could not open or communicate with {port}: {e}")
        except UnicodeDecodeError:
            messagebox.showerror("Error", f"Received non-ASCII data on {port}.")
        except ValueError as e:
            messagebox.showerror("Error", f"ValueError while parsing weight: {e}")
        except OverflowError as e:
            messagebox.showerror("Error", f"OverflowError: {e}")
        finally:
            if ser and ser.is_open:
                ser.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernWeighingApp(root)
    root.mainloop()
